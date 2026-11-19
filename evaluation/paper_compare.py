"""Self-consistency EX of every model run next to the SLM-SQL paper's numbers.

Covers the runs made by notebooks/paper/*.ipynb (scripts/make_paper_notebooks.py):
  * BIRD dev, paper Table 2: the five SLM-SQL models (64 samples + CSC in the paper).
  * Spider dev, paper Table 3 "Dev EX": base / SFT / SFT+RL of each base model (16 samples).

A run directory holds pool.jsonl, or shard*/pool.jsonl as written on Kaggle (questions split over
GPUs). Vote@K uses the first K samples of every question (the canonical order), so Vote@16 of a
64-sample pool is the 16-sample setting. Runs that are missing are listed as such.

    python -m evaluation.paper_compare                       # table -> results/paper-compare/tables.md
    python -m evaluation.paper_compare --write-pool          # also writes <run>/pool.jsonl for selection_study
    python -m evaluation.paper_compare --combine results/bird-dev-slm13   # only join shards of these dirs
"""
import argparse
import json
from pathlib import Path
import re
import statistics

from core.config import ROOT, load_config
from evaluation.run_sweep import _read_pool, _select

# (benchmark, run directory under results/, model, train method, paper SC, paper CSC)
# BIRD: Table 2 reports only the full method (64 samples + CSC).
# Spider: Table 3, Dev EX (16 samples; CSC adds merge revision).
RUNS = [
    ("bird", "bird-dev-0.5b-rl", "cycloneboy/SLM-SQL-0.5B", "SFT + RL", None, 56.87),
    ("bird", "bird-dev-0.6b-rl", "cycloneboy/SLM-SQL-0.6B", "SFT + RL", None, 59.52),
    ("bird", "bird-dev-1b-sft", "cycloneboy/SLM-SQL-Base-1B", "SFT (RL chưa công bố)", None, 54.78),
    ("bird", "bird-dev-1.3b-rl", "cycloneboy/SLM-SQL-1.3B", "SFT + RL", None, 62.19),
    ("bird", "bird-dev-vllm-64", "cycloneboy/SLM-SQL-1.5B", "SFT + RL", None, 67.08),
    ("spider", "spider-dev-0.5b-base", "Qwen/Qwen2.5-Coder-0.5B-Instruct", "-", 42.13, 44.07),
    ("spider", "spider-dev-0.5b-sft", "cycloneboy/SLM-SQL-Base-0.5B", "SFT", 65.31, 68.28),
    ("spider", "spider-dev-0.5b-rl", "cycloneboy/SLM-SQL-0.5B", "SFT + RL", 70.60, 72.08),
    ("spider", "spider-dev-0.6b-base", "Qwen/Qwen3-0.6B", "-", 63.19, 65.15),
    ("spider", "spider-dev-0.6b-sft", "cycloneboy/SLM-SQL-Base-0.6B", "SFT", 68.02, 70.05),
    ("spider", "spider-dev-0.6b-rl", "cycloneboy/SLM-SQL-0.6B", "SFT + RL", 72.05, 72.99),
    ("spider", "spider-dev-1b-base", "unsloth/Llama-3.2-1B-Instruct", "-", 30.79, 32.72),
    ("spider", "spider-dev-1b-sft", "cycloneboy/SLM-SQL-Base-1B", "SFT", 63.77, 66.18),
    ("spider", None, "SLM-SQL-1B (Llama, SFT + RL)", "SFT + RL (chưa công bố)", 67.63, 69.12),
    ("spider", "spider-dev-1.3b-base", "deepseek-ai/deepseek-coder-1.3b-instruct", "-", 48.23, 49.94),
    ("spider", "spider-dev-1.3b-sft", "cycloneboy/SLM-SQL-Base-1.3B", "SFT", 72.86, 74.31),
    ("spider", "spider-dev-1.3b-rl", "cycloneboy/SLM-SQL-1.3B", "SFT + RL", 75.47, 76.11),
    ("spider", "spider-dev-1.5b-base", "Qwen/Qwen2.5-Coder-1.5B-Instruct", "-", 63.54, 65.99),
    ("spider", "spider-dev-1.5b-sft", "cycloneboy/SLM-SQL-Base-1.5B", "SFT", 74.53, 76.66),
    ("spider", "spider-dev-1.5b-rl", "cycloneboy/SLM-SQL-1.5B", "SFT + RL", 75.15, 76.72),
]
METRIC = {"bird": "set", "spider": "spider"}
TOTAL = {"bird": 1534, "spider": 1034}


def _order(row) -> tuple:
    match = re.search(r"(\d+)$", row["id"])
    return (int(match.group(1)) if match else 0, row["id"])


def pool_files(run: Path) -> list[Path]:
    if (run / "pool.jsonl").exists():
        return [run / "pool.jsonl"]
    return sorted(run.glob("shard*/pool.jsonl"))


