"""Progress, ETA and running self-consistency EX of a run_sweep collection (safe while it runs).

collect rewrites <output>/progress.txt with the same report after every question.
"""
import argparse
from collections import Counter
from datetime import datetime, timedelta
import json
from pathlib import Path
import statistics

from core.config import load_config
from evaluation.run_sweep import _read_pool, _select


def report(output: Path, total: int) -> str:
    rows = _read_pool(output / "pool.jsonl")
    if not rows:
        return f"0/{total} câu xong."
    seconds = [(r["greedy_ms"] + sum(r["batch_ms"])) / 1000 for r in rows]
    recent = statistics.fmean(seconds[-20:])
    left = (total - len(rows)) * recent
    finish = datetime.now() + timedelta(seconds=left)
    sizes = [len(r["pool"]) for r in rows]
    lines = [f"Cập nhật: {datetime.now():%Y-%m-%d %H:%M}",
             f"Tiến độ: {len(rows)}/{total} câu ({len(rows) / total:.0%})",
             f"Thời gian: trung bình {statistics.fmean(seconds):.0f}s/câu, 20 câu gần nhất {recent:.0f}s/câu",
             f"Còn lại: khoảng {left / 3600:.1f} giờ (xong khoảng {finish:%Y-%m-%d %H:%M})",
             f"Số mẫu/câu: trung bình {statistics.fmean(sizes):.1f}; "
             + ", ".join(f"{k} mẫu: {n} câu" for k, n in sorted(Counter(sizes).items())), ""]
    weights = load_config()["ranking"]
    for metric, label in [("set", "BIRD EX (set)"), ("spider", "Spider EX"), ("strict", "EX strict")]:
        if metric != "strict" and f"correct_{metric}" not in rows[0]["pool"][0]:
            continue
        scored = _read_pool(output / "pool.jsonl", metric=metric)
        vote = statistics.fmean(_select(r["pool"], weights) for r in scored)
        oracle = statistics.fmean(any(c["correct"] for c in r["pool"]) for r in scored)
        lines.append(f"{label:<14} bỏ phiếu = {vote:.1%}   oracle (có ít nhất 1 mẫu đúng) = {oracle:.1%}")
    lines += ["", "Từng câu (mới nhất trước): câu | độ khó | mẫu đúng/số mẫu | dừng | thời gian"]
    for r, s in reversed(list(zip(rows, seconds))):
        correct = sum(c.get("correct_set", c["correct"]) for c in r["pool"])
        lines.append(f"{r['id']:<10} {r.get('difficulty') or '':<12} {correct:>2}/{len(r['pool']):<2} "
                     f"{r.get('stop', 'pool'):<10} {s:>5.0f}s")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="run_sweep --output directory")
    parser.add_argument("--dataset", type=Path, required=True)
    args = parser.parse_args()
    total = len(json.loads(args.dataset.read_text(encoding="utf-8")))
    print(report(args.output, total))


if __name__ == "__main__":
    main()
