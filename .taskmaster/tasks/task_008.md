# Task ID: 8

**Title:** Implement Data Safety Strategy

**Status:** pending

**Dependencies:** 7

**Priority:** medium

**Description:** Develop a strategy for safely migrating data from the old system to the new library.

**Details:**

PRD Section 4 Phase 3: Do NOT copy .db file directly (binary compatibility risk). Keep HPE_ARCHIVE as read-only reference. Instead: (1) Create export script flashcore/scripts/dump_history.py that connects directly to the OLD DB path (duckdb) and exports cards -> cards.json, reviews -> reviews.json (no imports from HPE_ARCHIVE required). (2) Create flashcore/scripts/migrate.py (utility folder, NOT core package) with import_from_json(cards_path, reviews_path, db_path) that recreates schema and inserts data. (3) Validation: Compare row counts between old and new DBs, plus integrity checks (relationships and value ranges).

**Test Strategy:**

Export from old DB using flashcore/scripts/dump_history.py, import to new DB using flashcore/scripts/migrate.py. Verify row counts: SELECT COUNT(*) FROM cards matches; SELECT COUNT(*) FROM reviews matches. Relationship check: SELECT COUNT(*) FROM reviews r WHERE NOT EXISTS (SELECT 1 FROM cards c WHERE c.uuid = r.card_uuid); expected 0. Range check (example): SELECT COUNT(*) FROM cards WHERE state != 'New' AND (stability IS NULL OR stability <= 0); expected 0. Spot-check card UUIDs exist in both DBs.

## Subtasks

### 8.1. Create dump_history.py Export Script

**Status:** pending  
**Dependencies:** None  

Export cards and reviews from the legacy DB into JSON files.

**Details:**

Create flashcore/scripts/dump_history.py. It must connect directly to the old DuckDB file path and export cards -> cards.json, reviews -> reviews.json. Do not import anything from HPE_ARCHIVE.

### 8.2. Create migrate.py Import Utility

**Status:** pending  
**Dependencies:** 8.1  

Import cards/reviews JSON into a new DB and recreate schema.

**Details:**

Create flashcore/scripts/migrate.py with import_from_json(cards_path, reviews_path, db_path). It recreates schema and inserts data.

### 8.3. Add Migration Validation Queries

**Status:** pending  
**Dependencies:** 8.2  

Validate migration completeness and integrity beyond simple row counts.

**Details:**

In addition to row count comparisons, run integrity checks: (1) Relationship validation: reviews must reference existing cards. (2) Value range validation: stability/difficulty values are within expected ranges. (3) Schema sanity: expected columns exist and are correct types.

## Audit Finding Notes

### F169 — FSRS elapsed_days=0 for on-time reviews (ADDRESSED, 2026-06-19)

Path A chosen (D1, operator-confirmed 2026-06-19). `last_review_date` transient field added to `Card` model (`flashcore/models.py:61`); hub (`review_processor`) reads `reviews.ts` from DB via `get_latest_review_for_card` before every `compute_next_state` call; scheduler uses ground-truth `elapsed_days` for all cards with review history. Commit SHAs: `e0f6519` (models), `3fa913a` (scheduler), `37a0dec` (review_processor). Follow-up: DB migration PR to persist `last_review_date` column (deferred to stage-c2 migration PR); backfill PR for existing DB rows.
