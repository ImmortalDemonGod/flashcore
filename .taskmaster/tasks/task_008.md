# Task ID: 8

**Title:** Implement Data Safety Strategy

**Status:** pending

**Dependencies:** 7

**Priority:** medium

**Description:** Develop a strategy for safely migrating data from the old system to the new library.

**Details:**

PRD Section 4 Phase 3: Do NOT copy .db file directly (binary compatibility risk). Keep HPE_ARCHIVE as read-only reference. Instead: (1) Create export script flashcore/scripts/dump_history.py that connects directly to the OLD DB path (duckdb) and exports cards -> cards.json, reviews -> reviews.json (no imports from HPE_ARCHIVE required). (2) Create flashcore/scripts/migrate.py (utility folder, NOT core package) with import_from_json(cards_path, reviews_path, db_path) that recreates schema and inserts data. (3) Validation: Compare row counts between old and new DBs.

**Test Strategy:**

Export from old DB using flashcore/scripts/dump_history.py, import to new DB using flashcore/scripts/migrate.py, verify: SELECT COUNT(*) FROM cards matches, SELECT COUNT(*) FROM reviews matches. Spot-check card UUIDs exist in both DBs.
