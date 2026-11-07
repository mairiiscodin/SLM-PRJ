"""Second opinion on contested questions: settle the vote between the largest result clusters.

For every question, each pair among the largest clusters of the pool (at least --min-size
members) gets a verdict, cached in judgments.jsonl (resumable) and replayed by
selection_study --judge for every budget and permutation without further model calls.

--mode merge (default), as CSC-SQL's merge revision: the paper prompt is extended with the two
queries and their result previews, the model writes the SQL again (--samples draws), and each
draw votes for the cluster whose result it reproduces. This uses what the model is trained for.
--cav judges the top pairs left after CAV-3 drops flagged candidates (use with --min-size 1), the
pairs selection_study's "CAV + judge" asks about; pairs already in judgments-<mode>.jsonl are reused.
--mode ab asks "A or B?" and reads the next-token probabilities in both orders. SLM-SQL-1.5B
gives ~0.5 for every pair there (it was trained to write SQL, not to compare it); the mode stays
for judge models that can.
"""
import argparse
from copy import deepcopy
from itertools import combinations
import json
import os
from pathlib import Path
import re
import sqlite3
import time

from core.config import load_config
from core.model_backend import create_backend
from core.omnisql_prompt import TEMPLATE, build_paper_prompt
from core.pipeline import Pipeline
from core.sql_executor import SQLExecutor
from core.sql_generator import generate_candidates
from evaluation.run_sweep import PAPER_SAMPLING, _read_pool

AB_PROMPT = """Database schema (tables used by the queries):
{schema}

{evidence}Question:
{question}

Two SQLite queries were written for this question. They return different results.

Query A:
{sql_a}
Result A: {result_a}

Query B:
{sql_b}
Result B: {result_b}

Which query answers the question correctly? Check the selected columns, aggregation, grouping, filters, ordering, DISTINCT and the returned rows against what the question asks. Answer with one letter in <answer> </answer> tags: A or B."""
# The answer prefix skips the model's <think> block: the next token is the verdict.
AB_PREFILL = "<think>\nI compare both queries and their results with the question.\n</think>\n<answer>\n"
MERGE_NOTE = """

Candidate SQL queries written for this question disagree; at most one of them is correct, and both may be wrong:
{candidates}
Compare them with the question and the schema, then write the correct SQL query."""


def pair_key(a: str, b: str) -> str:
    return "|".join(sorted((a, b)))


def clusters(pool: list, min_size: int) -> list:
    """Executed candidates grouped by result, largest first; first member's SQL represents the group."""
    groups = {}
    for record in pool:
        if record["success"]:
            groups.setdefault(record["result"], []).append(record)
    ranked = sorted(groups.values(), key=len, reverse=True)
    return [g for g in ranked if len(g) >= min_size]


def _create_statements(db_path: Path) -> list:
    connection = sqlite3.connect(Path(db_path).resolve().as_uri() + "?mode=ro", uri=True)
    try:
        return connection.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()
    finally:
        connection.close()


def mentions(table: str, text: str) -> bool:
    """Lower-case table name appears in lower-case SQL, bare or quoted."""
    return bool(re.search(rf"(?<![\w`\"]){re.escape(table)}(?![\w`\"])", text)) \
        or f"`{table}`" in text or f'"{table}"' in text


def schema_for(db_path: Path, sqls: list) -> str:
    """CREATE statements of the tables either query mentions (all tables when none match)."""
    tables = _create_statements(db_path)
    text = " ".join(sqls).lower()
    used = [sql for name, sql in tables if mentions(name.lower(), text)]
    return "\n".join(s.strip() for s in (used or [sql for _, sql in tables]) if s)


def preview(execution, rows: int = 5, width: int = 40) -> str:
    def cell(value):
        text = str(value)
        return text if len(text) <= width else text[:width] + "…"
    shown = [", ".join(cell(v) for v in row) for row in execution.rows[:rows]]
    body = "; ".join(f"({r})" for r in shown) or "no rows"
    return f"{execution.row_count} row(s), columns ({', '.join(execution.columns)}): {body}" + (
        " …" if execution.row_count > rows else "")


