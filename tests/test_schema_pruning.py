import json

from core.omnisql_prompt import schema_details
from core.schema_pruning import kept_columns, sql_names
from evaluation.schema_keep import main
from tests.test_paper_mode import _db_info
from tests.test_vllm_collect import _dataset


def test_names_of_unparsable_sql():
    assert sql_names("SELECT FROM WHERE (") is None
    assert sql_names("SELECT s.Full_Name FROM Students AS s") == ({"students"}, {"full_name"})


def test_columns_mode_keeps_used_columns_and_keys(db):
    info = _db_info(db)
    kept = kept_columns(["SELECT full_name FROM students", "not sql ("], info)
    assert kept == [["students", "id"], ["students", "full_name"], ["students", "class_id"]]
    assert len(kept_columns(["SELECT full_name FROM students"], info, mode="tables")) == 4
    assert kept_columns(["SELECT 1"], info) == []


def test_pruned_prompt_hides_other_tables_and_dangling_foreign_keys(db):
    info = _db_info(db)
    details = schema_details(db, info, "How many students?", keep=kept_columns(["SELECT full_name FROM students"], info))
    assert "CREATE TABLE students (" in details and "full_name" in details and "class_id" in details
    assert "CREATE TABLE classes" not in details and "gender" not in details
    assert "FOREIGN KEY" not in details  # classes.id is not shown
    assert schema_details(db, info, "How many students?", keep=[]) == schema_details(db, info, "How many students?")


def test_schema_keep_cli(tmp_path, db, capsys):
    dataset = _dataset(tmp_path, db, count=2)
    pool = tmp_path / "pool.jsonl"
    rows = [{"id": "q0", "pool": [{"sql": "SELECT COUNT(*) FROM students", "success": True},
                                  {"sql": "SELECT name FROM classes", "success": False}]},
            {"id": "q1", "pool": [{"sql": "", "success": False}]}]
    pool.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    assert main([str(pool), str(dataset), "--output", str(tmp_path / "keep.json")]) == 0
    keep = json.loads((tmp_path / "keep.json").read_text(encoding="utf-8"))
    assert list(keep) == ["q0"] and ["students", "id"] in keep["q0"] and all(t == "students" for t, _ in keep["q0"])
    assert "1/2 questions pruned" in capsys.readouterr().out
