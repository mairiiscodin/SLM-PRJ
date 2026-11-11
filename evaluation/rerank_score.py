"""Coder-Reviewer re-ranking of the clusters left after CAV-3, scored by the generation model itself.

`score` (GPU): for every question whose CAV-3 survivors split into >= 2 result clusters, the top
--top clusters (by size) get two teacher-forced log-likelihoods from the SLM, no sampling:
  coder    log p(SQL | paper prompt)        the SQL as the model's own <answer>, after an empty <think>
  reviewer log p(question | schema, SQL)    how well the SQL explains the question (same schema text
                                            for every cluster of a question, so sums are comparable)
The paper prompt is encoded once per question and its KV cache is reused for every cluster.
Results go to a resumable JSONL (one line per question).

`study` (CPU): replays CAV-3 and the re-ranked choice on the same clusters and reports EX,
rescued / lost questions against CAV-3 and an exact McNemar p for a small grid of fixed rules.
Pick the rule on bird_dev200 and only then look at the held-out questions (--exclude).
"""
import argparse
import json
import math
import os
from pathlib import Path
import time

from core.config import load_config
from core.consistency_checks import CHECKS
from evaluation.judge import base_prompt, schema_for
from evaluation.run_sweep import PAPER_SAMPLING, _candidates, _read_pool
from evaluation.selection_study import _clean, enrich
from core.candidate_ranker import rank_candidates
from core.result_grouper import group_candidates

THINK = "<think>\nI write the SQL query for the question.\n</think>\n<answer>\n```sql\n"
REVIEW_PROMPT = """Database schema:
{schema}

SQLite query:
{sql}

Write the natural-language question that this SQL query answers."""
REVIEW_PREFILL = "<think>\nI read the query and state its question.\n</think>\n<answer>\n"


def cav_clusters(row, weights):
    """CAV-3 survivors grouped by result (largest first) and the result hash CAV-3 selects."""
    clean = _clean(row["pool"], CHECKS)
    if not clean:
        return [], None
    candidates = _candidates(clean)
    group_candidates(candidates)
    chosen = rank_candidates(candidates, weights)
    groups = {}
    for record in clean:
        groups.setdefault(record["result"], []).append(record)
    ranked = sorted(groups.values(), key=len, reverse=True)
    return ranked, clean[chosen.id]["result"] if chosen else None


def load_rows(args, config):
    rows = _read_pool(args.pool_dir / "pool.jsonl", metric="set")
    ids = None
    if args.subset:
        ids = {i["id"] for i in json.loads(args.subset.read_text(encoding="utf-8"))}
        rows = [r for r in rows if r["id"] in ids]
    if args.exclude:
        skip = {i["id"] for i in json.loads(args.exclude.read_text(encoding="utf-8"))}
        rows = [r for r in rows if r["id"] not in skip]
    enrich(rows, None, config, args.pool_dir / "candidate_flags.json")
    return rows


class Scorer:
    def __init__(self, config):
        from core.model_backend import create_backend
        self.backend = create_backend(config)
        self.torch = self.backend.torch
        self.tok, self.model = self.backend.tokenizer, self.backend.model
        self.system = config["generation"]["system_prompt"]

    def _chat(self, user):
        return self.tok.apply_chat_template([{"role": "system", "content": self.system},
                                             {"role": "user", "content": user}],
                                            tokenize=False, add_generation_prompt=True)

    def _ids(self, text):
        return self.tok(text, return_tensors="pt", add_special_tokens=False)["input_ids"].to(self.model.device)

    def _continuations(self, prefix, texts):
        """Sum of log p(text | prefix) and token count for each text, one prefix forward pass."""
        torch = self.torch
        prefix_ids = self._ids(prefix)
        length = prefix_ids.shape[1]
        with torch.inference_mode():
            out = self.model(prefix_ids, use_cache=True, logits_to_keep=1)
            cache, first = out.past_key_values, out.logits[0, -1].float()
            scores = []
            for text in texts:
                ids = self._ids(text)
                logits = self.model(ids, past_key_values=cache, use_cache=True).logits[0].float()
                logits = torch.cat([first[None], logits[:-1]], 0)
                logp = torch.log_softmax(logits, -1).gather(1, ids[0][:, None]).sum().item()
                scores.append((logp, ids.shape[1]))
                cache.crop(length)
                del logits
        return scores

    def coder(self, prompt, sqls):
        return self._continuations(self._chat(prompt) + THINK, [s.strip() + "\n```\n</answer>" for s in sqls])

    def reviewer(self, schema, sqls, question):
        out = []
        for sql in sqls:
            prefix = self._chat(REVIEW_PROMPT.format(schema=schema, sql=sql.strip())) + REVIEW_PREFILL
            out.extend(self._continuations(prefix, [question.strip()]))
        return out


