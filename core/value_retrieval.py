"""Question-matched example values for the schema prompt (retrieval "new").

Differences from the paper-style retrieval in core.omnisql_prompt._relevant_values:
- Matching is done on normalised text (lowercase, punctuation and repeated spaces folded), so
  "St. Louis", "st louis" and "St Louis" match, and a light plural/possessive stem lets
  "Lakers'" or "schools" find "Laker"/"school" values. Leading zeros are ignored in numbers, so
  "40" finds "0040" and "1994/3/3" finds "1994-03-03".
- A value is kept when it is (almost) contained in the question/evidence, as before, or when all of
  its content tokens occur there, in any order.
- Up to 3 values per column, 40 in total, instead of 20 in total, so a frequent token in one
  column (e.g. "male") cannot crowd out the value of another column.
- More distinct values are indexed per column (100 000 instead of 20 000).
The index is built once per database and kept in memory.
"""
from functools import lru_cache
from pathlib import Path
import re
import sqlite3

STOPWORDS = set("""
a an the of in on at to for from by with and or not no is are was were be been being has have had do does did
what which who whom whose when where why how many much list name names give show find tell me please all any
each per than then that this these those it its as into over under between among their there they them he she
his her him we our you your i one two three most more least less highest lowest top among average total number
""".split())
_WORD = re.compile(r"[a-z0-9]+")
MAX_PER_COLUMN = 3
MAX_TOTAL = 40
MIN_SCORE = 0.85
MAX_QUOTED = 40
_QUOTED = re.compile(r"'([^'\n]{1,%d})'|\"([^\"\n]{1,%d})\"" % (MAX_QUOTED, MAX_QUOTED))


def normalise(text: str) -> str:
    return " ".join(_WORD.findall(text.lower()))


def _stem(token: str) -> str:
    if token.isdigit():  # "0040" ~ "40", "1994-03-03" ~ "1994/3/3"
        return token.lstrip("0") or "0"
    if len(token) > 4 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 3 and token.endswith("es") and token[-3] in "sxz":
        return token[:-2]
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def _content_tokens(text: str) -> set:
    return {_stem(t) for t in _WORD.findall(text.lower()) if t not in STOPWORDS}


def _connect(db_path: str) -> sqlite3.Connection:
    connection = sqlite3.connect(Path(db_path).resolve().as_uri() + "?mode=ro", uri=True)
    connection.text_factory = lambda b: b.decode("utf-8", "replace")
    return connection


@lru_cache(maxsize=16)
def _index(db_path: str) -> tuple:
    """(values, inverted index stem -> value ids, short raw value lowercased -> value ids).

    values[i] = (key, raw, normalised, content stems).
    """
    values, inverted, by_raw = [], {}, {}
    connection = _connect(db_path)
    try:
        tables = [r[0] for r in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
        for table in tables:
            for column in [r[1] for r in connection.execute(f"PRAGMA table_info(`{table}`)")]:
                key = f"{table}.{column}".lower()
                for (raw,) in connection.execute(
                        f"SELECT DISTINCT `{column}` FROM `{table}` WHERE typeof(`{column}`) = 'text' "
                        f"AND length(`{column}`) BETWEEN 1 AND 100 LIMIT 100000"):
                    norm = normalise(raw)
                    stems = _content_tokens(raw) or {_stem(t) for t in norm.split()}
                    index = len(values)
                    values.append((key, raw, norm, frozenset(stems)))
                    if len(raw) <= MAX_QUOTED:
                        by_raw.setdefault(raw.lower(), []).append(index)
                    for stem in stems:
                        inverted.setdefault(stem, []).append(index)
    finally:
        connection.close()
    return values, inverted, by_raw


def _substring_score(value: str, text: str) -> float:
    """Longest substring of `value` found in `text`, as a fraction of len(value)."""
    best = 0
    for i in range(len(value)):
        if len(value) - i <= best:
            break
        for j in range(len(value), i + best, -1):
            if value[i:j] in text:
                best = j - i
                break
    return best / len(value)


def retrieve_values(db_path: str, question: str) -> dict:
    """{table.column: [values]} of values that the question/evidence refers to."""
    values, inverted, by_raw = _index(str(db_path))
    norm_question = normalise(question)
    question_stems = _content_tokens(question)
    # Quoted strings in the question/evidence (e.g. bond_type = '#', element = 'i') match a value
    # exactly, ignoring case, even when they are punctuation or stopwords.
    quoted = set()
    for single, double in _QUOTED.findall(question):
        quoted.update(by_raw.get((single or double).lower(), []))
    # Very common stems (e.g. a token in every row of a column) are skipped as entry points.
    limit = max(2000, len(values) // 20)
    candidates = set()
    for stem in question_stems:
        ids = inverted.get(stem, [])
        if len(ids) <= limit:
            candidates.update(ids)

    hits = []
    for index in candidates | quoted:
        key, raw, norm, stems = values[index]
        exact = index in quoted or bool(norm) and f" {norm} " in f" {norm_question} "
        if exact:
            score = 1.0
        elif not norm or not stems:
            continue
        else:
            coverage = len(stems & question_stems) / len(stems)
            score = max(coverage if coverage == 1.0 else 0.0, _substring_score(norm, norm_question))
        if score >= MIN_SCORE:
            # Longer exact phrases first: "Los Angeles" beats "Los"; raw-case equality breaks ties.
            hits.append((exact, score, len(norm), raw in question, -index, key, raw))

    relevant, total = {}, 0
    for *_, key, raw in sorted(hits, reverse=True):
        column_values = relevant.setdefault(key, [])
        if len(column_values) < MAX_PER_COLUMN and raw not in column_values:
            column_values.append(raw)
            total += 1
            if total >= MAX_TOTAL:
                break
    return {k: v for k, v in relevant.items() if v}