def base_prompt(row: dict, item: dict, evidence: str) -> str:
    """The generation prompt the pool was sampled with (paper format when tables.json is known)."""
    database = Path(row["db"])
    if item.get("tables_path"):
        return build_paper_prompt(row["question"], database, item["db_id"], Path(item["tables_path"]), evidence)
    question = f"{evidence}\n{row['question']}" if evidence.strip() else row["question"]
    schema = "\n\n".join(sql.strip() for _, sql in _create_statements(database) if sql)
    return TEMPLATE.format(db_details=schema, question=question)


class Judge:
    def __init__(self, config: dict):
        self.config = config
        self.backend = create_backend(config)
        self.pipeline = Pipeline(config, self.backend)
        self.torch = self.backend.torch
        tokenizer = self.backend.tokenizer
        # Leading-space variants matter for BPE tokenizers; the best-scoring spelling counts.
        self.ids = {letter: sorted({tokenizer.encode(v, add_special_tokens=False)[0] for v in (letter, " " + letter)})
                    for letter in "AB"}

    def prob_a(self, prompt: str) -> float:
        tokenizer, model = self.backend.tokenizer, self.backend.model
        text = tokenizer.apply_chat_template([{"role": "user", "content": prompt}], tokenize=False,
                                             add_generation_prompt=True) + AB_PREFILL
        inputs = tokenizer(text, return_tensors="pt", add_special_tokens=False).to(model.device)
        with self.torch.inference_mode():
            # Only the last position's logits: a full vocab x length tensor does not fit in 4 GB.
            logits = model(**inputs, logits_to_keep=1).logits[0, -1].float()
        a = self.torch.logsumexp(logits[self.ids["A"]], 0)
        b = self.torch.logsumexp(logits[self.ids["B"]], 0)
        return self.torch.sigmoid(a - b).item()

    def revise(self, prompt: str, database: Path, samples: int, batch_size: int) -> list:
        """Result hashes of the re-written SQL draws (None for draws that fail)."""
        params = dict(self.config["generation"], batch_size=batch_size)
        self.backend.start_request(self.config["seed"])
        out = []
        for candidate in generate_candidates(self.backend, prompt, samples, params):
            self.pipeline._check(candidate, database)
            execution = candidate.execution
            out.append(execution.normalized_result if execution and execution.success else None)
        return out


def _ab_pairs(judge, row, shown, fill):
    pairs = {}
    for x, y in combinations(shown, 2):
        (sql_x, res_x), (sql_y, res_y) = shown[x], shown[y]
        schema = schema_for(Path(row["db"]), [sql_x, sql_y])
        forward = judge.prob_a(AB_PROMPT.format(sql_a=sql_x, result_a=res_x, sql_b=sql_y, result_b=res_y,
                                                schema=schema, **fill))
        backward = judge.prob_a(AB_PROMPT.format(sql_a=sql_y, result_a=res_y, sql_b=sql_x, result_b=res_x,
                                                 schema=schema, **fill))
        # Probability that x's result is the right one, averaged over both positions.
        p_x = (forward + 1 - backward) / 2
        key = pair_key(x, y)
        pairs[key] = p_x if key.split("|")[0] == x else 1 - p_x
    return pairs


def _merge_pairs(judge, row, item, shown, hint, args, known=()):
    pairs, draws = {}, {}
    for x, y in combinations(shown, 2):
        if pair_key(x, y) in known:
            continue
        listing = "".join(f"\nQuery {i}:\n{sql}\nResult {i}: {result}\n"
                          for i, (sql, result) in enumerate((shown[x], shown[y]), 1))
        prompt = base_prompt(row, item, hint)
        marker = "\n\nInstructions:"
        prompt = prompt.replace(marker, MERGE_NOTE.format(candidates=listing) + marker, 1)
        results = judge.revise(prompt, Path(row["db"]), args.samples, args.batch_size)
        votes_x, votes_y = results.count(x), results.count(y)
        # Draws that reproduce neither cluster abstain; no reproduced cluster leaves the pair undecided.
        p_x = votes_x / (votes_x + votes_y) if votes_x + votes_y else 0.5
        key = pair_key(x, y)
        pairs[key] = p_x if key.split("|")[0] == x else 1 - p_x
        draws[key] = {"first": results.count(key.split("|")[0]), "second": results.count(key.split("|")[1]),
                      "other": len(results) - votes_x - votes_y}
    return pairs, draws


