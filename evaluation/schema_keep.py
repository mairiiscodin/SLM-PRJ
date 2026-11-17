"""Schema for a second, pruned-prompt sampling round, from the first-round samples of each question.

No model call. Reads a pool.jsonl, takes the first --samples samples of every question and writes
{question id: [[table, column], ...]} for `vllm_collect --keep-schema`. Also reports how often
the kept schema still holds every table/column of the gold SQL, and how much of the schema is left.

    python -m evaluation.schema_keep results/bird-dev-vllm-64/pool.jsonl data/benchmarks/bird_dev.json \\
        --samples 32 --output data/benchmarks/bird_dev_keep32.json
"""
import argparse
import json
from pathlib import Path

from core.omnisql_prompt import _tables
from core.schema_pruning import kept_columns, sql_names


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pool", type=Path)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--samples", type=int, default=32)
    parser.add_argument("--mode", choices=["columns", "tables"], default="columns")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    items = {item["id"]: item for item in json.loads(args.dataset.read_text(encoding="utf-8"))}
    keep, covered, share, total = {}, 0, 0.0, 0
    for line in args.pool.open(encoding="utf-8"):
        row = json.loads(line)
        item = items[row["id"]]
        tables_path = (args.dataset.parent / item["tables_path"].replace("\\", "/")).resolve()
        info = _tables(str(tables_path))[item["db_id"]]
        sqls = [c["sql"] for c in row["pool"][: args.samples] if c["success"]]
        kept = kept_columns(sqls, info, args.mode)
        if kept:
            keep[row["id"]] = kept
        gold = sql_names(item["gold_sql"])
        if gold:
            names = info["table_names_original"]
            every = [(names[o].lower(), c.lower()) for o, c in info["column_names_original"] if o >= 0]
            needed = {(t, c) for t, c in every if t in gold[0] and c in gold[1]}
            shown = {(t.lower(), c.lower()) for t, c in kept} or set(every)
            total += 1
            covered += needed <= shown and gold[0] & {t for t, _ in every} <= {t for t, _ in shown}
            share += len(shown) / len(every)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(keep, ensure_ascii=False), encoding="utf-8")
    print(f"{len(keep)}/{len(items)} questions pruned ({args.mode}, first {args.samples} samples); "
          f"gold tables and columns all kept: {covered}/{total} ({covered / max(1, total):.1%}); "
          f"columns shown: {share / max(1, total):.1%} of the schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
