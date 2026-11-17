"""Does mixing samples from several small models beat the same number of samples from one model?

No model calls. Each pool is a vllm_collect/run_sweep pool.jsonl of the same questions from a
different model. Candidates get the CAV flags (re-executed once per pool, cached in --output), then
a weighted execution vote is taken over the least-flagged candidates of the mixed pool.

To separate "another model" from "more samples", the mixed pools keep the base budget: with a
64-sample base and a 16-sample extra pool, base[:48] + extra[:16] is compared with base[:64].
The extra model's vote weight is chosen on --tune (bird_dev200) and reported on the other questions.

    python -m evaluation.ensemble_study results/bird-dev-vllm-64 results/bird-dev-slm13 \\
        --flags results/selection-bird-dev-vllm-64/candidate_flags.json \\
        --tune data/benchmarks/bird_dev200.json --output results/ensemble-bird-dev
"""
import argparse
import json
from pathlib import Path
import random

from core.config import ROOT, load_config
from core.consistency_checks import CHECKS
from evaluation.run_sweep import _read_pool
from evaluation.selection_study import bootstrap, enrich, mcnemar

WEIGHTS = [0.5, 0.75, 1.0, 1.5, 2.0]


def read_pool_dir(path: Path, metric: str) -> list[dict]:
    """A pool directory, or one holding shard*/pool.jsonl from a multi-GPU run."""
    files = [path / "pool.jsonl"] if (path / "pool.jsonl").exists() else sorted(path.glob("shard*/pool.jsonl"))
    if not files:
        raise FileNotFoundError(f"No pool.jsonl under {path}")
    return [row for file in files for row in _read_pool(file, metric=metric)]


def apply_cached_flags(rows: list[dict], cache: dict) -> bool:
    """Attach flags from a candidate_flags.json; False when a successful candidate is missing."""
    complete = True
    for row in rows:
        name = Path(row["db"]).name
        for record in row["pool"]:
            if record["success"]:
                flags = cache.get(f"{name}|{record['sql']}")
                if flags is None:
                    complete = False
                else:
                    record.update(flags)
    return complete


def choose(weighted: list[tuple[dict, float]]) -> bool:
    """Correctness of the heaviest result cluster among the least-flagged successful candidates."""
    ok = [(r, w) for r, w in weighted if r["success"] and w > 0]
    if not ok:
        return False
    fewest = min(sum(bool(r.get(c)) for c in CHECKS) for r, _ in ok)
    totals, first = {}, {}
    for record, weight in ok:
        if sum(bool(record.get(c)) for c in CHECKS) == fewest:
            totals[record["result"]] = totals.get(record["result"], 0.0) + weight
            first.setdefault(record["result"], record)
    return bool(first[max(totals, key=totals.get)]["correct"])  # ties: first seen, i.e. the base model


