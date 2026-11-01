"""Convert a locally downloaded Spider split (JSON + SQLite) for run_sweep --prompt paper.

Every item is kept, in the official order, so results compare with papers reporting the full
split. Difficulty is Spider's hardness from the parsed `sql`. Gold SQL that fails to execute is
reported but not dropped: it still counts as a question every method gets wrong.
"""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import sqlite3

from import_vitext2sql import hardness


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spider-root", type=Path, required=True, help="Folder with dev.json, tables.json, database/")
    parser.add_argument("--split", default="dev.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.spider_root.resolve(strict=True)
    items = json.loads((root / args.split).read_text(encoding="utf-8"))
    base = args.output.resolve().parent
    tables = os.path.relpath(root / "tables.json", base)
    records, failing = [], []
    for index, item in enumerate(items):
        path = root / "database" / item["db_id"] / f"{item['db_id']}.sqlite"
        if not path.is_file():
            raise ValueError(f"Missing SQLite database for item {index}: {item['db_id']}")
        connection = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
        connection.text_factory = lambda b: b.decode("utf-8", "replace")
        try:
            connection.execute(item["query"]).fetchmany(1)
        except sqlite3.Error:
            failing.append(index)
        finally:
            connection.close()
        records.append({
            "id": f"spider_{Path(args.split).stem}_{index}", "db_id": item["db_id"],
            "db_path": os.path.relpath(path, base), "tables_path": tables,
            "question": item["question"], "evidence": "", "gold_sql": item["query"],
            "difficulty": hardness(item["sql"]), "tags": [], "source": "Spider", "language": "en",
        })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"questions": len(records), "databases": len({r["db_id"] for r in records}),
                      "hardness": dict(Counter(r["difficulty"] for r in records)),
                      "gold_not_executable": failing}, indent=2))


if __name__ == "__main__":
    main()