def load(run: Path, metric: str = "strict") -> list[dict]:
    rows = [row for path in pool_files(run) for row in _read_pool(path, metric=metric)]
    return sorted(rows, key=_order)


def combine(run: Path) -> Path:
    """Join shard*/pool.jsonl into <run>/pool.jsonl (dataset order) for selection_study / merge_pools."""
    shards = sorted(run.glob("shard*/pool.jsonl"))
    if not shards:
        raise SystemExit(f"{run}: không có shard*/pool.jsonl")
    rows = sorted((row for path in shards for row in _read_pool(path)), key=_order)
    ids = [row["id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit(f"{run}: một câu xuất hiện ở nhiều shard")
    with (run / "pool.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    config = shards[0].parent / "config.json"
    if config.exists() and not (run / "config.json").exists():
        (run / "config.json").write_text(config.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"{run}: {len(rows)} câu -> {run / 'pool.jsonl'}")
    return run / "pool.jsonl"


def score(rows: list[dict], weights: dict) -> dict:
    sizes = [len(row["pool"]) for row in rows]
    out = {"questions": len(rows), "samples": min(sizes),
           "sample_acc": 100 * statistics.fmean(c["correct"] for row in rows for c in row["pool"]),
           "oracle": 100 * statistics.fmean(any(c["correct"] for c in row["pool"]) for row in rows)}
    for k in (16, 64):
        if min(sizes) >= k:
            out[f"vote{k}"] = 100 * statistics.fmean(_select(row["pool"][:k], weights) for row in rows)
    return out


def _fmt(value) -> str:
    return "" if value is None else f"{value:.2f}"


def report(results: Path, only: set | None) -> str:
    weights = load_config()["ranking"]
    lines = []
    for bench, title, paper_cols in [
        ("bird", "BIRD dev (bài báo Bảng 2: 64 mẫu + CSC; metric set)", ["Bài báo (64 + CSC)"]),
        ("spider", "Spider dev (bài báo Bảng 3, Dev EX: 16 mẫu; metric spider)", ["Bài báo SC", "Bài báo CSC"]),
    ]:
        head = ["Model", "Train", "Run", "Số câu", "Mẫu/câu", "Vote@16", "Vote@64", "Oracle", "TB 1 mẫu",
                *paper_cols, "Δ Vote − bài báo"]
        lines += [f"## {title}", "", "| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
        for b, run, model, train, paper_sc, paper_csc in RUNS:
            if b != bench or (only and run not in only):
                continue
            paper = [paper_csc] if bench == "bird" else [paper_sc, paper_csc]
            rows = load(results / run, METRIC[bench]) if run and pool_files(results / run) else []
            if not rows:
                status = "chưa công bố" if run is None else "chưa chạy"
                lines.append("| " + " | ".join([model, train, run or "-", status, "", "", "", "", "",
                                                *map(_fmt, paper), ""]) + " |")
                continue
            s = score(rows, weights)
            vote = s.get("vote64", s.get("vote16")) if bench == "bird" else s.get("vote16")
            target = paper[0] if bench == "bird" else paper_sc
            n = f"{s['questions']}/{TOTAL[bench]}"
            lines.append("| " + " | ".join([
                model, train, run, n, str(s["samples"]), _fmt(s.get("vote16")), _fmt(s.get("vote64")),
                _fmt(s["oracle"]), _fmt(s["sample_acc"]), *map(_fmt, paper),
                f"{vote - target:+.2f}" if vote is not None and target is not None else ""]) + " |")
        lines.append("")
    lines += ["Ghi chú:",
              "- Vote@K: bỏ phiếu (self-consistency) trên K mẫu đầu của mỗi câu; ứng với cột SC của bài báo.",
              "- BIRD: bài báo chỉ công bố cấu hình đầy đủ 64 mẫu + CSC (merge revision), nên Vote@64 thường "
              "thấp hơn vài điểm; CAV-3 tính bằng `evaluation.selection_study`.",
              "- Δ: BIRD so Vote@64 (hoặc @16 nếu pool chỉ có 16) với 64 + CSC; Spider so Vote@16 với SC.",
              "- Số câu < tổng: run chưa xong (LIMIT hoặc hết 12 giờ Kaggle), chưa so được."]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--results", type=Path, default=ROOT / "results", help="Folder holding the run folders")
    parser.add_argument("--runs", nargs="+", help="Only these run folder names")
    parser.add_argument("--write-pool", action="store_true", help="Join shards into <run>/pool.jsonl")
    parser.add_argument("--combine", type=Path, nargs="+", help="Only join the shards of these run folders")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "paper-compare")
    args = parser.parse_args()
    if args.combine:
        for run in args.combine:
            combine(run)
        return
    if args.write_pool:
        for _, run, *_ in RUNS:
            if run and (args.results / run).is_dir() and not (args.results / run / "pool.jsonl").exists():
                combine(args.results / run)
    text = report(args.results, set(args.runs) if args.runs else None)
    print(text)
    if args.output:
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "tables.md").write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
