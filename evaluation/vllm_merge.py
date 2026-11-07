"""CSC-SQL merge revision with the paper's dedicated merge model, on the pairs a pool disagrees on.

evaluation.judge asks the SQL generator itself, with a project-written prompt. This module uses
cycloneboy/CscSQL-Merge-Qwen2.5-Coder-1.5B-Instruct and the prompt of CSC-SQL's
build_merge_generate_prompt: two draft queries with their execution results, schema cut to the
tables they use, 8 draws at temperature 0.8.

    # Local: the pool and CAV flags stay here; only the small pairs file goes to Kaggle.
    python -m evaluation.vllm_merge prepare results/bird-dev-vllm-64 \\
        --flags results/selection-bird-dev-vllm-64/candidate_flags.json \\
        --output data/benchmarks/bird_dev_merge_pairs.jsonl
    # GPU (one process per GPU with --shard i/n):
    python -m evaluation.vllm_merge run --dataset data/benchmarks/bird_dev.json \\
        --pairs data/benchmarks/bird_dev_merge_pairs.jsonl --output results/bird-dev-merge

Each question gets the pair the plain vote sees (source "vote", as the paper) and the pair left
after CAV-3 (source "cav"); identical pairs are sampled once. evaluation.merge_study replays the
draws without further model calls.
"""
import argparse
from collections import Counter
from copy import deepcopy
import json
import os
from pathlib import Path
import time

from core.candidate_ranker import rank_candidates
from core.config import ROOT, load_config
from core.consistency_checks import CHECKS
from core.omnisql_prompt import build_paper_prompt
from core.pipeline import Pipeline
from core.result_grouper import group_candidates
from core.sql_executor import SQLExecutor
from evaluation.judge import mentions
from evaluation.run_sweep import PAPER_EXECUTION, PAPER_SAMPLING, _candidates, _read_pool, _record
from evaluation.vllm_collect import _candidates as _draws, _portable

MODEL = "cycloneboy/CscSQL-Merge-Qwen2.5-Coder-1.5B-Instruct"
TASK = ("You are a data science expert. Below, you are provided with a database schema and a natural "
        "language question. Your task is to understand the schema and generate a valid SQL query to answer "
        "the question.")
MERGE_TASK = ("You are a data science expert. Below, you are provided with a database schema, a natural "
              "language question, some draft SQL and its corresponding execution result. Your task is to "
              "understand the schema and generate a valid SQL query to answer the question.")
SCHEMA_START = "Database Schema:"
SCHEMA_END = "This schema describes the database's structure,"
TABLE = "CREATE TABLE "


def result_text(rows: list, row_count: int) -> str:
    """CSC-SQL's normal_execute_result: at most 20 rows and 1000 characters."""
    rows = [tuple(row) for row in rows]
    if row_count > 20:
        head = str(rows[:20])
        head = head[:1000] + "...]" if len(head) > 1000 else head
        text = f"The execution results of the first twenty columns are: {head}"
    else:
        text = str(rows)
    return text[:1000] + "..." if len(text) > 1000 else text


def keep_tables(prompt: str, sqls: list) -> str:
    """Drop CREATE TABLE blocks neither query mentions (the prompt is unchanged when none match)."""
    start, end = prompt.find(SCHEMA_START), prompt.find(SCHEMA_END)
    if start < 0 or end < 0:
        return prompt
    start += len(SCHEMA_START)
    head, *blocks = prompt[start:end].split(TABLE)
    text = " ".join(sqls).lower()
    used = [b for b in blocks if mentions(b.split("(")[0].strip().strip('`"').lower(), text)]
    return prompt[:start] + TABLE.join([head, *used]) + prompt[end:] if used else prompt


def merge_prompt(prompt: str, pair: dict) -> str:
    drafts = "\n".join(f"{i}. {sql[:500]}\n【Execution result】\n{result}\n" for i, (sql, result) in enumerate(
        ((pair["sql1"], pair["res1"]), (pair["sql2"], pair["res2"])), 1))
    prompt = prompt.replace(TASK, MERGE_TASK).replace(
        "Instructions:", f"Here are some corresponding draft SQL and execute result: \n{drafts}\n\nInstructions:", 1)
    return keep_tables(prompt, [pair["sql1"], pair["sql2"]])


def top_pair(records: list, weights: dict):
    """(selected record, largest other cluster's record, their votes), or None without a rival."""
    candidates = _candidates(records)
    group_candidates(candidates)
    chosen = rank_candidates(candidates, weights)
    if not chosen:
        return None
    winner = records[chosen.id]
    sizes = Counter(r["result"] for r in records if r["success"])
    rivals = [h for h in sizes if h != winner["result"]]
    if not rivals:
        return None
    rival = max(rivals, key=sizes.get)
    return winner, next(r for r in records if r["result"] == rival), [sizes[winner["result"]], sizes[rival]]


def apply_flags(rows: list, flags: dict) -> None:
    for row in rows:
        name = Path(row["db"]).name
        for record in row["pool"]:
            if record["success"]:
                record.update(flags[f"{name}|{record['sql']}"])


def clean(records: list) -> list:
    # Imported here: selection_study imports evaluation.judge, as this module does.
    from evaluation.selection_study import _clean
    return _clean(records, CHECKS)


