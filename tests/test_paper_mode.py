import json

from core.omnisql_prompt import TEMPLATE, _match_score, schema_details
from core.sql_executor import SQLExecutor
from evaluation.metrics import execution_match
from evaluation.run_sweep import _read_pool


def _db_info(db):
    tables = ["departments", "classes", "students"]
    columns = [(-1, "*"), (0, "id"), (0, "name"), (1, "id"), (1, "name"), (1, "department_id"),
               (2, "id"), (2, "full_name"), (2, "gender"), (2, "class_id")]
    return {"table_names_original": tables, "column_names_original": [list(c) for c in columns],
            "column_names": [[t, n.replace("_", " ")] for t, n in columns],
            "column_types": ["text"] + ["number", "text"] * 2 + ["number", "number", "text", "text", "number"],
            "primary_keys": [1, 3, 6], "foreign_keys": [[5, 1], [9, 3]]}


def test_template_keeps_paper_wording():
    prompt = TEMPLATE.format(db_details="DDL", question="Q")
    assert prompt.startswith("You first thinks about the reasoning process")
    assert "</answer>.  \n\nLet me solve this step by step." in prompt
    assert prompt.endswith("Let me solve this step by step.")


def test_schema_has_keys_and_question_matched_values(db):
    details = schema_details(db, _db_info(db), "Liệt kê sinh viên giới tính Nữ")
    assert "CREATE TABLE students (" in details
    assert "PRIMARY KEY (id)" in details
    assert "FOREIGN KEY (class_id) REFERENCES classes (id)" in details
    assert "'Nữ'" in details.split("CREATE TABLE students")[1]
    assert _match_score("Nữ", "giới tính Nữ") == 1.0


def test_set_metric_ignores_duplicates_and_order(db, config):
    executor = SQLExecutor(config["execution"])
    gold = executor.execute(db, "SELECT DISTINCT gender FROM students ORDER BY gender")
    duplicated = executor.execute(db, "SELECT gender FROM students")
    assert execution_match(duplicated, gold, "SELECT DISTINCT gender FROM students ORDER BY gender", mode="set")
    assert not execution_match(duplicated, gold, "SELECT DISTINCT gender FROM students ORDER BY gender")


def test_spider_metric_allows_column_permutation(db, config):
    config["execution"]["max_rows"] = 50000
    executor = SQLExecutor(config["execution"])
    gold_sql = "SELECT gender, full_name FROM students ORDER BY id"
    gold = executor.execute(db, gold_sql)
    swapped = executor.execute(db, "SELECT full_name, gender FROM students ORDER BY id")
    reversed_order = executor.execute(db, "SELECT gender, full_name FROM students ORDER BY id DESC")
    assert execution_match(swapped, gold, gold_sql, mode="spider")
    assert not execution_match(swapped, gold, gold_sql, mode="set")
    assert not execution_match(reversed_order, gold, gold_sql, mode="spider")


def test_pool_reader_drops_line_cut_by_power_loss(tmp_path):
    path = tmp_path / "pool.jsonl"
    row = {"id": "q1", "greedy": None, "pool": [{"correct": False, "correct_set": True}]}
    path.write_text(json.dumps(row) + "\n" + '{"id": "q2", "pool": [', encoding="utf-8")
    rows = _read_pool(path, repair=True, metric="set")
    assert [r["id"] for r in rows] == ["q1"] and rows[0]["pool"][0]["correct"]
    assert path.read_text(encoding="utf-8").count("\n") == 1


def test_schedule_targets_are_cumulative_and_capped():
    from argparse import Namespace
    from evaluation.run_sweep import _targets
    assert _targets(Namespace(schedule="4-4-8", pool=16)) == [4, 8, 16]
    assert _targets(Namespace(schedule="4-4-8-16", pool=16)) == [4, 8, 16, 16]
    assert _targets(Namespace(schedule=None, pool=16)) == [16]
