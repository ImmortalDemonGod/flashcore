#!/usr/bin/env python3
"""
Export cards, reviews, and sessions from a legacy Flashcore DuckDB database
to JSON files for safe migration to the new schema.

Usage:
    python flashcore/scripts/dump_history.py --db ./old.db --out-dir ./export/
"""

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

import duckdb


def _serialize(value):
    """Convert DuckDB-specific types to JSON-serializable Python primitives."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, list):
        return [_serialize(v) for v in value]
    # UUID objects and other non-primitives → str
    if not isinstance(value, (int, float, bool, str, type(None))):
        return str(value)
    return value


def _rows_to_json(cursor):
    """Fetch all rows from a cursor and return as a list of dicts."""
    rows = cursor.fetchall()
    if not rows:
        return []
    columns = [desc[0] for desc in cursor.description]
    return [
        {col: _serialize(val) for col, val in zip(columns, row)}
        for row in rows
    ]


def dump_table(conn, table_name, out_path):
    """Export a single table to a JSON file. Returns row count."""
    cursor = conn.execute(f"SELECT * FROM {table_name}")  # noqa: S608
    data = _rows_to_json(cursor)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    return len(data)


def dump_database(db_path, out_dir):
    """
    Connect read-only to db_path and export all recognized tables to out_dir.

    Parameters
    ----------
    db_path : str | Path
        Path to the legacy DuckDB database file.
    out_dir : str | Path
        Directory where cards.json, reviews.json, sessions.json are written.

    Returns
    -------
    dict[str, int]
        Mapping of table name → number of rows exported.
    """
    db_path = Path(db_path)
    out_dir = Path(out_dir)

    if not db_path.exists():
        raise FileNotFoundError(f"DB file not found: {db_path}")

    out_dir.mkdir(parents=True, exist_ok=True)

    conn = duckdb.connect(str(db_path), read_only=True)
    try:
        existing_tables = {
            row[0] for row in conn.execute("SHOW TABLES").fetchall()
        }
        results = {}
        for table in ("cards", "reviews", "sessions"):
            if table not in existing_tables:
                print(
                    f"  WARNING: table '{table}' not found in source DB"
                    " — skipping.",
                    file=sys.stderr,
                )
                continue
            out_path = out_dir / f"{table}.json"
            count = dump_table(conn, table, out_path)
            results[table] = count
            print(f"  {table}: {count} rows → {out_path}")
    finally:
        conn.close()

    return results


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Export a legacy Flashcore DuckDB database to JSON files"
            " for safe migration."
        )
    )
    parser.add_argument(
        "--db",
        required=True,
        metavar="PATH",
        help="Path to the legacy DuckDB file.",
    )
    parser.add_argument(
        "--out-dir",
        required=True,
        metavar="DIR",
        help="Directory to write cards.json, reviews.json, sessions.json.",
    )
    args = parser.parse_args()

    print(f"Exporting from: {args.db}")
    print(f"Output dir:     {args.out_dir}")
    print()

    try:
        results = dump_database(args.db, args.out_dir)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    total = sum(results.values())
    tables_n = len(results)
    print(f"\nDone. {total} total rows exported across {tables_n} table(s).")


if __name__ == "__main__":
    main()
