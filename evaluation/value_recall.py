"""Offline check of value retrieval: are the gold SQL's text literals shown as column examples?

No model is needed. For every `column = 'literal'` / `IN (...)` / `!=` in the gold SQL whose literal
exists in that column of the database, the literal counts as recalled if it is among the example
values the prompt shows for a column of that name. With a pool, it also reports how often a
missed literal coincides with no candidate using it and with no candidate being correct.

    python -m evaluation.value_recall data/benchmarks/bird_dev.json --retrieval paper new \
        --pool results/bird-dev-vllm-64/pool.jsonl
"""
import argparse
from collections import Counter
from functools import lru_cache
import json
from pathlib import Path
import time

import sqlglot
from sqlglot import exp

from core.omnisql_prompt import _text_values, column_examples


def gold_literals(sql: str) -> list[tuple[str, str]]:
    """(column name lowercase, literal) pairs compared by equality in the gold SQL."""
    try:
        tree = sqlglot.parse_one(sql, read="sqlite")
    except sqlglot.errors.ParseError:
        return []
    pairs = []
    for node in tree.find_all(exp.EQ, exp.NEQ, exp.In):
        if isinstance(node, exp.In):
            column, literals = node.this, node.expressions
        else:
            column, literal = node.this, node.expression
            if isinstance(column, exp.Literal):
                column, literal = literal, column
            literals = [literal]
        if not isinstance(column, exp.Column):
            continue
        for literal in literals:
            if isinstance(literal, exp.Literal) and literal.is_string and literal.this:
                pairs.append((column.name.lower(), literal.this))
    return list(dict.fromkeys(pairs))


@lru_cache(maxsize=16)
def _value_set(db_path: str) -> frozenset:
    return frozenset((key.rsplit(".", 1)[1], value) for key, value, _ in _text_values(db_path))


def _in_database(db_path: str, column: str, literal: str) -> bool:
    return (column, literal) in _value_set(db_path)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--retrieval", nargs="+", default=["paper"])
    parser.add_argument("--pool", type=Path, help="pool.jsonl for the same dataset (optional)")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output", type=Path, help="write per-literal rows as JSONL")
    args = parser.parse_args(argv)

    items = json.loads(args.dataset.read_text(encoding="utf-8"))[: args.limit]
    pool = {}
    if args.pool:
        for line in args.pool.open(encoding="utf-8"):
            row = json.loads(line)
            pool[row["id"]] = row["pool"]

    rows, timing = [], Counter()
    started = time.perf_counter()
    for number, item in enumerate(items, 1):
        if number % 50 == 0:
            print(f"  {number}/{len(items)} questions, {time.perf_counter() - started:.0f} s", flush=True)
        db_path = str((args.dataset.parent / item["db_path"]).resolve())
        question = f"{item['evidence']}\n{item['question']}" if item.get("evidence", "").strip() else item["question"]
        literals = [(c, v) for c, v in gold_literals(item["gold_sql"]) if _in_database(db_path, c, v)]
        if not literals:
            continue
        shown = {}
        for method in args.retrieval:
            start = time.perf_counter()
            examples = column_examples(Path(db_path), question, method)
            timing[method] += time.perf_counter() - start
            shown[method] = examples
        candidates = pool.get(item["id"], [])
        for column, literal in literals:
            row = {"id": item["id"], "difficulty": item.get("difficulty"), "column": column, "literal": literal,
                   "verbatim": literal in question,
                   "used_by_pool": any(f"'{literal}'" in (c.get("sql") or "") for c in candidates) if candidates else None,
                   "oracle": any(c.get("correct_set") for c in candidates) if candidates else None}
            for method, examples in shown.items():
                row[method] = any(literal in values for key, values in examples.items() if key.endswith("." + column))
            rows.append(row)

    print(f"{len(rows)} gold literals present in the database, {len({r['id'] for r in rows})} questions")
    for method in args.retrieval:
        hit = sum(r[method] for r in rows)
        not_verbatim = [r for r in rows if not r["verbatim"]]
        print(f"[{method}] recall {hit / len(rows):.1%} ({hit}/{len(rows)}); "
              f"not verbatim in question/evidence: {sum(r[method] for r in not_verbatim)}/{len(not_verbatim)}; "
              f"{timing[method] / max(1, len({r['id'] for r in rows})) * 1000:.0f} ms/question")
        if pool:
            missed = [r for r in rows if not r[method]]
            print(f"    missed: {len(missed)}, of which no candidate uses the literal: "
                  f"{sum(not r['used_by_pool'] for r in missed)}, question oracle-wrong: "
                  f"{sum(not r['oracle'] for r in missed)}")
    if pool:
        hit_oracle = Counter((r[args.retrieval[0]], r["oracle"]) for r in rows)
        print("oracle rate by recall of", args.retrieval[0], dict(hit_oracle))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
