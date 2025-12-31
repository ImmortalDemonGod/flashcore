# Task ID: 8

**Title:** Implement Data Safety Strategy

**Status:** pending

**Dependencies:** 7

**Priority:** medium

**Description:** Develop a strategy for safely migrating data from the old system to the new library.

**Details:**

PRD Section 4 Phase 3: Do NOT copy .db file directly (binary compatibility risk). Instead: (1) Create export script in HPE_ARCHIVE: dump_history.py that exports cards -> cards.json, reviews -> reviews.json. (2) Create flashcore/migrate.py with import_from_json(cards_path, reviews_path, db_path) that recreates schema and inserts data. (3) Validation: Compare row counts between old and new DBs. This ensures schema compatibility and data integrity.

**Test Strategy:**

Export from old DB, import to new DB, verify: SELECT COUNT(*) FROM cards matches, SELECT COUNT(*) FROM reviews matches. Spot-check card UUIDs exist in both DBs.