def score(args):
    config = load_config(args.config)
    saved = json.loads((args.pool_dir / "config.json").read_text(encoding="utf-8"))
    config["execution"], config["generation"] = saved["execution"], dict(saved["generation"])
    config["generation"].setdefault("system_prompt", PAPER_SAMPLING["system_prompt"])
    config["model"]["model_id"] = args.model or saved["model"]["model_id"]
    config["model"]["local_files_only"] = True
    rows = load_rows(args, config)
    dataset = json.loads(args.dataset.read_text(encoding="utf-8"))
    items = {i["id"]: dict(i, tables_path=str((args.dataset.parent / i["tables_path"]).resolve()))
             for i in dataset}
    out = args.output
    done = {json.loads(l)["id"] for l in out.read_text(encoding="utf-8").splitlines() if l.strip()} \
        if out.exists() else set()
    scorer = None
    todo = [r for r in rows if r["id"] not in done]
    print(f"{len(rows)} questions, {len(done)} done, {len(todo)} to score", flush=True)
    with out.open("a", encoding="utf-8") as handle:
        for index, row in enumerate(todo, 1):
            start = time.perf_counter()
            groups, chosen = cav_clusters(row, config["ranking"])
            record = {"id": row["id"], "difficulty": row["difficulty"], "cav_result": chosen, "clusters": []}
            if len(groups) >= 2:
                scorer = scorer or Scorer(config)
                top = groups[: args.top]
                if chosen not in {g[0]["result"] for g in top}:
                    top = top[:-1] + [next(g for g in groups if g[0]["result"] == chosen)]
                sqls = [g[0]["sql"] for g in top]
                item = items[row["id"]]
                prompt = base_prompt(row, item, item.get("evidence", ""))
                coder = scorer.coder(prompt, sqls)
                schema = schema_for(Path(row["db"]), [g[0]["sql"] for g in groups[: args.top]])
                reviewer = scorer.reviewer(schema, sqls, row["question"])
                for g, (c, n), (r, m) in zip(top, coder, reviewer):
                    record["clusters"].append({
                        "result": g[0]["result"], "size": len(g), "correct": bool(g[0]["correct"]),
                        "coder": c, "coder_tokens": n, "reviewer": r, "question_tokens": m})
            record["survivors"] = sum(len(g) for g in groups)
            record["oracle"] = any(g[0]["correct"] for g in groups)
            record["cav_correct"] = any(g[0]["correct"] for g in groups if g[0]["result"] == chosen)
            record["ms"] = (time.perf_counter() - start) * 1000
            handle.write(json.dumps(record) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
            print(f"[{index}/{len(todo)}] {row['id']} clusters={len(record['clusters'])} "
                  f"{record['ms'] / 1000:.1f}s", flush=True)


def mcnemar(lost, rescued):
    n = lost + rescued
    if not n:
        return 1.0
    k = min(lost, rescued)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def choose(record, rule):
    """Result hash picked by a rule; CAV-3's pick when the rule does not override it."""
    clusters = record["clusters"]
    if len(clusters) < 2:
        return record["cav_result"]
    survivors = record["survivors"]
    base = next((c for c in clusters if c["result"] == record["cav_result"]), clusters[0])

    def value(c):
        coder = c["coder"] / c["coder_tokens"] if rule["coder_mean"] else c["coder"]
        return rule["vote"] * math.log(c["size"] / survivors) + rule["coder"] * coder + rule["reviewer"] * c["reviewer"]

    rivals = [c for c in clusters if c is not base and c["size"] >= rule["gate"] * base["size"]]
    if not rivals:
        return base["result"]
    best = max([base, *rivals], key=value)
    return best["result"] if value(best) - value(base) > rule["margin"] else base["result"]


def study(args):
    records = [json.loads(l) for l in args.scores.read_text(encoding="utf-8").splitlines() if l.strip()]
    if args.subset:
        ids = {i["id"] for i in json.loads(args.subset.read_text(encoding="utf-8"))}
        records = [r for r in records if r["id"] in ids]
    if args.exclude:
        skip = {i["id"] for i in json.loads(args.exclude.read_text(encoding="utf-8"))}
        records = [r for r in records if r["id"] not in skip]
    n = len(records)
    cav = sum(r["cav_correct"] for r in records)
    contested = [r for r in records if len(r["clusters"]) >= 2]
    print(f"{n} questions, CAV-3 {100 * cav / n:.2f}%, oracle {100 * sum(r['oracle'] for r in records) / n:.2f}%, "
          f"contested {len(contested)} (correct cluster scored in "
          f"{sum(any(c['correct'] for c in r['clusters']) for r in contested)}, CAV-3 right in "
          f"{sum(r['cav_correct'] for r in contested)})")

    # Oracle-free diagnostics: how often each signal alone ranks the correct cluster first.
    def top1(key):
        hits = [max(r["clusters"], key=key)["correct"] for r in contested if any(c["correct"] for c in r["clusters"])]
        return f"{sum(hits)}/{len(hits)}"
    print("signal alone picks the correct cluster (questions where one is scored):",
          "vote", top1(lambda c: c["size"]), "| coder sum", top1(lambda c: c["coder"]),
          "| coder mean", top1(lambda c: c["coder"] / c["coder_tokens"]), "| reviewer", top1(lambda c: c["reviewer"]))

    rules = []
    for coder_mean in (False, True):
        for vote in (0.0, 1.0, 2.0):
            for coder_w, reviewer_w in ((1, 0), (0, 1), (1, 1), (0.5, 1), (1, 0.5)):
                for gate in (0.0, 0.25, 0.5):
                    for margin in (0.0, 1.0):
                        rules.append(dict(coder_mean=coder_mean, vote=vote, coder=coder_w,
                                          reviewer=reviewer_w, gate=gate, margin=margin))
    table = []
    for rule in rules:
        rescued = lost = correct = 0
        for r in records:
            pick = choose(r, rule)
            ok = any(c["correct"] for c in r["clusters"] if c["result"] == pick) if r["clusters"] else r["cav_correct"]
            correct += ok
            rescued += ok and not r["cav_correct"]
            lost += r["cav_correct"] and not ok
        table.append((correct, rescued, lost, mcnemar(lost, rescued), rule))
    table.sort(key=lambda t: (-t[0], t[2]))
    print(f"\n{'EX %':>6} {'Δ':>6} {'cứu':>4} {'mất':>4} {'p':>6}  rule")
    for correct, rescued, lost, p, rule in table[: args.show]:
        print(f"{100 * correct / n:6.2f} {100 * (correct - cav) / n:+6.2f} {rescued:4d} {lost:4d} {p:6.3f}  {rule}")
    if args.rule:
        rule = json.loads(args.rule)
        row = next(t for t in table if t[4] == rule) if any(t[4] == rule for t in table) else None
        if row is None:
            rescued = lost = correct = 0
            for r in records:
                pick = choose(r, rule)
                ok = any(c["correct"] for c in r["clusters"] if c["result"] == pick) if r["clusters"] else r["cav_correct"]
                correct += ok; rescued += ok and not r["cav_correct"]; lost += r["cav_correct"] and not ok
            row = (correct, rescued, lost, mcnemar(lost, rescued), rule)
        print(f"\nfixed rule: EX {100 * row[0] / n:.2f} (Δ {100 * (row[0] - cav) / n:+.2f}), "
              f"rescued {row[1]}, lost {row[2]}, p {row[3]:.3f}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("score")
    s.add_argument("pool_dir", type=Path)
    s.add_argument("--dataset", type=Path, required=True, help="Dataset JSON with tables_path (paper prompt)")
    s.add_argument("--subset", type=Path, help="Only questions in this dataset JSON (e.g. bird_dev200.json)")
    s.add_argument("--exclude", type=Path, help="Skip questions in this dataset JSON")
    s.add_argument("--top", type=int, default=3, help="Clusters scored per question (CAV-3's pick always included)")
    s.add_argument("--model", help="Default: the pool's model")
    s.add_argument("--config", type=Path)
    s.add_argument("--output", type=Path, required=True)
    t = sub.add_parser("study")
    t.add_argument("scores", type=Path)
    t.add_argument("--subset", type=Path)
    t.add_argument("--exclude", type=Path)
    t.add_argument("--show", type=int, default=15)
    t.add_argument("--rule", help="JSON rule fixed in advance (held-out report)")
    args = parser.parse_args()
    score(args) if args.command == "score" else study(args)


if __name__ == "__main__":
    main()
