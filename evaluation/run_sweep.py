"""Sweep greedy / fixed-K / adaptive settings from one shared candidate pool per question.

Phase `collect` runs the model once per question: one greedy candidate plus a pool of N
sampled candidates, each validated, executed and checked against gold. Phase `simulate`
replays every configuration on that pool with the project's own grouping, ranking and
stopping rules, so all methods see identical samples and the sweep costs one model pass.
Bootstrap permutations of the pool give confidence intervals for the sampled methods.
Correction is disabled to isolate the effect of sampling and stopping.
"""
import argparse
from copy import deepcopy
import csv
import json
import math
import os
from pathlib import Path
import random
import statistics
import time

from core.adaptive_sampler import decide
from core.candidate_ranker import rank_candidates
from core.config import ROOT, load_config
from core.model_backend import create_backend
from core.omnisql_prompt import SYSTEM_PROMPT, build_paper_prompt
from core.pipeline import Pipeline
from core.prompt_builder import build_prompt
from core.result_grouper import group_candidates
from core.schema_inspector import SchemaInspector
from core.sql_executor import SQLExecutor
from core.sql_generator import generate_candidates
from core.types import Candidate, ExecutionResult, ValidationResult
from databases.create_student_db import DEFAULT_DB, create_database
from evaluation.metrics import execution_match

FIXED_K = [1, 2, 4, 8, 16]
SCHEDULES = {"2-2-4-8": [2, 2, 4, 8], "4-4-8": [4, 4, 8], "4-4-8-16": [4, 4, 8, 16]}
THRESHOLDS = [0.5, 0.6, 0.75, 0.9, 1.0]
MIN_VALID = [2, 4]
# Spider/ViText2SQL hardness, then BIRD difficulty.
LEVELS = ("easy", "medium", "hard", "extra", "simple", "moderate", "challenging")
# CSC-SQL/SLM-SQL inference: vLLM SamplingParams(temperature=0.8, max_tokens=1024) leaves top_p=1,
# top_k off and repetition_penalty=1, overriding the checkpoint's generation_config defaults.
PAPER_SAMPLING = {"temperature": 0.8, "top_p": 1.0, "top_k": 0, "repetition_penalty": 1.0,
                  "max_new_tokens": 1024, "max_input_tokens": 7000, "system_prompt": SYSTEM_PROMPT}
# CSC-SQL's evaluation.py: 30 s per query and no step budget. The project's 2M-step budget is a UI guard
# that rejects correct queries over large Spider tables (e.g. wta_1.rankings) in a fraction of a second.
# Full rows are kept so Spider-style column-permutation matching never sees a truncated preview.
PAPER_EXECUTION = {"timeout_seconds": 30, "max_steps": 10 ** 12, "max_rows": 50000}


def _paper_mode(args, config):
    if args.prompt == "paper":
        config["generation"].update(PAPER_SAMPLING)
        config["execution"].update(PAPER_EXECUTION)


def _read_pool(path: Path, repair: bool = False, metric: str = "strict") -> list[dict]:
    """Complete rows only. A line cut off by a power loss is dropped (and removed when repair=True)."""
    rows, broken = [], 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            broken += 1
    if broken and repair:
        path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
        print(f"Removed {broken} incomplete line(s) from {path.name}; those questions will be redone.")
    if metric != "strict":
        for row in rows:
            for record in [row["greedy"], *row["pool"]]:
                if record:
                    # Candidates that never executed carry no per-metric label and are wrong under all of them.
                    record["correct"] = record.get(f"correct_{metric}", False)
    return rows


def _record(candidate, gold, gold_sql) -> dict:
    execution, validation = candidate.execution, candidate.validation
    return {
        "sql": candidate.sql, "error": candidate.error,
        "success": bool(execution and execution.success),
        "result": execution.normalized_result if execution and execution.success else None,
        "schema_score": validation.schema_score if validation else 0.0,
        "warnings": len(validation.warnings) if validation else 0,
        "error_type": (execution.error_type if execution and execution.error_type else
                       validation.error_type if validation else "generation"),
        "correct": execution_match(execution, gold, gold_sql),
        "correct_set": execution_match(execution, gold, gold_sql, mode="set"),
        "correct_spider": execution_match(execution, gold, gold_sql, mode="spider"),
        "generation_ms": candidate.generation_ms,
    }


