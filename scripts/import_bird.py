"""Convert a locally downloaded BIRD JSON/SQLite package; no automatic downloads.

With --tables the records carry `tables_path` for run_sweep --prompt paper. --sample N keeps a
difficulty-stratified subset (proportional to the full split, official order preserved) so a
small GPU can finish a run; the same --seed always picks the same questions. Gold SQL that fails
to execute is reported but kept: it still counts as a question every method gets wrong.
"""
import argparse
from collections import Counter, defaultdict
import json
import os
from pathlib import Path
import random
import sqlite3


def stratified(items: list, size: int, seed: int) -> list:
    """Largest-remainder allocation per difficulty, then a seeded draw inside each level."""
    levels = defaultdict(list)
    for index, item in enumerate(items):
        levels[item.get("difficulty", "unknown")].append(index)
    quotas = {level: size * len(indices) / len(items) for level, indices in levels.items()}
    counts = {level: int(q) for level, q in quotas.items()}
    for level in sorted(quotas, key=lambda l: quotas[l] - counts[l], reverse=True)[: size - sum(counts.values())]:
        counts[level] += 1
    rng = random.Random(seed)
    chosen = [i for level in sorted(levels) for i in rng.sample(levels[level], counts[level])]
    return [items[i] for i in sorted(chosen)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=Path, required=True, help="dev.json or mini_dev_sqlite.json")
    parser.add_argument("--database-root", type=Path, required=True, help="Folder of <db_id>/<db_id>.sqlite")
    parser.add_argument("--tables", type=Path, help="dev_tables.json; needed for run_sweep --prompt paper")
    parser.add_argument("--sample", type=int, help="Stratified subset size (default: every question)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    items = json.loads(args.questions.read_text(encoding="utf-8"))
    if args.sample and args.sample < len(items):
        items = stratified(items, args.sample, args.seed)
    root = args.database_root.resolve(strict=True)
    base = args.output.resolve().parent
    tables = Path(os.path.relpath(args.tables.resolve(strict=True), base)).as_posix() if args.tables else None
    records, failing = [], []
    for index, item in enumerate(items):
        db_id = item["db_id"]
        path = (root / db_id / (db_id + ".sqlite")).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f"Missing SQLite database for item {index}.")
        gold = item.get("SQL") or item.get("sql")
        if not isinstance(gold, str) or not gold.strip():
            raise ValueError(f"Missing gold SQL for item {index}.")
        connection = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
        connection.text_factory = lambda b: b.decode("utf-8", "replace")
        try:
            connection.execute(gold).fetchmany(1)
        except sqlite3.Error:
            failing.append(item.get("question_id", index))
        finally:
            connection.close()
        record = {"id": f"bird_{item.get('question_id', index)}", "db_id": db_id,
                  "db_path": Path(os.path.relpath(path, base)).as_posix(),
                  "question": item["question"], "evidence": item.get("evidence", ""),
                  "gold_sql": gold, "difficulty": item.get("difficulty", "unknown"),
                  "tags": [], "source": "BIRD (user supplied)", "language": "en"}
        if tables:
            record["tables_path"] = tables
        records.append(record)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"questions": len(records), "databases": len({r["db_id"] for r in records}),
                      "difficulty": dict(Counter(r["difficulty"] for r in records)),
                      "gold_not_executable": failing}, indent=2))


if __name__ == "__main__":
    main()