def prepare(args):
    config = deepcopy(load_config(args.config))
    executor = SQLExecutor(dict(config["execution"], **dict(PAPER_EXECUTION, max_rows=20)))
    rows = _read_pool(args.pool_dir / "pool.jsonl", metric="set")
    apply_flags(rows, json.loads(args.flags.read_text(encoding="utf-8")))
    previews = {}

    def preview(row, sql):
        key = (row["db"], sql)
        if key not in previews:
            result = executor.execute(ROOT / row["db"], sql)
            previews[key] = result_text(result.rows, result.row_count)
        return previews[key]

    count = 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for row in rows:
            pairs = {}
            for source, records in (("vote", row["pool"]), ("cav", clean(row["pool"]))):
                found = top_pair(records, config["ranking"]) if records else None
                if found:
                    winner, rival, votes = found
                    pair = pairs.setdefault((winner["result"], rival["result"]), {
                        "key": f"{row['id']}|{winner['result']}|{rival['result']}", "id": row["id"],
                        "winner": winner["result"], "rival": rival["result"], "sources": {},
                        "sql1": winner["sql"], "res1": preview(row, winner["sql"]),
                        "sql2": rival["sql"], "res2": preview(row, rival["sql"])})
                    pair["sources"][source] = votes
            for pair in pairs.values():
                handle.write(json.dumps(pair, ensure_ascii=False) + "\n")
                count += 1
    print(f"{count} pairs for {len(rows)} questions -> {args.output}")


def run(args):
    from vllm import LLM, SamplingParams

    config = deepcopy(load_config(args.config))
    config["generation"].update(PAPER_SAMPLING)
    config["execution"].update(PAPER_EXECUTION)
    config["correction"]["enabled"] = False
    generation = config["generation"]
    items = {i["id"]: i for i in json.loads(args.dataset.read_text(encoding="utf-8"))}
    pairs = [json.loads(line) for line in args.pairs.read_text(encoding="utf-8").splitlines() if line.strip()]
    pairs = pairs[: args.limit]
    out = args.output / "merge.jsonl"
    done = {r["key"] for r in map(json.loads, out.read_text(encoding="utf-8").splitlines())} if out.exists() else set()
    shard, shards = map(int, args.shard.split("/"))
    todo = [(i, p) for i, p in enumerate(pairs) if p["key"] not in done and i % shards == shard]
    args.output.mkdir(parents=True, exist_ok=True)
    print(f"{len(done)} done, {len(todo)} to sample", flush=True)
    if not todo:
        return

    llm = LLM(model=args.model, dtype=args.dtype, seed=config["seed"], max_model_len=args.max_model_len,
              gpu_memory_utilization=args.gpu_memory, tensor_parallel_size=1, enable_prefix_caching=True)
    tokenizer = llm.get_tokenizer()
    pipeline = Pipeline(config, backend=object())
    executor = SQLExecutor(config["execution"])

    for start in range(0, len(todo), args.chunk):
        chunk = todo[start: start + args.chunk]
        prompts, keep, skipped = [], [], []
        for index, pair in chunk:
            item = items[pair["id"]]
            database = Path(os.path.abspath(args.dataset.parent / _portable(item["db_path"])))
            tables = args.dataset.parent / _portable(item["tables_path"])
            prompt = merge_prompt(build_paper_prompt(item["question"], database, item["db_id"], tables,
                                                     item.get("evidence", "")), pair)
            text = tokenizer.apply_chat_template(
                [{"role": "system", "content": generation["system_prompt"]}, {"role": "user", "content": prompt}],
                tokenize=False, add_generation_prompt=True)
            if len(tokenizer(text, add_special_tokens=False)["input_ids"]) > generation["max_input_tokens"]:
                skipped.append((pair, item, database))
                continue
            prompts.append(text)
            keep.append((index, pair, item, database))
        params = [SamplingParams(n=args.samples, temperature=generation["temperature"], top_p=generation["top_p"],
                                 max_tokens=generation["max_new_tokens"], seed=config["seed"] + index)
                  for index, *_ in keep]
        began = time.perf_counter()
        outputs = llm.generate(prompts, params, use_tqdm=False) if prompts else []
        seconds = time.perf_counter() - began
        results = [(pair, item, database, _draws(o, seconds * 1000 / max(1, len(prompts)) / args.samples))
                   for (_, pair, item, database), o in zip(keep, outputs)]
        results += [(pair, item, database, []) for pair, item, database in skipped]
        with out.open("a", encoding="utf-8") as handle:
            for pair, item, database, draws in results:
                gold = executor.execute(database, item["gold_sql"])
                for draw in draws:
                    pipeline._check(draw, database)
                handle.write(json.dumps({
                    "key": pair["key"], "id": pair["id"], "winner": pair["winner"], "rival": pair["rival"],
                    "sources": pair["sources"], "draws": [_record(d, gold, item["gold_sql"]) for d in draws],
                }, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        print(f"[{len(done) + start + len(chunk)}/{len(done) + len(todo)}] chunk of {len(chunk)} in {seconds:.0f}s",
              flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    pairs = commands.add_parser("prepare")
    pairs.add_argument("pool_dir", type=Path)
    pairs.add_argument("--flags", type=Path, required=True, help="candidate_flags.json of selection_study")
    pairs.add_argument("--output", type=Path, required=True)
    pairs.add_argument("--config", type=Path)
    pairs.set_defaults(handler=prepare)
    sample = commands.add_parser("run")
    sample.add_argument("--dataset", type=Path, required=True)
    sample.add_argument("--pairs", type=Path, required=True)
    sample.add_argument("--output", type=Path, required=True)
    sample.add_argument("--config", type=Path)
    sample.add_argument("--model", default=MODEL)
    sample.add_argument("--samples", type=int, default=8, help="CSC-SQL's n_sql_merge")
    sample.add_argument("--limit", type=int)
    sample.add_argument("--chunk", type=int, default=32)
    sample.add_argument("--dtype", default="half")
    sample.add_argument("--max-model-len", type=int, default=8192)
    sample.add_argument("--gpu-memory", type=float, default=0.90)
    sample.add_argument("--shard", default="0/1", help="i/n: only pairs whose index %% n == i (one GPU each)")
    sample.set_defaults(handler=run)
    args = parser.parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