def _targets(args) -> list[int]:
    """Cumulative pool sizes to check consensus at: '4-4-8' -> [4, 8, 16]; no schedule -> [pool]."""
    if not args.schedule:
        return [args.pool]
    sizes = [int(n) for n in args.schedule.split("-")]
    return [min(sum(sizes[: i + 1]), args.pool) for i in range(len(sizes))]


def collect(args, config):
    items = json.loads(args.dataset.read_text(encoding="utf-8"))[: args.limit]
    if args.db.resolve() == DEFAULT_DB.resolve():
        create_database()
    out = args.output / "pool.jsonl"
    done = {row["id"] for row in _read_pool(out, repair=True)} if out.exists() else set()
    config["correction"]["enabled"] = False
    _paper_mode(args, config)
    stopping = dict(config["sampling"], max_candidates=args.pool)
    if args.threshold is not None:
        stopping["confidence_threshold"] = args.threshold
    backend = create_backend(config)
    pipeline = Pipeline(config, backend)
    executor = SQLExecutor(config["execution"])
    schema_inspector = SchemaInspector(**config["schema"])
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "config.json").write_text(json.dumps(
        dict(config, sweep={k: str(v) for k, v in vars(args).items()}), indent=2), encoding="utf-8")
    with out.open("a", encoding="utf-8") as handle:
        for index, item in enumerate(items, 1):
            if item["id"] in done:
                continue
            database = (args.dataset.parent / item["db_path"]).resolve() if item.get("db_path") else args.db
            gold = executor.execute(database, item["gold_sql"])
            if args.prompt == "paper":
                prompt = build_paper_prompt(item["question"], database, item["db_id"],
                                            args.dataset.parent / item["tables_path"], item.get("evidence", ""))
            else:
                prompt = build_prompt(item["question"], schema_inspector.inspect(database), item.get("evidence", ""))
            greedy_params = dict(config["generation"], temperature=0.0)
            sample_params = dict(config["generation"], batch_size=args.batch_size)
            backend.start_request(config["seed"])
            greedy, greedy_ms = [], 0.0
            if not args.skip_greedy:
                start = time.perf_counter()
                greedy = generate_candidates(backend, prompt, 1, greedy_params)
                greedy_ms = (time.perf_counter() - start) * 1000
            pool, batch_ms, stop = [], [], "pool"
            for target in _targets(args):
                while len(pool) < target:
                    start = time.perf_counter()
                    new = generate_candidates(backend, prompt, min(args.batch_size, target - len(pool)),
                                              sample_params, len(pool))
                    batch_ms.append((time.perf_counter() - start) * 1000)
                    if not new:
                        break
                    for candidate in new:
                        pipeline._check(candidate, database)
                    pool += new
                if args.schedule and len(pool) < args.pool:
                    # Same rule as the live adaptive pipeline; elapsed time is ignored so reruns match.
                    decision = decide(group_candidates(pool), len(pool), 0, stopping)
                    if decision.should_stop:
                        stop = decision.reason
                        break
            for candidate in greedy:
                pipeline._check(candidate, database)
            row = {"id": item["id"], "difficulty": item.get("difficulty"), "question": item["question"],
                   "evidence": item.get("evidence", ""), "db": str(database),
                   "gold_sql": item["gold_sql"], "greedy_ms": greedy_ms, "batch_ms": batch_ms,
                   "batch_size": args.batch_size, "stop": stop,
                   "greedy": _record(greedy[0], gold, item["gold_sql"]) if greedy else None,
                   "pool": [_record(c, gold, item["gold_sql"]) for c in pool]}
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()
            # A finished question survives a hard power-off; at most the current one is lost.
            os.fsync(handle.fileno())
            print(f"[{index}/{len(items)}] {item['id']} greedy={row['greedy'] and row['greedy']['correct']} "
                  f"pool_correct={sum(r['correct'] for r in row['pool'])}/{len(pool)} stop={stop} "
                  f"{(greedy_ms + sum(batch_ms)) / 1000:.0f}s", flush=True)
            from evaluation.progress import report  # progress imports this module
            (args.output / "progress.txt").write_text(report(args.output, len(items)) + "\n", encoding="utf-8")