def collect(args):
    config = deepcopy(load_config(args.config))
    saved = args.pool_dir / "config.json"
    if saved.exists():
        collected = json.loads(saved.read_text(encoding="utf-8"))
        config["execution"] = collected["execution"]
        config["generation"] = collected["generation"]
    else:
        config["generation"].update(PAPER_SAMPLING)
    config["correction"]["enabled"] = False
    if args.model:
        config["model"]["model_id"] = args.model
    rows = _read_pool(args.pool_dir / "pool.jsonl")
    items = {}
    if args.dataset:
        dataset = json.loads(args.dataset.read_text(encoding="utf-8"))
        # Dataset-relative paths become absolute so the prompt builder finds tables.json.
        items = {i["id"]: dict(i, tables_path=str((args.dataset.parent / i["tables_path"]).resolve()))
                 if i.get("tables_path") else i for i in dataset}
    known = {}
    if args.cav:
        # Imported here: selection_study imports this module.
        from evaluation.selection_study import CHECKS, _clean, enrich
        enrich(rows, None, config, args.pool_dir / "candidate_flags.json")
        plain = args.pool_dir / f"judgments-{args.mode}.jsonl"
        known = load(plain) if plain.exists() else {}
    out = args.output or args.pool_dir / f"judgments-{args.mode}{'-cav' if args.cav else ''}.jsonl"
    done = {json.loads(line)["id"] for line in out.read_text(encoding="utf-8").splitlines() if line.strip()} \
        if out.exists() else set()
    executor = SQLExecutor(config["execution"])
    judge = None
    with out.open("a", encoding="utf-8") as handle:
        for index, row in enumerate(rows, 1):
            if row["id"] in done:
                continue
            pool = _clean(row["pool"], CHECKS) if args.cav else row["pool"]
            groups = clusters(pool, args.min_size)[: args.top]
            pairs, draws, start = {}, {}, time.perf_counter()
            if len(groups) >= 2 and not all(pair_key(x[0]["result"], y[0]["result"]) in known.get(row["id"], {})
                                            for x, y in combinations(groups, 2)):
                judge = judge or Judge(config)
                database = Path(row["db"])
                shown = {g[0]["result"]: (g[0]["sql"], preview(executor.execute(database, g[0]["sql"])))
                         for g in groups}
                item = items.get(row["id"], {})
                hint = row.get("evidence") or item.get("evidence", "")
                if args.mode == "ab":
                    fill = dict(question=row["question"], evidence=f"Evidence:\n{hint}\n\n" if hint.strip() else "")
                    pairs = _ab_pairs(judge, row, shown, fill)
                else:
                    pairs, draws = _merge_pairs(judge, row, item, shown, hint, args, known.get(row["id"], {}))
            handle.write(json.dumps({"id": row["id"], "pairs": pairs, "draws": draws,
                                     "ms": (time.perf_counter() - start) * 1000}) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
            print(f"[{index}/{len(rows)}] {row['id']} clusters={len(groups)} pairs={len(pairs)} "
                  f"{time.perf_counter() - start:.1f}s", flush=True)


def load(path: Path) -> dict:
    """id -> {pair_key: probability that the lexicographically first result hash is correct}."""
    return {r["id"]: r["pairs"] for r in map(json.loads, path.read_text(encoding="utf-8").splitlines()) if r}


def preference(judgments: dict, qid: str, winner: str, challenger: str):
    """Probability that challenger beats winner, or None when the pair was never judged."""
    key = pair_key(winner, challenger)
    p = judgments.get(qid, {}).get(key)
    if p is None:
        return None
    return p if key.split("|")[0] == challenger else 1 - p


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pool_dir", type=Path, help="Directory with run_sweep's pool.jsonl")
    parser.add_argument("--mode", choices=["merge", "ab"], default="merge")
    parser.add_argument("--config", type=Path)
    parser.add_argument("--model", help="Judge model id or local folder (default: config model)")
    parser.add_argument("--dataset", type=Path, help="Dataset JSON: tables.json path (paper prompt) and evidence")
    parser.add_argument("--min-size", type=int, default=2, help="Smallest cluster that can be judged")
    parser.add_argument("--top", type=int, default=2, help="Judge pairs among this many largest clusters")
    parser.add_argument("--samples", type=int, default=4, help="merge: re-written SQL draws per pair")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--cav", action="store_true", help="Judge the top clusters left after CAV-3 (see above)")
    parser.add_argument("--output", type=Path, help="Default: <pool_dir>/judgments-<mode>[-cav].jsonl")
    collect(parser.parse_args())


if __name__ == "__main__":
    main()
