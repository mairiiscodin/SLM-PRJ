"""Append extra samples to a pool: base pool.jsonl + one or more pools of the same questions.

The extra pools come from vllm_collect with --seed-offset (and usually --shard, one directory per
GPU); every question of the base must appear in exactly one of them. Candidates keep their order
(base first), so selection_study's fixed K=16 on the canonical order still sees the base pool.

    python scripts/merge_pools.py results/bird-dev-vllm results/bird-dev-vllm-extra48/shard0 \\
        results/bird-dev-vllm-extra48/shard1 --output results/bird-dev-vllm-64
"""
import argparse
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evaluation.run_sweep import _read_pool  # noqa: E402


def merge(base: list[dict], extras: list[dict]) -> list[dict]:
    by_id = {}
    for row in extras:
        if row["id"] in by_id:
            raise ValueError(f"{row['id']} appears in more than one extra pool")
        by_id[row["id"]] = row
    missing = [row["id"] for row in base if row["id"] not in by_id]
    if missing:
        raise ValueError(f"{len(missing)} question(s) have no extra samples, e.g. {missing[:3]}")
    if len(by_id) != len(base):
        raise ValueError("Extra pools contain questions that are not in the base pool")
    merged = []
    for row in base:
        extra = by_id[row["id"]]
        if extra["gold_sql"] != row["gold_sql"] or extra["db"] != row["db"]:
            raise ValueError(f"{row['id']}: gold SQL or database differs between pools")
        # Latency is kept per base-sized batch so _batch_cost stays comparable across budgets.
        scale = row["batch_size"] / extra["batch_size"]
        merged.append(dict(row, pool=row["pool"] + extra["pool"],
                           batch_ms=row["batch_ms"] + [ms * scale for ms in extra["batch_ms"]]))
    return merged


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("base", type=Path, help="Pool directory of the first run")
    parser.add_argument("extra", type=Path, nargs="+", help="Pool directories with the extra samples")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    base = _read_pool(args.base / "pool.jsonl")
    extras = [row for path in args.extra for row in _read_pool(path / "pool.jsonl")]
    merged = merge(base, extras)
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / "pool.jsonl").open("w", encoding="utf-8") as handle:
        for row in merged:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    shutil.copy(args.base / "config.json", args.output / "config.json")
    sizes = sorted({len(row["pool"]) for row in merged})
    print(f"{len(merged)} questions, pool size {sizes} -> {args.output / 'pool.jsonl'}")


if __name__ == "__main__":
    main()
