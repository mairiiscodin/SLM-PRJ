"""Replay the merge-revision draws of evaluation.vllm_merge on a pool, without model calls.

A policy keeps the base selection (vote or CAV-3) unless the merge model overrules it:
  free: the largest result cluster of the draws replaces the answer, as CSC-SQL does; it may be a new query.
  pick: only the winner/rival pair counts; the rival must get more draws than the winner.
A gate g asks the model only when rival votes >= g * winner votes (g = 0: every contested question).

The gate is chosen on the tuning questions (--tune, bird_dev200) for each policy; the report on the
other questions is the number to quote. Questions without a rival or a usable draw keep the base answer.

    python -m evaluation.merge_study results/bird-dev-vllm-64 results/bird-dev-merge \\
        --flags results/selection-bird-dev-vllm-64/candidate_flags.json \\
        --tune data/benchmarks/bird_dev200.json --output results/merge-study-bird-dev
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import random

from core.config import load_config
from evaluation.run_sweep import _read_pool, _select
from evaluation.selection_study import bootstrap, mcnemar
from evaluation.vllm_merge import apply_flags, clean

GATES = [0.0, 0.1, 0.25, 0.5, 0.75]


def load_merge(paths: list) -> dict:
    """(question id, source) -> merge row; paths are merge.jsonl files or directories holding one."""
    out = {}
    for path in paths:
        path = path / "merge.jsonl" if path.is_dir() else path
        for row in map(json.loads, path.read_text(encoding="utf-8").splitlines()):
            for source in row["sources"]:
                out[(row["id"], source)] = row
    return out


def overrule(row, base: bool, mode: str, gate: float, source: str, pool: list) -> bool:
    """Correctness of the answer after the merge model had its say on one question."""
    if row is None:
        return base
    winner_votes, rival_votes = row["sources"][source]
    if rival_votes < gate * winner_votes:
        return base
    draws = [d for d in row["draws"] if d["success"]]
    if not draws:
        return base
    counts = Counter(d["result"] for d in draws)
    if mode == "pick":
        if counts[row["rival"]] <= counts[row["winner"]]:
            return base
        return next(r["correct"] for r in pool if r["result"] == row["rival"])
    # Ties keep the base answer when it is among the largest clusters.
    top = max(counts.values())
    if counts[row["winner"]] == top:
        return base
    best = next(h for h, n in counts.items() if n == top)
    return next(d["correct"] for d in draws if d["result"] == best)


def evaluate(rows, merge, source, mode, gate, bases):
    return [overrule(merge.get((row["id"], source)), base, mode, gate, source, row["pool"])
            for row, base in zip(rows, bases[source])]


def choose_gate(rows, merge, source, mode, bases, tune):
    """Best gate on the tuning questions; ties go to the larger gate (fewer model calls)."""
    scored = []
    for gate in GATES:
        hits = evaluate(rows, merge, source, mode, gate, bases)
        scored.append((sum(h for h, t in zip(hits, tune) if t), gate))
    return max(scored)[1]


def line(name, hits, base, rng):
    n = len(hits)
    delta = [float(a) - float(b) for a, b in zip(hits, base)]
    low, high, _ = bootstrap(delta, rng, 2000)
    lost, gained, p = mcnemar(base, hits)
    return (f"| {name} | {n} | {100 * sum(hits) / n:.2f} | {100 * sum(delta) / n:+.2f} "
            f"[{100 * low:+.2f}, {100 * high:+.2f}] | {lost} / {gained} | {p:.3f} |")


def study(args):
    weights = load_config(args.config)["ranking"]
    rows = _read_pool(args.pool_dir / "pool.jsonl", metric="set")
    apply_flags(rows, json.loads(args.flags.read_text(encoding="utf-8")))
    merge = load_merge(args.merge)
    tune_ids = {i["id"] for i in json.loads(args.tune.read_text(encoding="utf-8"))}
    tune = [row["id"] in tune_ids for row in rows]
    bases = {"vote": [bool(_select(r["pool"], weights)) for r in rows],
             "cav": [bool(_select(clean(r["pool"]), weights)) if clean(r["pool"]) else False for r in rows]}
    rng = random.Random(args.seed)
    policies = [("CSC theo bài báo: vote + merge", "vote", "free", 0.0)]
    for mode, label in (("free", "CAV-3 + merge"), ("pick", "CAV-3 + merge chỉ chọn trong cặp")):
        gate = choose_gate(rows, merge, "cav", mode, bases, tune)
        policies.append((f"{label} (gate {gate})", "cav", mode, gate))
    held = [i for i, t in enumerate(tune) if not t]
    blocks = []
    for title, keep in ((f"Câu không dùng để chỉnh ({len(held)} câu)", held),
                        (f"Toàn bộ ({len(rows)} câu)", list(range(len(rows)))),
                        (f"Câu dùng để chỉnh gate ({sum(tune)} câu)", [i for i, t in enumerate(tune) if t])):
        table = [f"### {title}", "", "| Cách chọn | Số câu | EX % | Δ vs CAV-3 [CI95] | Mất / cứu | p |",
                 "|---|---|---|---|---|---|"]
        cav = [bases["cav"][i] for i in keep]
        table.append(line("Vote", [bases["vote"][i] for i in keep], cav, rng))
        table.append(f"| CAV-3 | {len(keep)} | {100 * sum(cav) / len(keep):.2f} | | | |")
        for name, source, mode, gate in policies:
            hits = evaluate(rows, merge, source, mode, gate, bases)
            table.append(line(name, [hits[i] for i in keep], cav, rng))
        blocks.append("\n".join(table))
    judged = len({k[0] for k in merge})
    text = f"Merge model đã xét {judged}/{len(rows)} câu.\n\n" + "\n\n".join(blocks) + "\n"
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "tables.md").write_text(text, encoding="utf-8")
    print(text.encode("ascii", "replace").decode() if args.ascii else text)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pool_dir", type=Path)
    parser.add_argument("merge", type=Path, nargs="+", help="merge.jsonl files, or directories with one (shards)")
    parser.add_argument("--flags", type=Path, required=True)
    parser.add_argument("--tune", type=Path, required=True, help="Dataset JSON of the questions that choose the gate")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--ascii", action="store_true", help="Console without UTF-8")
    study(parser.parse_args())


if __name__ == "__main__":
    main()
