from argparse import Namespace
import json

from core.config import load_config
from core.omnisql_prompt import TEMPLATE
from evaluation.merge_study import load_merge, overrule
from evaluation.vllm_merge import keep_tables, merge_prompt, result_text, run, top_pair
from tests.test_vllm_collect import _LLM, _dataset, _fake_vllm


def _record(result, correct=False, sql="SELECT 1"):
    return {"sql": sql, "error": None, "success": True, "result": result, "schema_score": 1.0, "warnings": 0,
            "correct": correct}


def _pair(key="k"):
    return {"key": key, "id": "q0", "winner": "w", "rival": "r", "sources": {"cav": [6, 3]},
            "sql1": "SELECT COUNT(*) FROM students", "res1": "[(3,)]",
            "sql2": "SELECT COUNT(*) FROM classes", "res2": "[(2,)]"}


def test_result_text_follows_csc_limits():
    assert result_text([[1, "a"]], 1) == "[(1, 'a')]"
    assert result_text([], 0) == "[]"
    long = result_text([[i] for i in range(21)], 30)
    assert long.startswith("The execution results of the first twenty columns are: [(0,), (1,)") and "(20,)" not in long
    assert len(result_text([["x" * 2000]], 1)) == 1003


def test_merge_prompt_has_both_drafts_and_only_their_tables():
    schema = "\nCREATE TABLE students (\n id INT\n);\nCREATE TABLE `classes` (\n id INT\n);\nCREATE TABLE other (\n id INT\n);\n"
    prompt = merge_prompt(TEMPLATE.format(db_details=schema, question="Q"), _pair())
    assert "some draft SQL and its corresponding execution result" in prompt
    assert "1. SELECT COUNT(*) FROM students\n【Execution result】\n[(3,)]\n" in prompt
    assert "2. SELECT COUNT(*) FROM classes\n【Execution result】\n[(2,)]\n" in prompt
    assert prompt.index("draft SQL and execute result") < prompt.index("Instructions:")
    assert "CREATE TABLE students" in prompt and "CREATE TABLE `classes`" in prompt
    assert "CREATE TABLE other" not in prompt


def test_keep_tables_leaves_prompt_when_no_table_matches():
    prompt = TEMPLATE.format(db_details="\nCREATE TABLE a_table (\n id INT\n);\n", question="Q")
    assert keep_tables(prompt, ["SELECT 1"]) == prompt


def test_top_pair_needs_a_rival():
    weights = load_config(None)["ranking"]
    records = [_record("a"), _record("a"), _record("a"), _record("b", sql="SELECT 2"), _record("b", sql="SELECT 2"),
               _record("c", sql="SELECT 3")]
    winner, rival, votes = top_pair(records, weights)
    assert (winner["result"], rival["result"], votes) == ("a", "b", [3, 2])
    assert top_pair(records[:3], weights) is None


def _merge_row(*draws):
    return {"winner": "w", "rival": "r", "sources": {"cav": [6, 3]},
            "draws": [dict(_record(h, correct=c)) for h, c in draws]}


def test_overrule_modes_and_gate():
    pool = [_record("w", correct=False), _record("r", correct=True)]
    rival_wins = _merge_row(("r", True), ("r", True), ("w", False))
    new_query = _merge_row(("n", True), ("n", True), ("w", False))
    assert overrule(rival_wins, False, "pick", 0.0, "cav", pool) is True
    assert overrule(rival_wins, False, "free", 0.0, "cav", pool) is True
    assert overrule(new_query, False, "free", 0.0, "cav", pool) is True
    assert overrule(new_query, False, "pick", 0.0, "cav", pool) is False  # neither side gets a draw more
    assert overrule(rival_wins, False, "pick", 0.75, "cav", pool) is False  # 3 < 0.75 * 6: not asked
    assert overrule(None, True, "free", 0.0, "cav", pool) is True
    assert overrule(_merge_row(("w", False), ("r", True)), False, "free", 0.0, "cav", pool) is False  # tie keeps base


def test_run_samples_pairs_per_shard_and_resumes(tmp_path, db, monkeypatch):
    _fake_vllm(monkeypatch)
    dataset = _dataset(tmp_path, db)
    pairs = tmp_path / "pairs.jsonl"
    rows = [dict(_pair(f"k{i}"), id=f"q{i}") for i in range(3)]
    pairs.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    args = Namespace(dataset=dataset, pairs=pairs, output=tmp_path / "out", config=None, model="m", samples=4,
                     limit=None, chunk=2, dtype="half", max_model_len=8192, gpu_memory=0.9, shard="0/2")
    _LLM.calls = []
    run(args)
    assert _LLM.calls == [[42, 44]]
    run(args)  # finished shard: nothing to sample
    assert _LLM.calls == [[42, 44]]
    merged = load_merge([tmp_path / "out"])
    assert sorted(merged) == [("q0", "cav"), ("q2", "cav")]
    draws = merged[("q0", "cav")]["draws"]
    assert len(draws) == 4 and draws[0]["correct_set"] and not draws[2]["success"]
