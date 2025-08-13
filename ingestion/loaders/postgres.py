from __future__ import annotations

import csv
import io
import json
from typing import Iterable, Mapping
from uuid import uuid4

import psycopg2


def bulk_upsert(
    conn: psycopg2.extensions.connection,
    table: str,
    rows: Iterable[Mapping[str, object]],
    conflict_keys: list[str],
) -> int:
    """COPY rows into a temp table then UPSERT into ``table``.

    Returns the number of rows affected in the target table.
    """

    row_list = list(rows)
    if not row_list:
        return 0

    columns = list(row_list[0].keys())
    tmp_table = f"tmp_{table}_{uuid4().hex}"

    cur = conn.cursor()

    cur.execute(
        f"CREATE TEMP TABLE {tmp_table} (LIKE {table} INCLUDING DEFAULTS) "
        "ON COMMIT DROP"
    )

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    for row in row_list:
        writer.writerow(
            [
                (
                    json.dumps(row.get(col))
                    if isinstance(row.get(col), (dict, list))
                    else row.get(col)
                )
                for col in columns
            ]
        )
    buffer.seek(0)

    cur.copy_expert(
        f"COPY {tmp_table} ({', '.join(columns)}) FROM STDIN WITH (FORMAT CSV)",
        buffer,
    )

    assignments = ", ".join(
        f"{col}=EXCLUDED.{col}" for col in columns if col not in conflict_keys
    )
    action = f"DO UPDATE SET {assignments}" if assignments else "DO NOTHING"
    sql = (
        f"INSERT INTO {table} ({', '.join(columns)}) SELECT {', '.join(columns)} "
        f"FROM {tmp_table} ON CONFLICT ({', '.join(conflict_keys)}) {action}"
    )
    cur.execute(sql)
    affected = cur.rowcount
    conn.commit()
    return affected