def rescore(args, config):
    """Re-execute stored SQL and gold under the current execution limits; no model calls."""
    _paper_mode(args, config)
    path = args.output / "pool.jsonl"
    rows = _read_pool(path, repair=True)
    executor = SQLExecutor(config["execution"])
    changed = 0
    for row in rows:
        database = Path(row["db"]) if row.get("db") else args.db
        gold = executor.execute(database, row["gold_sql"])
        for record in [row["greedy"], *row["pool"]]:
            # Only candidates that reached execution: generation, syntax, schema and safety failures stand.
            if not record or not (record["success"] or record["error_type"] in {"timeout", "result_limit", "execution"}):
                continue
            execution = executor.execute(database, record["sql"])
            before = (record["success"], record["correct"], record.get("correct_set"), record.get("correct_spider"))
            record.update(success=execution.success,
                          result=execution.normalized_result if execution.success else None,
                          error_type=execution.error_type,
                          correct=execution_match(execution, gold, row["gold_sql"]),
                          correct_set=execution_match(execution, gold, row["gold_sql"], mode="set"),
                          correct_spider=execution_match(execution, gold, row["gold_sql"], mode="spider"))
            changed += before != (record["success"], record["correct"], record["correct_set"], record["correct_spider"])
    temporary = path.with_suffix(".rescore.tmp")
    temporary.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    temporary.replace(path)
    print(f"Rescored {len(rows)} questions; {changed} candidate outcomes changed.")


def _candidates(records):
    return [Candidate(i, sql=r["sql"] or "", error=r["error"],
                      validation=ValidationResult(is_safe=True, is_valid=r["success"],
                                                  warnings=[""] * r["warnings"],
                                                  schema_score=r["schema_score"]),
                      execution=ExecutionResult(success=r["success"], normalized_result=r["result"]))
            for i, r in enumerate(records)]


def _select(records, weights):
    candidates = _candidates(records)
    group_candidates(candidates)
    chosen = rank_candidates(candidates, weights)
    return records[chosen.id]["correct"] if chosen else False


def _batch_cost(row, count):
    """Sampled-generation latency estimate: one measured batch time per started batch."""
    per_batch = statistics.mean(row["batch_ms"]) if row["batch_ms"] else 0.0
    return math.ceil(count / row["batch_size"]) * per_batch


def _adaptive(row, order, schedule, sample, weights):
    records = [row["pool"][i] for i in order]
    used, cost, reason = 0, 0.0, "rounds_exhausted"
    for requested in schedule:
        count = min(requested, sample["max_candidates"] - used, len(records) - used)
        if count <= 0:
            reason = "max_candidates"
            break
        used += count
        cost += _batch_cost(row, count)
        candidates = _candidates(records[:used])
        decision = decide(group_candidates(candidates), used, 0, sample)
        if decision.should_stop:
            reason = decision.reason
            break
    return _select(records[:used], weights), used, cost, reason


