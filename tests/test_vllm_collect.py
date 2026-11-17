import json
from argparse import Namespace
import sys
from types import ModuleType, SimpleNamespace

import pytest

from evaluation.run_sweep import _read_pool
from evaluation.vllm_collect import collect
from tests.test_paper_mode import _db_info

ANSWERS = ["<think>x</think>\n<answer>```sql\nSELECT COUNT(*) FROM students\n```</answer>",
           "<answer>SELECT COUNT(*) FROM classes</answer>", "no sql here"]


class _Tokenizer:
    def apply_chat_template(self, messages, tokenize, add_generation_prompt):
        return "\n".join(m["content"] for m in messages)

    def __call__(self, text, add_special_tokens):
        return {"input_ids": text.split()}


class _LLM:
    calls = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get_tokenizer(self):
        return _Tokenizer()

    def generate(self, prompts, params, use_tqdm):
        _LLM.calls.append([p.kwargs["seed"] for p in params])
        return [SimpleNamespace(outputs=[SimpleNamespace(text=ANSWERS[i % 3]) for i in range(p.kwargs["n"])])
                for p in params]


def _fake_vllm(monkeypatch):
    module = ModuleType("vllm")
    module.LLM = _LLM
    module.SamplingParams = lambda **kwargs: SimpleNamespace(kwargs=kwargs)
    monkeypatch.setitem(sys.modules, "vllm", module)


def _dataset(tmp_path, db, count=3):
    (tmp_path / "tables.json").write_text(json.dumps([dict(_db_info(db), db_id="students")]), encoding="utf-8")
    items = [{"id": f"q{i}", "db_id": "students", "db_path": "students.sqlite", "tables_path": "tables.json",
              "question": "How many students?", "evidence": "", "gold_sql": "SELECT COUNT(*) FROM students",
              "difficulty": "simple"} for i in range(count)]
    dataset = tmp_path / "data.json"
    dataset.write_text(json.dumps(items), encoding="utf-8")
    return dataset


def _args(dataset, output, **overrides):
    return Namespace(**dict(dict(dataset=dataset, output=output, config=None, model="m", pool=4, limit=None,
                                 chunk=1, dtype="half", max_model_len=8192, gpu_memory=0.9, tensor_parallel=1,
                                 seed_offset=0, shard="0/1"), **overrides))


def test_vllm_pool_matches_run_sweep_format_and_resumes(tmp_path, db, monkeypatch):
    _fake_vllm(monkeypatch)
    args = _args(_dataset(tmp_path, db), tmp_path / "out", limit=2)
    _LLM.calls = []
    collect(args)
    rows = _read_pool(tmp_path / "out" / "pool.jsonl", metric="set")
    assert [r["id"] for r in rows] == ["q0", "q1"] and _LLM.calls == [[42], [43]]
    pool = rows[0]["pool"]
    assert len(pool) == 4 and [r["correct"] for r in pool] == [True, False, False, True]
    assert pool[2]["error"] and not pool[2]["success"]
    args.limit = None
    collect(args)  # resumes: only q2 is sampled
    assert _LLM.calls[-1] == [44] and len(_read_pool(tmp_path / "out" / "pool.jsonl")) == 3


def test_extra_samples_use_offset_seeds_per_shard_and_merge(tmp_path, db, monkeypatch):
    from scripts.merge_pools import merge

    _fake_vllm(monkeypatch)
    dataset = _dataset(tmp_path, db, count=5)
    _LLM.calls = []
    collect(_args(dataset, tmp_path / "base", chunk=5))
    for shard in (0, 1):
        collect(_args(dataset, tmp_path / f"shard{shard}", pool=12, chunk=5, seed_offset=100000,
                      shard=f"{shard}/2"))
    assert _LLM.calls == [[42, 43, 44, 45, 46], [100042, 100044, 100046], [100043, 100045]]
    shards = [_read_pool(tmp_path / f"shard{s}" / "pool.jsonl") for s in (0, 1)]
    assert [r["id"] for r in shards[0]] == ["q0", "q2", "q4"] and [r["id"] for r in shards[1]] == ["q1", "q3"]
    base = _read_pool(tmp_path / "base" / "pool.jsonl")
    merged = merge(base, shards[0] + shards[1])
    assert [r["id"] for r in merged] == [r["id"] for r in base]
    assert all(len(r["pool"]) == 16 for r in merged)
    assert merged[1]["pool"][:4] == base[1]["pool"] and merged[1]["pool"][4:] == shards[1][0]["pool"]
    assert len(merged[0]["batch_ms"]) == 2 and merged[0]["batch_size"] == 4
    with pytest.raises(ValueError, match="no extra samples"):
        merge(base, shards[0])


def test_calls_are_packed_under_the_kv_budget_and_preempted_calls_are_redone(tmp_path, db, monkeypatch):
    class _Small(_LLM):
        """KV cache for about two questions; vLLM preempts whenever a call holds more than one."""
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.scheduler = SimpleNamespace(num_cumulative_preemption=0)
            self.llm_engine = SimpleNamespace(scheduler=[self.scheduler],
                                              cache_config=SimpleNamespace(num_gpu_blocks=700, block_size=16))

        def generate(self, prompts, params, use_tqdm):
            self.scheduler.num_cumulative_preemption += len(prompts) > 1
            return super().generate(prompts, params, use_tqdm)

    _fake_vllm(monkeypatch)
    monkeypatch.setattr(sys.modules["vllm"], "LLM", _Small)
    _LLM.calls = []
    collect(_args(_dataset(tmp_path, db, count=5), tmp_path / "out", chunk=5))
    # Budget 10080 tokens, 4 x 1024 new tokens per question: two questions per call, each call redone singly.
    assert _LLM.calls == [[42, 43], [42], [43], [44, 45], [44], [45], [46]]
    rows = _read_pool(tmp_path / "out" / "pool.jsonl")
    assert [r["id"] for r in rows] == [f"q{i}" for i in range(5)] and all(len(r["pool"]) == 4 for r in rows)


def test_keep_schema_prunes_the_prompt(tmp_path, db, monkeypatch):
    seen = []

    class _Recording(_LLM):
        def generate(self, prompts, params, use_tqdm):
            seen.extend(prompts)
            return super().generate(prompts, params, use_tqdm)

    _fake_vllm(monkeypatch)
    monkeypatch.setattr(sys.modules["vllm"], "LLM", _Recording)
    keep = tmp_path / "keep.json"
    keep.write_text(json.dumps({"q0": [["students", "id"], ["students", "full_name"]]}), encoding="utf-8")
    collect(_args(_dataset(tmp_path, db, count=2), tmp_path / "out", chunk=2, keep_schema=keep))
    assert "CREATE TABLE classes" not in seen[0] and "CREATE TABLE students" in seen[0]
    assert "CREATE TABLE classes" in seen[1]  # q1 is not in the file: full schema
