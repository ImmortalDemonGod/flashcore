#!/usr/bin/env python3
"""
Import cards, reviews, and sessions from JSON export files into a new
Flashcore DuckDB database, then validate migration completeness.

Usage:
    # Import only
    python flashcore/scripts/migrate.py import \
        --cards export/cards.json \
        --reviews export/reviews.json \
        --sessions export/sessions.json \
        --db ./new.db

    # Validate new DB against old DB
    python flashcore/scripts/migrate.py validate \
        --old-db ./old.db --new-db ./new.db
"""

import argparse
import json
import sys
from pathlib import Path

import duckdb

from flashcore.db.schema import DB_SCHEMA_SQL


# ---------------------------------------------------------------------------
# Schema initialisation
# ---------------------------------------------------------------------------


def _init_schema(conn):
    """Run the canonical Flashcore schema SQL against an open connection."""
    conn.execute(DB_SCHEMA_SQL)


# ---------------------------------------------------------------------------
# JSON loading helpers
# ---------------------------------------------------------------------------


def _load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _coerce(value, nullable=True):
    """Return value as-is; empty string → None when nullable."""
    if nullable and value == "":
        return None
    return value


# ---------------------------------------------------------------------------
# Insert helpers
# ---------------------------------------------------------------------------

_CARDS_COLUMNS = [
    "uuid", "deck_name", "front", "back", "tags",
    "added_at", "modified_at", "last_review_id", "next_due_date",
    "state", "stability", "difficulty", "origin_task",
    "media_paths", "source_yaml_file", "internal_note",
    "front_length", "back_length", "has_media", "tag_count",
]

_REVIEWS_COLUMNS = [
    "card_uuid", "session_uuid", "ts", "rating",
    "resp_ms", "eval_ms", "stab_before", "stab_after",
    "diff", "next_due", "elapsed_days_at_review",
    "scheduled_days_interval", "review_type",
]

_SESSIONS_COLUMNS = [
    "session_uuid", "user_id", "start_ts", "end_ts",
    "total_duration_ms", "cards_reviewed", "decks_accessed",
    "deck_switches", "interruptions", "device_type", "platform",
]


def _row_tuple(row, columns):
    """Extract ordered values from a dict row, defaulting missing keys to None."""  # noqa: E501
    return tuple(row.get(col) for col in columns)


def _insert_cards(conn, rows):
    placeholders = ", ".join(["?"] * len(_CARDS_COLUMNS))
    col_list = ", ".join(_CARDS_COLUMNS)
    sql = (
        f"INSERT OR REPLACE INTO cards ({col_list}) VALUES ({placeholders})"
    )
    data = [_row_tuple(r, _CARDS_COLUMNS) for r in rows]
    conn.executemany(sql, data)
    return len(data)


def _insert_reviews(conn, rows):
    placeholders = ", ".join(["?"] * len(_REVIEWS_COLUMNS))
    col_list = ", ".join(_REVIEWS_COLUMNS)
    # Omit review_id — let the sequence assign new IDs in the new DB.
    sql = (
        f"INSERT INTO reviews ({col_list}) VALUES ({placeholders})"
    )
    data = [_row_tuple(r, _REVIEWS_COLUMNS) for r in rows]
    conn.executemany(sql, data)
    return len(data)


def _insert_sessions(conn, rows):
    placeholders = ", ".join(["?"] * len(_SESSIONS_COLUMNS))
    col_list = ", ".join(_SESSIONS_COLUMNS)
    # Omit session_id — let the sequence assign new IDs.
    sql = (
        f"INSERT OR IGNORE INTO sessions ({col_list}) VALUES ({placeholders})"
    )
    data = [_row_tuple(r, _SESSIONS_COLUMNS) for r in rows]
    conn.executemany(sql, data)
    return len(data)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def import_from_json(
    cards_path,
    reviews_path,
    db_path,
    sessions_path=None,
):
    """
    Recreate the Flashcore schema in a new DuckDB file and bulk-insert rows
    from JSON export files produced by dump_history.py.

    Parameters
    ----------
    cards_path : str | Path
        Path to cards.json produced by dump_history.py.
    reviews_path : str | Path
        Path to reviews.json produced by dump_history.py.
    db_path : str | Path
        Path where the new DuckDB file will be created (or appended to).
    sessions_path : str | Path | None
        Optional path to sessions.json. Skipped when None.

    Returns
    -------
    dict[str, int]
        Mapping of table name → number of rows inserted.
    """
    db_path = Path(db_path)
    results = {}

    conn = duckdb.connect(str(db_path))
    try:
        _init_schema(conn)

        cards_rows = _load_json(cards_path)
        results["cards"] = _insert_cards(conn, cards_rows)
        print(f"  cards:    {results['cards']} rows inserted")

        reviews_rows = _load_json(reviews_path)
        results["reviews"] = _insert_reviews(conn, reviews_rows)
        print(f"  reviews:  {results['reviews']} rows inserted")

        if sessions_path is not None:
            sessions_rows = _load_json(sessions_path)
            results["sessions"] = _insert_sessions(conn, sessions_rows)
            print(f"  sessions: {results['sessions']} rows inserted")

        conn.commit()
    finally:
        conn.close()

    return results


# ---------------------------------------------------------------------------
# Validation (Task 8.3)
# ---------------------------------------------------------------------------


