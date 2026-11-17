import sqlite3

import pytest

from core.value_retrieval import _index, normalise, retrieve_values
from evaluation.value_recall import gold_literals


@pytest.fixture()
def db(tmp_path):
    path = tmp_path / "v.sqlite"
    connection = sqlite3.connect(path)
    connection.executescript("""
        CREATE TABLE schools (County TEXT, City TEXT, Charter TEXT, Opened TEXT, Gender TEXT);
        INSERT INTO schools VALUES ('Alameda', 'St. Louis', '0040', '1994-03-03', 'M');
        INSERT INTO schools VALUES ('Los Angeles', 'Los Altos', '0041', '1994-03-30', 'F');
    """)
    connection.commit()
    connection.close()
    _index.cache_clear()
    return str(path)


def test_normalise_folds_case_and_punctuation():
    assert normalise("St. Louis!") == "st louis"


def test_case_and_punctuation_insensitive(db):
    assert "St. Louis" in retrieve_values(db, "Schools in st louis?")["schools.city"]


def test_leading_zeros_and_dates(db):
    found = retrieve_values(db, "Which school has charter number 40 and opened in 1994/3/3?")
    assert found["schools.charter"] == ["0040"]
    assert found["schools.opened"] == ["1994-03-03"]


def test_partial_value_is_not_returned(db):
    found = retrieve_values(db, "How many schools are in Los Angeles?")
    assert found["schools.county"] == ["Los Angeles"]
    assert "schools.city" not in found  # "Los Altos" shares only "los"


def test_quoted_symbols_and_stopwords(tmp_path):
    path = tmp_path / "q.sqlite"
    connection = sqlite3.connect(path)
    connection.executescript("CREATE TABLE bond (bond_type TEXT, element TEXT);"
                             "INSERT INTO bond VALUES ('#', 'i'), ('=', 'cl');")
    connection.commit()
    connection.close()
    found = retrieve_values(str(path), "triple bond refers to bond_type = '#'; iodine refers to element = 'I'\n"
                                       "How many triple bonds with iodine?")
    assert found["bond.bond_type"] == ["#"]
    assert found["bond.element"] == ["i"]


def test_gold_literals():
    sql = "SELECT a FROM t WHERE `County Name` = 'Alameda' AND 'x' = b AND c IN ('p', 'q') AND d LIKE '%z%'"
    assert set(gold_literals(sql)) == {("county name", "Alameda"), ("b", "x"), ("c", "p"), ("c", "q")}