def study(args):
    config = load_config(args.config)
    args.output.mkdir(parents=True, exist_ok=True)
    pools, names = [], []
    for index, directory in enumerate(args.pools):
        rows = read_pool_dir(directory, args.metric)
        cache_path = args.output / f"flags-{directory.name}.json"
        source = args.flags if index == 0 and args.flags else cache_path
        if not (source.exists() and apply_cached_flags(rows, json.loads(source.read_text(encoding="utf-8")))):
            saved = directory / "config.json"
            if not saved.exists():
                saved = next(directory.glob("shard*/config.json"), saved)
            if saved.exists():
                config["execution"] = json.loads(saved.read_text(encoding="utf-8"))["execution"]
            for row in rows:
                row.setdefault("greedy", None)
                row["db"] = str(ROOT / row["db"]) if not Path(row["db"]).is_absolute() else row["db"]
            print(f"Computing flags for {directory.name} (re-executes every SQL once)...", flush=True)
            enrich(rows, None, config, cache_path)
        pools.append({row["id"]: row for row in rows})
        names.append(directory.name)

    base, extras = pools[0], pools[1:]
    ids = [q for q in base if all(q in extra for extra in extras)]
    if len(ids) != len(base):
        print(f"Only {len(ids)}/{len(base)} questions are in every pool; the rest are ignored.")
    budget = min(len(base[q]["pool"]) for q in ids)
    extra_sizes = [min(len(extra[q]["pool"]) for q in ids) for extra in extras]
    tune = {item["id"] for item in json.loads(args.tune.read_text(encoding="utf-8"))} if args.tune else set()
    held_out = [q for q in ids if q not in tune]

    def run(base_count, extra_counts, weight):
        out = {}
        for q in ids:
            mixed = [(r, 1.0) for r in base[q]["pool"][:base_count]]
            for extra, count in zip(extras, extra_counts):
                mixed += [(r, weight) for r in extra[q]["pool"][:count]]
            out[q] = choose(mixed)
        return out

    def accuracy(result, subset):
        return 100 * sum(result[q] for q in subset) / max(1, len(subset))

    rows_out = []
    reference = run(budget, [0] * len(extras), 1.0)
    configs = [(f"{names[0]} only, K={budget}", budget, [0] * len(extras), 1.0)]
    for extra_name, size, position in zip(names[1:], extra_sizes, range(len(extras))):
        counts = [size if i == position else 0 for i in range(len(extras))]
        configs.append((f"{extra_name} only, K={size}", 0, counts, 1.0))
        if size < budget:
            configs.append((f"{names[0]} only, K={size}", size, [0] * len(extras), 1.0))
    # --extra: samples taken from every extra pool; default: all of them.
    for per_pool in args.extra or [max(extra_sizes)]:
        counts = [min(per_pool, size) for size in extra_sizes]
        taken = sum(counts)
        if 0 < budget - taken:
            if (budget - taken) not in extra_sizes:
                configs.append((f"{names[0]} only, K={budget - taken}", budget - taken, [0] * len(extras), 1.0))
            for weight in WEIGHTS:
                configs.append((f"same budget: base {budget - taken} + extra {taken}, w={weight}",
                                budget - taken, counts, weight))
        for weight in WEIGHTS:
            configs.append((f"more samples: base {budget} + extra {taken}, w={weight}", budget, counts, weight))

    rng = random.Random(config["seed"])
    for label, base_count, counts, weight in configs:
        result = run(base_count, counts, weight)
        lost, won, p = mcnemar([reference[q] for q in held_out], [result[q] for q in held_out])
        delta = [float(result[q]) - float(reference[q]) for q in held_out]
        low, high, _ = bootstrap(delta, rng, args.resamples)
        rows_out.append({"config": label, "all": accuracy(result, ids), "tune": accuracy(result, [q for q in ids if q in tune]),
                         "held_out": accuracy(result, held_out), "delta": 100 * sum(delta) / max(1, len(delta)),
                         "ci_low": 100 * low, "ci_high": 100 * high, "lost": lost, "won": won, "p": p})

    oracle = {name: 100 * sum(any(r["correct"] for r in pool[q]["pool"]) for q in ids) / len(ids)
              for name, pool in zip(names, pools)}
    oracle["union"] = 100 * sum(any(r["correct"] for pool in pools for r in pool[q]["pool"]) for q in ids) / len(ids)
    lines = [f"# Ensemble study: {' + '.join(names)}", "",
             f"{len(ids)} questions ({len(held_out)} held-out, {len(ids) - len(held_out)} for choosing the weight). "
             f"Selection: weighted vote over the least-flagged candidates (CAV-3). Δ, lost/won and p are on the "
             f"held-out questions against `{configs[0][0]}`.", "",
             "Oracle (any correct sample): " + ", ".join(f"{k} {v:.1f}%" for k, v in oracle.items()), "",
             "| Config | All | Tune | Held-out | Δ held-out [CI95] | Lost / won | p |", "|---|---|---|---|---|---|---|"]
    for r in rows_out:
        lines.append(f"| {r['config']} | {r['all']:.2f} | {r['tune']:.1f} | {r['held_out']:.2f} | "
                     f"{r['delta']:+.2f} [{r['ci_low']:+.2f}, {r['ci_high']:+.2f}] | {r['lost']} / {r['won']} | {r['p']:.3f} |")
    (args.output / "tables.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (args.output / "ensemble.json").write_text(json.dumps({"oracle": oracle, "rows": rows_out}, indent=2), encoding="utf-8")
    print("\n".join(lines))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pools", type=Path, nargs="+", help="Base pool directory, then one per extra model")
    parser.add_argument("--flags", type=Path, help="Existing candidate_flags.json of the base pool")
    parser.add_argument("--tune", type=Path, help="Dataset JSON whose questions are used to choose the weight")
    parser.add_argument("--extra", type=int, nargs="+",
                        help="Samples taken from each extra pool, one set of rows per value (default: all)")
    parser.add_argument("--metric", default="set")
    parser.add_argument("--config", type=Path)
    parser.add_argument("--resamples", type=int, default=2000)
    parser.add_argument("--output", type=Path, required=True)
    study(parser.parse_args(argv))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
