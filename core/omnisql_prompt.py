"""SLM-SQL paper prompt (Appendix E.1) over the OmniSQL/CSC-SQL schema format.

Mirrors CSC-SQL's process_dataset.py and infer.py (think template, default system prompt):
CREATE TABLE blocks with column comments, PK/FK constraints and up to 6 example values per
column (question-matched values first, then 2 sampled distinct values). CSC-SQL retrieves
candidate values with a Lucene BM25 index; here every distinct short text value that shares a
token with the question is a candidate, and the same >0.85 substring-match filter and top-20
cut are applied.
"""
from functools import lru_cache
import json
from pathlib import Path
import re
import sqlite3

SYSTEM_PROMPT = (
    "You are a helpful AI Assistant that provides well-reasoned and detailed responses. You first think about "
    "the reasoning process as an internal monologue and then provide the user with the answer. Respond in the "
    "following format: <think>\n...\n</think>\n<answer>\n...\n</answer>"
)

_TASK = """Task Overview:
You are a data science expert. Below, you are provided with a database schema and a natural language question. Your task is to understand the schema and generate a valid SQL query to answer the question.

Database Engine:
SQLite

Database Schema:
{db_details}
This schema describes the database's structure, including tables, columns, primary keys, foreign keys, and any relevant relationships or constraints.

Question:
{question}

Instructions:
- Make sure you only output the information that is asked in the question. If the question asks for a specific column, make sure to only include that column in the SELECT clause, nothing more.
- The generated query should return all of the information asked in the question without any missing or extra information.
- Before generating the final SQL query, please think through the steps of how to write the query.

"""
_OUTPUT = ("Show your work in <think> </think> tags. And return the final SQLite SQL query that starts with keyword "
           "`SELECT` in <answer> </answer> tags, for example <answer>SELECT AVG(rating_score) FROM movies</answer>. ")
# Assembled exactly as CSC-SQL make_prefix(template_type="think") does, trailing spaces included.
TEMPLATE = ("You first thinks about the reasoning process in the mind and then provides the user with the answer.\n"
            + _TASK + "\n\nOutput Format:\n" + _OUTPUT + " \n\nLet me solve this step by step.")

SQL_RESERVED = set("""
ABORT ACTION ADD AFTER ALL ALTER ANALYZE AND AS ASC ATTACH AUTOINCREMENT BEFORE BEGIN BETWEEN BY CASCADE CASE
CAST CHECK COLLATE COLUMN COMMIT CONFLICT CONSTRAINT CREATE CROSS CURRENT_DATE CURRENT_TIME CURRENT_TIMESTAMP
DATABASE DEFAULT DEFERRABLE DEFERRED DELETE DESC DETACH DISTINCT DROP EACH ELSE END ESCAPE EXCEPT EXCLUSIVE
EXISTS EXPLAIN FAIL FOR FOREIGN FROM FULL GLOB GROUP HAVING IF IGNORE IMMEDIATE IN INDEX INDEXED INITIALLY INNER
INSERT INSTEAD INTERSECT INTO IS ISNULL JOIN KEY LEFT LIKE LIMIT MATCH NATURAL NO NOT NOTNULL NULL OF OFFSET ON
OR ORDER OUTER PLAN PRAGMA PRIMARY QUERY RAISE RECURSIVE REFERENCES REGEXP REINDEX RELEASE RENAME REPLACE
RESTRICT RIGHT ROLLBACK ROW SAVEPOINT SELECT SET TABLE TEMP TEMPORARY THEN TO TRANSACTION TRIGGER UNION UNIQUE
UPDATE USING VACUUM VALUES VIEW VIRTUAL WHEN WHERE WITH WITHOUT
""".split())


def _identifier(name: str) -> str:
    return f"`{name}`" if name.upper() in SQL_RESERVED or re.search(r"[^A-Za-z0-9_]", name) else name