def simulate(args, config):
    rows = _read_pool(args.output / "pool.jsonl", metric=args.metric)
    weights = config["ranking"]
    rng = random.Random(config["seed"])
    orders = [list(range(len(row["pool"]))) for row in rows]
    permutations = [orders] + [[rng.sample(o, len(o)) for o in orders] for _ in range(args.bootstrap)]
    settings = [("greedy", "greedy", {})] if all(row["greedy"] for row in rows) else []
    settings += [(f"fixed_k{k}", "fixed_sc", {"k": k}) for k in FIXED_K]
    settings += [(f"adaptive_{name}_t{t}_m{m}", "adaptive_sc", {"schedule": s, "threshold": t, "min_valid": m})
                 for name, s in SCHEDULES.items() for t in THRESHOLDS for m in MIN_VALID]
    settings += [("oracle_pass@16", "oracle", {})]
    summaries, per_question = [], []
    for label, mode, extra in settings:
        sample = dict(config["sampling"], max_candidates=len(rows[0]["pool"]))
        if mode == "adaptive_sc":
            sample.update(confidence_threshold=extra["threshold"], min_valid_candidates=extra["min_valid"])
        runs = []
        for perm in (permutations[:1] if mode in {"greedy", "oracle"} else permutations):
            outcomes = []
            for row, order in zip(rows, perm):
                if mode == "greedy":
                    outcomes.append((row["greedy"]["correct"], 1, row["greedy_ms"], "greedy", row["difficulty"]))
                elif mode == "oracle":
                    outcomes.append((any(r["correct"] for r in row["pool"]), len(row["pool"]),
                                     _batch_cost(row, len(row["pool"])), "oracle", row["difficulty"]))
                elif mode == "fixed_sc":
                    records = [row["pool"][i] for i in order[: extra["k"]]]
                    outcomes.append((_select(records, weights), len(records),
                                     _batch_cost(row, len(records)), "fixed", row["difficulty"]))
                else:
                    correct, used, cost, reason = _adaptive(row, order, extra["schedule"], sample, weights)
                    outcomes.append((correct, used, cost, reason, row["difficulty"]))
            runs.append(outcomes)
        first = runs[0]
        accuracies = sorted(sum(o[0] for o in run) / len(run) for run in runs)
        candidates = [statistics.mean(o[1] for o in run) for run in runs]
        latencies = [statistics.mean(o[2] for o in run) for run in runs]
        summary = {
            "method": label, "mode": mode,
            "schedule": "-".join(map(str, extra.get("schedule", []))) or extra.get("k", ""),
            "threshold": extra.get("threshold", ""), "min_valid": extra.get("min_valid", ""),
            "questions": len(rows),
            "execution_accuracy": statistics.mean(accuracies),
            "ci95_low": accuracies[int(0.025 * (len(accuracies) - 1))],
            "ci95_high": accuracies[int(0.975 * (len(accuracies) - 1))],
            "average_candidates": statistics.mean(candidates),
            "est_latency_s": statistics.mean(latencies) / 1000,
            "early_stop_rate": statistics.mean(
                sum(o[3] == "consensus" for o in run) / len(run) for run in runs),
        }
        for level in LEVELS:
            subset = [o for run in runs for o in run if o[4] == level]
            summary[f"acc_{level}"] = sum(o[0] for o in subset) / len(subset) if subset else ""
        summaries.append(summary)
        per_question.append({"method": label, **{row["id"]: o[0] for row, o in zip(rows, first)}})
    with (args.output / "sweep.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summaries[0]))
        writer.writeheader()
        writer.writerows(summaries)
    with (args.output / "per_question.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(per_question[0]))
        writer.writeheader()
        writer.writerows(per_question)
    pool_stats = {
        "questions": len(rows),
        "pool_valid_rate": statistics.mean(sum(r["success"] for r in row["pool"]) / len(row["pool"]) for row in rows),
        "pool_correct_rate": statistics.mean(sum(r["correct"] for r in row["pool"]) / len(row["pool"]) for row in rows),
        "avg_distinct_results": statistics.mean(len({r["result"] for r in row["pool"] if r["success"]}) for row in rows),
        "greedy_avg_s": statistics.mean(row["greedy_ms"] for row in rows) / 1000 if settings[0][1] == "greedy" else None,
        "batch_avg_s": statistics.mean(statistics.mean(row["batch_ms"]) for row in rows) / 1000,
    }
    (args.output / "pool_stats.json").write_text(json.dumps(pool_stats, indent=2), encoding="utf-8")
    print(json.dumps(pool_stats, indent=2))
    print(f"Saved: {args.output / 'sweep.csv'}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=["collect", "rescore", "simulate", "all"])
    parser.add_argument("--dataset", type=Path, default=ROOT / "data/evaluation_questions.json")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--pool", type=int, default=16)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--bootstrap", type=int, default=200)
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "sweep")
    parser.add_argument("--prompt", choices=["project", "paper"], default="project",
                        help="paper: SLM-SQL Appendix E.1 prompt + CSC-SQL schema format and sampling")
    parser.add_argument("--skip-greedy", action="store_true", help="Sample the pool only")
    parser.add_argument("--schedule", help="collect: stop sampling at consensus after these rounds, e.g. 4-4-8 "
                                           "(sampling.* stopping rules; the pool then holds 4, 8 or 16 candidates)")
    parser.add_argument("--threshold", type=float, help="collect --schedule: confidence threshold (default config)")
    parser.add_argument("--metric", choices=["strict", "set", "spider"], default="strict",
                        help="simulate: strict multiset EX, CSC-SQL set EX, or Spider test-suite style EX")
    args = parser.parse_args()
    config = deepcopy(load_config(args.config))
    if args.phase in {"collect", "all"}:
        collect(args, config)
    if args.phase == "rescore":
        rescore(args, config)
    if args.phase in {"simulate", "all"}:
        simulate(args, config)


if __name__ == "__main__":
    main()
