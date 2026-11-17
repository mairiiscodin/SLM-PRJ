"""Sample the paper-setting candidate pool with vLLM (Kaggle/Colab GPU) in run_sweep's pool.jsonl format.

Same prompt, sampling, SQL extraction, validation, execution and gold labels as
`run_sweep collect --prompt paper --skip-greedy`, but vLLM batches many questions at once and
shares the prompt KV cache across the samples of one question (as the SLM-SQL/CSC-SQL code does),
so 16 samples take seconds instead of minutes. Database paths are stored relative to the project
root, so judge / selection_study run on the downloaded pool from the project root on any machine.

    python -m evaluation.vllm_collect --dataset data/benchmarks/bird_dev.json --output results/bird-dev-vllm

More samples for the same questions (e.g. 48 on top of 16, as the paper's 64): draw them with
--seed-offset so they differ from the first pool, split the questions over GPUs with --shard i/n
(one process per GPU), then join the pools with scripts/merge_pools.py.
"""
import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import time

from core.config import ROOT, load_config
from core.omnisql_prompt import build_paper_prompt
from core.pipeline import Pipeline
from core.sql_executor import SQLExecutor
from core.sql_extractor import extract_sql
from core.types import Candidate
from evaluation.run_sweep import PAPER_EXECUTION, PAPER_SAMPLING, _read_pool, _record


def _portable(path: str) -> str:
    """Dataset paths written on Windows use backslashes; Linux needs forward slashes."""
    return path.replace("\\", "/")


def _relative(path: Path) -> str:
    # abspath, not resolve: on Kaggle data/external is a symlink into the read-only input.
    try:
        return Path(os.path.abspath(path)).relative_to(ROOT).as_posix()
    except ValueError:
        return os.path.abspath(path)


def _candidates(output, start_ms: float) -> list:
    completions = getattr(output, "outputs", output)  # a vLLM RequestOutput, or its completions
    out = []
    for index, completion in enumerate(completions):
        candidate = Candidate(index, raw_text=completion.text, generation_ms=start_ms)
        try:
            candidate.sql = extract_sql(completion.text)
        except ValueError as error:
            candidate.error = str(error)
        out.append(candidate)
    return out


def _kv_tokens(llm) -> int | None:
    """Tokens the KV cache can hold (vLLM V0 engine), or None when it cannot be read."""
    try:
        cache = llm.llm_engine.cache_config
        return int(cache.num_gpu_blocks) * int(cache.block_size)
    except (AttributeError, TypeError):
        return None


def _preemptions(llm) -> int | None:
    try:
        return sum(int(s.num_cumulative_preemption) for s in llm.llm_engine.scheduler)
    except (AttributeError, TypeError):
        return None