def _connect(db_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(Path(db_path).resolve().as_uri() + "?mode=ro", uri=True)
    connection.text_factory = lambda b: b.decode("utf-8", "replace")
    return connection


@lru_cache(maxsize=64)
def _tables(tables_path: str) -> dict:
    return {t["db_id"]: t for t in json.loads(Path(tables_path).read_text(encoding="utf-8"))}


@lru_cache(maxsize=64)
def _sampled_values(db_path: str, limit: int = 2) -> dict:
    values = {}
    connection = _connect(Path(db_path))
    try:
        tables = [r[0] for r in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
        for table in tables:
            for column in [r[1] for r in connection.execute(f"PRAGMA table_info(`{table}`)")]:
                rows = connection.execute(
                    f"SELECT `{column}` FROM (SELECT DISTINCT `{column}` FROM `{table}` "
                    f"WHERE `{column}` IS NOT NULL AND `{column}` != '') LIMIT {limit}").fetchall()
                found = [v[:40] if isinstance(v, str) else v for (v,) in rows]
                if found:
                    values[f"{table}.{column}".lower()] = found
    finally:
        connection.close()
    return values


@lru_cache(maxsize=64)
def _text_values(db_path: str) -> list:
    """Distinct short text values per column: the candidate pool for question-matched examples."""
    out = []
    connection = _connect(Path(db_path))
    try:
        tables = [r[0] for r in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
        for table in tables:
            for column in [r[1] for r in connection.execute(f"PRAGMA table_info(`{table}`)")]:
                for (value,) in connection.execute(
                        f"SELECT DISTINCT `{column}` FROM `{table}` WHERE typeof(`{column}`) = 'text' "
                        f"AND length(`{column}`) BETWEEN 1 AND 100 LIMIT 20000"):
                    out.append((f"{table}.{column}".lower(), value, set(re.findall(r"\w+", value.lower()))))
    finally:
        connection.close()
    return out


def _match_score(value: str, question: str) -> float:
    """CSC-SQL calculate_substring_match_percentage: longest substring of value found in question."""
    value, question = value.lower(), question.lower()
    best = 0
    for i in range(len(value)):
        for j in range(len(value), i + best, -1):
            if value[i:j] in question:
                best = j - i
                break
    return best / len(value)


def _relevant_values(db_path: str, question: str) -> dict:
    tokens = set(re.findall(r"\w+", question.lower()))
    hits = []
    for index, (key, value, value_tokens) in enumerate(_text_values(db_path)):
        if value_tokens & tokens:
            score = _match_score(value, question)
            if score > 0.85:
                hits.append((score, len(value), index, key, value))
    relevant = {}
    for _, _, _, key, value in sorted(hits, reverse=True)[:20]:
        relevant.setdefault(key, []).append(value)
    return relevant


def schema_details(db_path: Path, db_info: dict, question: str) -> str:
    sampled = _sampled_values(str(db_path))
    relevant = _relevant_values(str(db_path), question)
    names, comments, types = db_info["column_names_original"], db_info["column_names"], db_info["column_types"]
    primary = {i for k in db_info["primary_keys"] for i in (k if isinstance(k, list) else [k])}
    blocks = []
    for table_index, table in enumerate(db_info["table_names_original"]):
        columns, pk, fk = [], [], []
        for index, ((owner, column), (_, comment), column_type) in enumerate(zip(names, comments, types)):
            if owner != table_index:
                continue
            key = f"{table}.{column}".lower()
            examples = list(dict.fromkeys(relevant.get(key, []) + sampled.get(key, [])))[:6]
            plain = column.lower() in (comment.lower(), comment.lower().replace(" ", "_"),
                                       comment.lower().replace(" ", "")) or not comment.strip()
            line = f"    {_identifier(column)} {column_type},"
            if not plain:
                line += f" -- {comment}"
            if examples:
                line += (", example: " if not plain else " -- example: ") + str(examples)
            columns.append(line)
            if index in primary:
                pk.append(column)
            for source, target in db_info["foreign_keys"]:
                if source == index:
                    target_table = db_info["table_names_original"][names[target][0]]
                    fk.append(f"    CONSTRAINT fk_{table.lower().replace(' ', '_')}_{column.lower().replace(' ', '_')} "
                              f"FOREIGN KEY ({_identifier(column)}) REFERENCES {_identifier(target_table)} "
                              f"({_identifier(names[target][1])}),")
        if not columns:
            continue
        pk_line = ["    PRIMARY KEY (" + ", ".join(_identifier(c) for c in dict.fromkeys(pk)) + "),"] if pk else []
        ddl = f"CREATE TABLE {_identifier(table)} (\n" + "\n".join(columns + pk_line + list(dict.fromkeys(fk)))
        blocks.append(ddl.removesuffix(",") + "\n);")
    return "\n\n".join(blocks)


def build_paper_prompt(question: str, db_path: Path, db_id: str, tables_path: Path, evidence: str = "") -> str:
    question = f"{evidence}\n{question}" if evidence.strip() else question
    details = schema_details(db_path, _tables(str(Path(tables_path).resolve()))[db_id], question)
    return TEMPLATE.format(db_details=details, question=question)
