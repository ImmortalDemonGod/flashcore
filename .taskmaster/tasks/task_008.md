# Task ID: 8

**Title:** Implement Data Safety Strategy

**Status:** pending

**Dependencies:** 7

**Priority:** medium

**Description:** Develop a strategy for safely migrating data from the old system to the new library.

**Details:**

PRD Section 4 Phase 3: Do NOT copy .db file directly (binary compatibility risk). Instead: (1) Create export script HPE_ARCHIVE/dump_history.py (in legacy environment) that runs against the old DB and exports cards -> cards.json, reviews -> reviews.json. (2) Create flashcore/scripts/migrate.py (in new library utility folder, NOT core package) with import_from_json(cards_path, reviews_path, db_path) that recreates schema and inserts data. (3) Validation: Compare row counts between old and new DBs. CRITICAL SEPARATION: dump_history.py lives in HPE_ARCHIVE (legacy), migrate.py lives in flashcore/scripts/ (new utility). Do not put migration scripts in core flashcore package logic to avoid polluting the library.

**Test Strategy:**

Export from old DB using HPE_ARCHIVE/dump_history.py, import to new DB using flashcore/scripts/migrate.py, verify: SELECT COUNT(*) FROM cards matches, SELECT COUNT(*) FROM reviews matches. Spot-check card UUIDs exist in both DBs.
