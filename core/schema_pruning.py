"""Schema kept for a second sampling round: what the first-round SQL samples of a question used.

No model call. Every executable first-round sample is parsed; a table is kept when a sample reads
it, and (mode "columns") a column of a kept table when a sample names it or it is a primary/foreign
key, so joins stay visible. Mode "tables" keeps every column of the kept tables. An empty result
(no parsable sample) means "keep the full schema".
"""
import sqlglot
from sqlglot import exp


def sql_names(sql: str) -> tuple[set, set] | None:
    """(table names, column names), lowercase, or None when the SQL does not parse."""
    try:
        tree = sqlglot.parse_one(sql, read="sqlite")
    except (sqlglot.errors.SqlglotError, RecursionError):
        return None
    if tree is None:
        return None
    return ({t.name.lower() for t in tree.find_all(exp.Table)}, {c.name.lower() for c in tree.find_all(exp.Column)})


def kept_columns(sqls: list[str], db_info: dict, mode: str = "columns") -> list[list[str]]:
    """[[table, column], ...] in original spelling, in schema order."""
    tables, columns = set(), set()
    for sql in sqls:
        names = sql_names(sql)
        if names:
            tables |= names[0]
            columns |= names[1]
    table_names = db_info["table_names_original"]
    keys = {i for k in db_info["primary_keys"] for i in (k if isinstance(k, list) else [k])}
    keys |= {i for pair in db_info["foreign_keys"] for i in pair}
    kept = []
    for index, (owner, column) in enumerate(db_info["column_names_original"]):
        if owner < 0 or table_names[owner].lower() not in tables:
            continue
        if mode == "tables" or column.lower() in columns or index in keys:
            kept.append([table_names[owner], column])
    return kept
