#!/usr/bin/env python3
"""
Migration: DATE -> TIMESTAMP WITH TIME ZONE for the scheduling columns, plus a
new cards.step column.

Why: the scheduler used to truncate FSRS's datetime `due` to a bare DATE, so
learning/relearning steps (1m/10m) collapsed to a 0-day "due today" and the
learning-step counter was never persisted. The engine now stores full timestamps
and a step index; this migration brings an existing flash.db up to that schema.

It is IDEMPOTENT (safe to run twice) and takes a timestamped backup first.

Usage:
    python scripts/migrate_to_datetime_fidelity.py /path/to/flash.db
    python scripts/migrate_to_datetime_fidelity.py /path/to/flash.db --no-backup
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

import duckdb


def _col_type(con: duckdb.DuckDBPyConnection, table: str, column: str) -> str | None:
    row = con.execute(
        "SELECT data_type FROM information_schema.columns "
        "WHERE table_name = ? AND column_name = ?",
        [table, column],
    ).fetchone()
    return row[0] if row else None


# Canonical (table -> [(index_name, create_sql)]) so we can drop every index on a
# table before an ALTER COLUMN TYPE (DuckDB blocks the retype while any index on
# the table exists) and faithfully recreate them afterward.
_INDEXES = {
    "cards": [
        ("idx_cards_deck_name", "CREATE INDEX idx_cards_deck_name ON cards (deck_name)"),
        ("idx_cards_next_due_date", "CREATE INDEX idx_cards_next_due_date ON cards (next_due_date)"),
    ],
    "reviews": [
        ("idx_reviews_card_uuid", "CREATE INDEX idx_reviews_card_uuid ON reviews (card_uuid)"),
        ("idx_reviews_session_uuid", "CREATE INDEX idx_reviews_session_uuid ON reviews (session_uuid)"),
        ("idx_reviews_ts", "CREATE INDEX idx_reviews_ts ON reviews (ts)"),
        ("idx_reviews_next_due", "CREATE INDEX idx_reviews_next_due ON reviews (next_due)"),
    ],
}


def _drop_indexes(con: duckdb.DuckDBPyConnection, table: str) -> None:
    for name, _ in _INDEXES.get(table, []):
        con.execute(f"DROP INDEX IF EXISTS {name}")


def _recreate_indexes(con: duckdb.DuckDBPyConnection, table: str) -> None:
    for name, sql in _INDEXES.get(table, []):
        con.execute(sql.replace("CREATE INDEX", "CREATE INDEX IF NOT EXISTS"))


def migrate(db_path: Path, backup: bool = True) -> dict:
    if not db_path.exists():
        raise FileNotFoundError(db_path)

    report: dict = {"db": str(db_path), "backup": None, "actions": []}

    if backup:
        backup_dir = db_path.parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        # Caller passes a fixed timestamp-free name to keep this deterministic;
        # we stamp via mtime-free counter so reruns don't clobber.
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        bpath = backup_dir / f"{db_path.stem}-backup-pre-datetime-{stamp}{db_path.suffix}"
        shutil.copy2(db_path, bpath)
        report["backup"] = str(bpath)

    con = duckdb.connect(str(db_path), read_only=False)
    try:
        # 1. cards.next_due_date DATE -> TIMESTAMPTZ. DuckDB blocks ALTER COLUMN
        #    TYPE while any index on the table exists, so drop all of the table's
        #    indexes, retype, then recreate them.
        t = _col_type(con, "cards", "next_due_date")
        if t and "TIMESTAMP" not in t.upper():
            _drop_indexes(con, "cards")
            con.execute(
                "ALTER TABLE cards ALTER COLUMN next_due_date "
                "TYPE TIMESTAMP WITH TIME ZONE"
            )
            _recreate_indexes(con, "cards")
            report["actions"].append(f"cards.next_due_date {t} -> TIMESTAMPTZ")
        else:
            report["actions"].append(f"cards.next_due_date already {t} (skip)")

        # 2. reviews.next_due DATE -> TIMESTAMPTZ
        t = _col_type(con, "reviews", "next_due")
        if t and "TIMESTAMP" not in t.upper():
            _drop_indexes(con, "reviews")
            con.execute(
                "ALTER TABLE reviews ALTER COLUMN next_due "
                "TYPE TIMESTAMP WITH TIME ZONE"
            )
            _recreate_indexes(con, "reviews")
            report["actions"].append(f"reviews.next_due {t} -> TIMESTAMPTZ")
        else:
            report["actions"].append(f"reviews.next_due already {t} (skip)")

        # 3. cards.step INTEGER (new)
        if _col_type(con, "cards", "step") is None:
            con.execute("ALTER TABLE cards ADD COLUMN step INTEGER")
            report["actions"].append("cards.step added (INTEGER)")
        else:
            report["actions"].append("cards.step already present (skip)")

        # 4. Backfill step=0 for cards mid-(re)learning with no recorded step, so
        #    they resume at the first step instead of a NULL the engine must guess.
        n = con.execute(
            "UPDATE cards SET step = 0 "
            "WHERE step IS NULL AND state IN ('Learning', 'Relearning')"
        ).fetchall()
        # DuckDB UPDATE doesn't return rowcount via fetchall; count explicitly.
        backfilled = con.execute(
            "SELECT COUNT(*) FROM cards WHERE step = 0 AND state IN ('Learning','Relearning')"
        ).fetchone()[0]
        report["actions"].append(f"cards.step backfilled to 0 for Learning/Relearning (now {backfilled})")
    finally:
        con.close()

    return report


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("db_path", type=Path, help="Path to the flash.db DuckDB file")
    ap.add_argument("--no-backup", action="store_true", help="Skip the pre-migration backup")
    args = ap.parse_args(argv)

    report = migrate(args.db_path, backup=not args.no_backup)
    print(f"Migrated {report['db']}")
    if report["backup"]:
        print(f"  backup: {report['backup']}")
    for a in report["actions"]:
        print(f"  - {a}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