def _generate(llm, make_params, requests: list, budget: int | None, max_new: int) -> list:
    """Completions per request, never keeping results of a call in which vLLM preempted a sequence.

    requests: (prompt text, prompt tokens, n, seed). A model with many KV heads (deepseek-coder
    based SLM-SQL-1.3B: 16, against 2 for Qwen2.5-Coder) fills the KV cache with a few questions;
    vLLM then preempts and recomputes sequences, and on Kaggle about 30% of those samples came
    back without SQL. So the requests are packed under the KV budget, and a call that was
    preempted anyway is split in two and redone (a single question: its n samples are split).
    """
    def cost(request):
        return request[1] + request[2] * max_new  # the prompt is shared by the samples (prefix cache)

    def halves(request):
        text, tokens, n, seed = request
        return [(text, tokens, n // 2, seed), (text, tokens, n - n // 2, seed + 10_000_019 * (n // 2))]

    def run(batch):
        if budget and len(batch) == 1 and batch[0][2] > 1 and cost(batch[0]) > budget:
            first, second = halves(batch[0])
            return [run([first])[0] + run([second])[0]]
        before = _preemptions(llm)
        outputs = llm.generate([r[0] for r in batch], [make_params(r[2], r[3]) for r in batch], use_tqdm=False)
        after = _preemptions(llm)
        if before is not None and after is not None and after > before:
            if len(batch) > 1:
                middle = len(batch) // 2
                print(f"  preempted ({after - before}): redoing {len(batch)} questions as two calls", flush=True)
                return run(batch[:middle]) + run(batch[middle:])
            if batch[0][2] > 1:
                print(f"  preempted ({after - before}): redoing 1 question as two sample groups", flush=True)
                first, second = halves(batch[0])
                return [run([first])[0] + run([second])[0]]
        return [list(output.outputs) for output in outputs]

    results, batch, used = [], [], 0
    for request in requests:
        if batch and budget and used + cost(request) > budget:
            results += run(batch)
            batch, used = [], 0
        batch.append(request)
        used += cost(request)
    return results + (run(batch) if batch else [])


def collect(args):
    from vllm import LLM, SamplingParams

    config = deepcopy(load_config(args.config))
    config["generation"].update(PAPER_SAMPLING)
    if getattr(args, "temperature", None) is not None:
        config["generation"]["temperature"] = args.temperature
    config["execution"].update(PAPER_EXECUTION)
    config["correction"]["enabled"] = False
    generation = config["generation"]
    items = json.loads(args.dataset.read_text(encoding="utf-8"))[: args.limit]
    out = args.output / "pool.jsonl"
    done = {row["id"] for row in _read_pool(out, repair=True)} if out.exists() else set()
    shard, shards = map(int, args.shard.split("/"))
    todo = [item for index, item in enumerate(items) if item["id"] not in done and index % shards == shard]
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "config.json").write_text(json.dumps(
        dict(config, sweep={k: str(v) for k, v in vars(args).items()}, backend="vllm"), indent=2), encoding="utf-8")
    print(f"{len(done)} done, {len(todo)} to sample", flush=True)
    if not todo:
        return

    llm = LLM(model=args.model, dtype=args.dtype, seed=config["seed"], max_model_len=args.max_model_len,
              gpu_memory_utilization=args.gpu_memory, tensor_parallel_size=args.tensor_parallel,
              enable_prefix_caching=True)
    tokenizer = llm.get_tokenizer()
    kv_tokens = _kv_tokens(llm)
    budget = int(kv_tokens * getattr(args, "kv_budget", 0.9)) if kv_tokens else None
    print(f"KV cache: {kv_tokens} tokens, budget per vLLM call: {budget}", flush=True)

    def make_params(n, seed):
        return SamplingParams(n=n, temperature=generation["temperature"], top_p=generation["top_p"],
                              max_tokens=generation["max_new_tokens"], seed=seed)

    # Only the validator and executor are used; a placeholder backend keeps a second model off the GPU.
    pipeline = Pipeline(config, backend=object())
    executor = SQLExecutor(config["execution"])

    keep_path = getattr(args, "keep_schema", None)
    schema_keep = json.loads(keep_path.read_text(encoding="utf-8")) if keep_path else {}
    for start in range(0, len(todo), args.chunk):
        chunk = todo[start: start + args.chunk]
        prompts, keep, skipped = [], [], []
        for item in chunk:
            database = Path(os.path.abspath(args.dataset.parent / _portable(item["db_path"])))
            tables = args.dataset.parent / _portable(item["tables_path"])
            prompt = build_paper_prompt(item["question"], database, item["db_id"], tables, item.get("evidence", ""),
                                        retrieval=getattr(args, "retrieval", "paper"), keep=schema_keep.get(item["id"]))
            text = tokenizer.apply_chat_template(
                [{"role": "system", "content": generation["system_prompt"]}, {"role": "user", "content": prompt}],
                tokenize=False, add_generation_prompt=True)
            tokens = len(tokenizer(text, add_special_tokens=False)["input_ids"])
            if tokens > generation["max_input_tokens"]:
                skipped.append((item, database))
                continue
            prompts.append((text, tokens, args.pool, config["seed"] + args.seed_offset + items.index(item)))
            keep.append((item, database))
        # One seed per question: reruns and resumed runs draw the same samples.
        began = time.perf_counter()
        outputs = _generate(llm, make_params, prompts, budget, generation["max_new_tokens"]) if prompts else []
        per_question_ms = (time.perf_counter() - began) * 1000 / max(1, len(prompts))
        results = [(item, database, _candidates(o, per_question_ms / args.pool))
                   for (item, database), o in zip(keep, outputs)]
        results += [(item, database, [Candidate(0, error="Prompt vượt context; giảm row samples hoặc chọn schema.")])
                    for item, database in skipped]
        with out.open("a", encoding="utf-8") as handle:
            for item, database, pool in results:
                gold = executor.execute(database, item["gold_sql"])
                for candidate in pool:
                    pipeline._check(candidate, database)
                row = {"id": item["id"], "difficulty": item.get("difficulty"), "question": item["question"],
                       "evidence": item.get("evidence", ""), "db": _relative(database),
                       "gold_sql": item["gold_sql"], "greedy_ms": 0.0, "batch_ms": [per_question_ms],
                       "batch_size": args.pool, "stop": "pool", "greedy": None,
                       "pool": [_record(c, gold, item["gold_sql"]) for c in pool]}
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        finished = len(done) + start + len(chunk)
        samples = [c for _, _, pool in results for c in pool]
        print(f"[{finished}/{len(done) + len(todo)}] chunk of {len(chunk)} in {per_question_ms * len(prompts) / 1000:.0f}s "
              f"({per_question_ms / 1000:.1f}s/question), {sum(not c.sql for c in samples)}/{len(samples)} samples "
              f"without SQL", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--model", default="cycloneboy/SLM-SQL-1.5B")
    parser.add_argument("--pool", type=int, default=16)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--chunk", type=int, default=64, help="Questions per vLLM call (saved after each)")
    parser.add_argument("--dtype", default="half", help="half on T4/P100 (no bfloat16); bfloat16 on A100/L4")
    parser.add_argument("--max-model-len", type=int, default=8192)
    parser.add_argument("--gpu-memory", type=float, default=0.90)
    parser.add_argument("--tensor-parallel", type=int, default=1)
    parser.add_argument("--seed-offset", type=int, default=0,
                        help="Added to every question's seed: 100000 draws samples disjoint from a first run")
    parser.add_argument("--shard", default="0/1", help="i/n: only questions whose index %% n == i (one GPU each)")
    parser.add_argument("--temperature", type=float, help="Sampling temperature (default: the paper's 0.8)")
    parser.add_argument("--keep-schema", type=Path,
                        help="evaluation.schema_keep output: per question, only these columns are shown")
    parser.add_argument("--kv-budget", type=float, default=0.9,
                        help="Fraction of the KV cache one vLLM call may need (prompt + pool x max new tokens)")
    parser.add_argument("--retrieval", choices=["paper", "new"], default="paper",
                        help="Question-matched example values: paper (CSC-SQL style) or new (core/value_retrieval.py)")
    collect(parser.parse_args())


if __name__ == "__main__":
    main()