def validate_migration(old_db_path, new_db_path):
    """
    Compare an old and new DuckDB database for migration completeness.

    Checks performed
    ----------------
    1. Row count parity for cards and reviews.
    2. Orphaned reviews (reviews with no matching card UUID).
    3. Value-range integrity for non-New cards (stability > 0).
    4. Schema sanity: expected columns exist in both tables.

    Parameters
    ----------
    old_db_path : str | Path
        The source (legacy) database.
    new_db_path : str | Path
        The destination (new) database produced by import_from_json.

    Returns
    -------
    bool
        True if all checks pass, False otherwise.
    """
    old_db_path = Path(old_db_path)
    new_db_path = Path(new_db_path)

    old = duckdb.connect(str(old_db_path), read_only=True)
    new = duckdb.connect(str(new_db_path), read_only=True)

    passed = True

    try:
        # ── 1. Row count parity ────────────────────────────────────────────
        for table in ("cards", "reviews"):
            old_count = old.execute(
                f"SELECT COUNT(*) FROM {table}"  # noqa: S608
            ).fetchone()[0]
            new_count = new.execute(
                f"SELECT COUNT(*) FROM {table}"  # noqa: S608
            ).fetchone()[0]
            ok = old_count == new_count
            status = "PASS" if ok else "FAIL"
            print(
                f"  [{status}] {table} row count:"
                f" old={old_count}, new={new_count}"
            )
            if not ok:
                passed = False

        # ── 2. Orphaned reviews ────────────────────────────────────────────
        orphans = new.execute(
            """
            SELECT COUNT(*) FROM reviews r
            WHERE NOT EXISTS (
                SELECT 1 FROM cards c WHERE c.uuid = r.card_uuid
            )
            """
        ).fetchone()[0]
        ok = orphans == 0
        print(
            f"  [{'PASS' if ok else 'FAIL'}] orphaned reviews: {orphans}"
            " (expected 0)"
        )
        if not ok:
            passed = False

        # ── 3. Stability/difficulty range for non-New cards ───────────────
        bad_stability = new.execute(
            """
            SELECT COUNT(*) FROM cards
            WHERE state IS NOT NULL
              AND state != 'New'
              AND (stability IS NULL OR stability <= 0)
            """
        ).fetchone()[0]
        ok = bad_stability == 0
        print(
            f"  [{'PASS' if ok else 'FAIL'}] non-New cards with invalid"
            f" stability: {bad_stability} (expected 0)"
        )
        if not ok:
            passed = False

        # ── 4. Schema sanity: required columns present ────────────────────
        required_card_cols = {
            "uuid", "deck_name", "front", "back", "state",
            "stability", "difficulty", "next_due_date",
        }
        required_review_cols = {
            "card_uuid", "ts", "rating", "stab_before", "stab_after",
        }
        for table, required in (
            ("cards", required_card_cols),
            ("reviews", required_review_cols),
        ):
            actual_cols = {
                row[0]
                for row in new.execute(
                    f"DESCRIBE {table}"  # noqa: S608
                ).fetchall()
            }
            missing = required - actual_cols
            ok = len(missing) == 0
            print(
                f"  [{'PASS' if ok else 'FAIL'}] {table} schema:"
                + (
                    " all required columns present"
                    if ok
                    else f" missing columns: {missing}"
                )
            )
            if not ok:
                passed = False

    finally:
        old.close()
        new.close()

    return passed


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def _cmd_import(args):
    sessions = args.sessions if hasattr(args, "sessions") else None
    print(f"Importing into: {args.db}")
    results = import_from_json(
        cards_path=args.cards,
        reviews_path=args.reviews,
        db_path=args.db,
        sessions_path=sessions,
    )
    total = sum(results.values())
    print(f"\nDone. {total} total rows inserted.")


def _cmd_validate(args):
    print(f"Validating: old={args.old_db}  new={args.new_db}")
    print()
    ok = validate_migration(args.old_db, args.new_db)
    print()
    if ok:
        print("All checks passed.")
    else:
        print("One or more checks FAILED.", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Migrate Flashcore data from a legacy DB via JSON export."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ── import sub-command ─────────────────────────────────────────────────
    p_import = sub.add_parser(
        "import", help="Insert JSON-exported data into a new DB."
    )
    p_import.add_argument(
        "--cards", required=True, metavar="PATH", help="Path to cards.json."
    )
    p_import.add_argument(
        "--reviews",
        required=True,
        metavar="PATH",
        help="Path to reviews.json.",
    )
    p_import.add_argument(
        "--sessions",
        metavar="PATH",
        default=None,
        help="Path to sessions.json (optional).",
    )
    p_import.add_argument(
        "--db", required=True, metavar="PATH", help="Path to new DuckDB file."
    )
    p_import.set_defaults(func=_cmd_import)

    # ── validate sub-command ───────────────────────────────────────────────
    p_val = sub.add_parser(
        "validate", help="Compare old and new DBs for migration integrity."
    )
    p_val.add_argument(
        "--old-db",
        required=True,
        metavar="PATH",
        help="Path to the legacy DuckDB file.",
    )
    p_val.add_argument(
        "--new-db",
        required=True,
        metavar="PATH",
        help="Path to the new DuckDB file.",
    )
    p_val.set_defaults(func=_cmd_validate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
