"""Build an executable ViText2SQL subset: Vietnamese questions, English Spider schemas/SQL.

ViText2SQL translates Spider's schema names, so its SQL does not run on the Spider SQLite
files. Its parsed `sql` field keeps Spider's table/column indices, so each item is matched to
the Spider original with the same database and parsed SQL; the original English SQL becomes
the gold query and the original English question is kept for a language comparison. Items
without a match, or whose gold SQL fails or returns too many rows, are dropped. The sample is
stratified by Spider hardness. Both datasets are downloaded locally; nothing is redistributed.
"""
import argparse
from collections import Counter, defaultdict
import json
import os
from pathlib import Path
import random
import re
import sqlite3

KEYWORDS = ("where", "join", "group", "having", "order", "limit", "intersect", "union", "except",
            "like", "between", "not", "in", "distinct", "count", "max", "min", "avg", "sum", "or", "and")


def _conds(conds):
    return [c for c in conds if isinstance(c, list)]


def _nested(sql):
    nested = [c[3] for c in _conds(sql["where"]) + _conds(sql["having"]) if isinstance(c[3], dict)]
    nested += [c[4] for c in _conds(sql["where"]) + _conds(sql["having"]) if isinstance(c[4], dict)]
    nested += [sql[k] for k in ("intersect", "union", "except") if sql[k]]
    nested += [t[1] for t in sql["from"]["table_units"] if t[0] == "sql"]
    return nested


def hardness(sql) -> str:
    """Re-implementation of Spider's eval_hardness (evaluation.py) on the parsed SQL."""
    where, having = _conds(sql["where"]), _conds(sql["having"])
    comp1 = (bool(where) + bool(sql["groupBy"]) + bool(sql["orderBy"]) + bool(sql["limit"])
             + max(len(sql["from"]["table_units"]) - 1, 0)
             + sum(c == "or" for c in sql["where"] + sql["having"])
             + sum(c[1] == 9 for c in where + having))
    comp2 = len(_nested(sql))
    aggs = sum(unit[0] != 0 for unit in sql["select"][1])
    others = (aggs > 1) + (len(sql["select"][1]) > 1) + (len(where) > 1) + (len(sql["groupBy"]) > 1)
    if comp1 <= 1 and others == 0 and comp2 == 0:
        return "easy"
    if (others <= 2 and comp1 <= 1 and comp2 == 0) or (comp1 <= 2 and others < 2 and comp2 == 0):
        return "medium"
    if ((others > 2 and comp1 <= 2 and comp2 == 0) or (2 < comp1 <= 3 and others <= 2 and comp2 == 0)
            or (comp1 <= 1 and others == 0 and comp2 <= 1)):
        return "hard"
    return "extra"


def _literals(sql: str) -> list[str]:
    pairs = re.findall(r"\"([^\"]*)\"|'([^']*)'", sql)
    return sorted(value.strip("%").strip().lower() for double, single in pairs if (value := double or single))


def _signature(sql: str):
    """Keyword counts and literal values: guards against Spider items whose parsed `sql` disagrees with `query`."""
    words = re.findall(r"[a-z_]+", re.sub(r"\"[^\"]*\"|'[^']*'", " ", sql.lower()))
    return tuple(words.count(k) for k in KEYWORDS), _literals(sql)


def _key(item):
    return item["db_id"], json.dumps(item["sql"], sort_keys=True)


def _gold_ok(path: Path, sql: str, max_rows: int) -> bool:
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    connection.text_factory = lambda b: b.decode("utf-8", "replace")
    try:
        return len(connection.execute(sql).fetchmany(max_rows + 1)) <= max_rows
    except sqlite3.Error:
        return False
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vitext2sql", type=Path, required=True, help="ViText2SQL split JSON (e.g. test.json)")
    parser.add_argument("--spider-root", type=Path, required=True, help="Folder with Spider JSON files and database/")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--size", type=int, default=200)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-gold-rows", type=int, default=50000)
    args = parser.parse_args()
    root = args.spider_root.resolve(strict=True)
    originals = defaultdict(list)
    for name in ("train_spider.json", "train_others.json", "dev.json"):
        for item in json.loads((root / name).read_text(encoding="utf-8")):
            originals[_key(item)].append(item)
    items = json.loads(args.vitext2sql.read_text(encoding="utf-8"))
    used = Counter()
    records, dropped = [], Counter()
    for index, item in enumerate(items):
        matches = originals.get(_key(item))
        if not matches:
            dropped["no_spider_match"] += 1
            continue
        matches = [m for m in matches if _signature(m["query"]) == _signature(item["query"])]
        if not matches:
            dropped["spider_annotation_mismatch"] += 1
            continue
        # Paraphrases share one parsed SQL; take them in order so English questions stay distinct.
        original = matches[min(used[_key(item)], len(matches) - 1)]
        used[_key(item)] += 1
        question = item["question"].lower()
        if any(value not in question for value in _literals(original["query"])):
            dropped["value_translated_in_question"] += 1
            continue
        path = root / "database" / item["db_id"] / f"{item['db_id']}.sqlite"
        if not path.is_file() or not _gold_ok(path, original["query"], args.max_gold_rows):
            dropped["gold_not_executable"] += 1
            continue
        records.append({
            "id": f"vitext2sql_{args.vitext2sql.stem}_{index}", "db_id": item["db_id"],
            "db_path": os.path.relpath(path, args.output.resolve().parent),
            "question": " ".join(item["question"].split()).replace(" ?", "?").replace(" .", ".").replace(" ,", ","),
            "question_en": original["question"], "evidence": "", "gold_sql": original["query"],
            "difficulty": hardness(item["sql"]), "tags": [], "source": "ViText2SQL + Spider", "language": "vi",
        })
    rng = random.Random(args.seed)
    by_level = defaultdict(list)
    for record in records:
        by_level[record["difficulty"]].append(record)
    quotas = {level: round(args.size * len(group) / len(records)) for level, group in by_level.items()}
    largest = max(quotas, key=quotas.get)
    quotas[largest] += args.size - sum(quotas.values())
    sample = [r for level, group in sorted(by_level.items()) for r in rng.sample(group, quotas[level])]
    rng.shuffle(sample)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(sample, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"input": len(items), "executable": len(records), "dropped": dropped,
                      "pool_hardness": {k: len(v) for k, v in sorted(by_level.items())},
                      "sample_hardness": dict(Counter(r["difficulty"] for r in sample)),
                      "sample_databases": len({r["db_id"] for r in sample})}, indent=2))


if __name__ == "__main__":
    main()
