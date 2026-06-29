# AIV Evidence File (v1.0)

**File:** `flashcore/db/database.py`
**Commit:** `5d96cc4`
**Generated:** 2026-06-29T20:43:26Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "flashcore/db/database.py"
  classification_rationale: "R1 correctness-critical DB layer"
  classified_by: "Miguel Ingram"
  classified_at: "2026-06-29T20:43:26Z"
```

## Claim(s)

1. FlashcardDatabase.get_due_cards compares next_due_date against a timestamp, coercing a bare date to end-of-day
2. FlashcardDatabase persists the FSRS step via the cards upsert and the post-review card update
3. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/pull/58](https://github.com/ImmortalDemonGod/flashcore/pull/58)
- **Requirements Verified:** Due queries and writes must use timestamps and persist the step

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`5d96cc4`](https://github.com/ImmortalDemonGod/flashcore/tree/5d96cc4406821652303022d0633d15a29a02862e))

- [`flashcore/db/database.py#L145-L146`](https://github.com/ImmortalDemonGod/flashcore/blob/5d96cc4406821652303022d0633d15a29a02862e/flashcore/db/database.py#L145-L146)
- [`flashcore/db/database.py#L176-L180`](https://github.com/ImmortalDemonGod/flashcore/blob/5d96cc4406821652303022d0633d15a29a02862e/flashcore/db/database.py#L176-L180)
- [`flashcore/db/database.py#L400-L407`](https://github.com/ImmortalDemonGod/flashcore/blob/5d96cc4406821652303022d0633d15a29a02862e/flashcore/db/database.py#L400-L407)
- [`flashcore/db/database.py#L416`](https://github.com/ImmortalDemonGod/flashcore/blob/5d96cc4406821652303022d0633d15a29a02862e/flashcore/db/database.py#L416)
- [`flashcore/db/database.py#L453-L462`](https://github.com/ImmortalDemonGod/flashcore/blob/5d96cc4406821652303022d0633d15a29a02862e/flashcore/db/database.py#L453-L462)
- [`flashcore/db/database.py#L467`](https://github.com/ImmortalDemonGod/flashcore/blob/5d96cc4406821652303022d0633d15a29a02862e/flashcore/db/database.py#L467)
- [`flashcore/db/database.py#L533`](https://github.com/ImmortalDemonGod/flashcore/blob/5d96cc4406821652303022d0633d15a29a02862e/flashcore/db/database.py#L533)
- [`flashcore/db/database.py#L704`](https://github.com/ImmortalDemonGod/flashcore/blob/5d96cc4406821652303022d0633d15a29a02862e/flashcore/db/database.py#L704)
- [`flashcore/db/database.py#L717-L718`](https://github.com/ImmortalDemonGod/flashcore/blob/5d96cc4406821652303022d0633d15a29a02862e/flashcore/db/database.py#L717-L718)
- [`flashcore/db/database.py#L726`](https://github.com/ImmortalDemonGod/flashcore/blob/5d96cc4406821652303022d0633d15a29a02862e/flashcore/db/database.py#L726)
- [`flashcore/db/database.py#L733-L736`](https://github.com/ImmortalDemonGod/flashcore/blob/5d96cc4406821652303022d0633d15a29a02862e/flashcore/db/database.py#L733-L736)
- [`flashcore/db/database.py#L746`](https://github.com/ImmortalDemonGod/flashcore/blob/5d96cc4406821652303022d0633d15a29a02862e/flashcore/db/database.py#L746)
- [`flashcore/db/database.py#L758`](https://github.com/ImmortalDemonGod/flashcore/blob/5d96cc4406821652303022d0633d15a29a02862e/flashcore/db/database.py#L758)
- [`flashcore/db/database.py#L783-L786`](https://github.com/ImmortalDemonGod/flashcore/blob/5d96cc4406821652303022d0633d15a29a02862e/flashcore/db/database.py#L783-L786)
- [`flashcore/db/database.py#L807`](https://github.com/ImmortalDemonGod/flashcore/blob/5d96cc4406821652303022d0633d15a29a02862e/flashcore/db/database.py#L807)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`FlashcardDatabase`** (L145-L146): PASS -- 36 test(s) call `FlashcardDatabase` directly
  - `tests/test_db_coverage.py::test_safety_check_with_data`
  - `tests/test_db_coverage.py::test_safety_check_catalog_exception`
  - `tests/test_db_coverage.py::test_recreate_tables_drops_in_order`
  - `tests/test_db_coverage.py::test_backup_database_success`
  - `tests/test_db.py::test_instantiation_requires_db_path`
  - `tests/test_db.py::test_instantiation_custom_file_path`
  - `tests/test_db.py::test_instantiation_in_memory`
  - `tests/test_db.py::test_context_manager_usage`
  - `tests/test_db.py::test_read_only_mode_connection`
  - `tests/test_db.py::test_initialize_schema_on_readonly_db_fails_for_force_recreate`
- **`FlashcardDatabase.get_due_card_count`** (L176-L180): PASS -- 3 test(s) call `get_due_card_count` directly
  - `tests/test_review_manager.py::test_get_due_card_count_calls_db`
  - `tests/test_review_manager.py::test_e2e_session_flow`
  - `tests/test_db_errors.py::test_get_due_card_count_handles_db_error`
- **`FlashcardDatabase.get_due_cards`** (L400-L407): PASS -- 3 test(s) call `get_due_cards` directly
  - `tests/test_db.py::test_get_due_cards_logic`
  - `tests/test_db_errors.py::test_get_due_cards_handles_db_error`
  - `tests/test_db_errors.py::test_get_due_cards_handles_validation_error`
- **`FlashcardDatabase.get_database_stats`** (L416): FAIL -- WARNING: No tests import or call `get_database_stats`
- **`FlashcardDatabase._update_card_after_review`** (L453-L462): FAIL -- WARNING: No tests import or call `_update_card_after_review`
- **`FlashcardDatabase._execute_review_transaction`** (L467): FAIL -- WARNING: No tests import or call `_execute_review_transaction`
- **`FlashcardDatabase.add_review_and_update_card`** (L533): PASS -- 19 test(s) call `add_review_and_update_card` directly
  - `tests/test_review_manager.py::test_e2e_session_flow`
  - `tests/test_db.py::test_get_due_cards_logic`
  - `tests/test_db.py::test_add_review_success`
  - `tests/test_db.py::test_add_review_fk_violation`
  - `tests/test_db.py::test_add_review_check_constraint_violation`
  - `tests/test_db.py::test_add_reviews_individually`
  - `tests/test_db.py::test_add_review_transactionality`
  - `tests/test_db.py::test_get_reviews_for_card`
  - `tests/test_db.py::test_get_latest_review_for_card`
  - `tests/test_db.py::test_get_all_reviews_with_data_and_filtering`

**Coverage summary:** 4/7 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | FlashcardDatabase.get_due_cards compares next_due_date again... | symbol | 39 test(s) call `FlashcardDatabase.get_due_cards`, `FlashcardDatabase` | PASS VERIFIED |
| 2 | FlashcardDatabase persists the FSRS step via the cards upser... | symbol | 36 test(s) call `FlashcardDatabase` | PASS VERIFIED |
| 3 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 2 verified, 0 unverified, 1 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (4/7 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Timestamp due predicates and step persistence
