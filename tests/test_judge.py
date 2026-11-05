from collections import Counter
import importlib.util
from pathlib import Path

from core.config import ROOT
from evaluation.judge import base_prompt, clusters, pair_key, preference, schema_for
from evaluation.selection_study import _judged

_spec = importlib.util.spec_from_file_location("import_bird", ROOT / "scripts" / "import_bird.py")
import_bird = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(import_bird)


def _record(result, correct, sql="SELECT 1"):
    return {"sql": sql, "error": None, "success": True, "result": result, "schema_score": 1.0,
            "warnings": 0, "correct": correct}


def test_stratified_sample_keeps_proportions_order_and_seed():
    items = [{"question_id": i, "difficulty": level}
             for i, level in enumerate(["simple"] * 60 + ["moderate"] * 30 + ["challenging"] * 10)]
    sample = import_bird.stratified(items, 20, seed=1)
    assert Counter(i["difficulty"] for i in sample) == {"simple": 12, "moderate": 6, "challenging": 2}
    ids = [i["question_id"] for i in sample]
    assert ids == sorted(ids)
    assert sample == import_bird.stratified(items, 20, seed=1)


def test_preference_is_symmetric_in_pair_order():
    judgments = {"q": {pair_key("b", "a"): 0.8}}  # first hash "a" is right with p = 0.8
    assert preference(judgments, "q", winner="b", challenger="a") == 0.8
    assert abs(preference(judgments, "q", winner="a", challenger="b") - 0.2) < 1e-9
    assert preference(judgments, "q", winner="a", challenger="c") is None


def test_judge_overturns_vote_only_above_margin(config):
    records = [_record("big", False)] * 5 + [_record("small", True)] * 2 + [_record("lone", False)]
    ids, weights = ["q"], config["ranking"]
    assert clusters(records, 2)[1][0]["result"] == "small"
    assert _judged(records, 0, ids, weights, {"q": {pair_key("big", "small"): 0.25}}, margin=0.1)
    assert not _judged(records, 0, ids, weights, {"q": {pair_key("big", "small"): 0.45}}, margin=0.1)
    assert not _judged(records, 0, ids, weights, {}, margin=0.1)


def test_judge_prompts_use_only_tables_in_queries(db):
    schema = schema_for(db, ["SELECT full_name FROM students"])
    assert "CREATE TABLE students" in schema and "CREATE TABLE departments" not in schema
    prompt = base_prompt({"db": str(db), "question": "Q?"}, {}, "")
    assert "CREATE TABLE departments" in prompt and "\n\nInstructions:" in prompt


def test_judge_after_cav_can_overturn_with_single_rival(config):
    records = [_record("big", False)] * 3 + [_record("lone", True)]
    ids, weights, judgments = ["q"], config["ranking"], {"q": {pair_key("big", "lone"): 0.0}}
    assert not _judged(records, 0, ids, weights, judgments, margin=0.1)  # default needs a rival of >= 2
    assert _judged(records, 0, ids, weights, judgments, margin=0.1, min_rival=1)
