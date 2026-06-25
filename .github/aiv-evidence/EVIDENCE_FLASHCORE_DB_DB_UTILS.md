# AIV Evidence File (v1.0)

**File:** `flashcore/db/db_utils.py`
**Commit:** `9fdf978`
**Previous:** `d4433ab`
**Generated:** 2026-06-25T17:05:59Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "flashcore/db/db_utils.py"
  classification_rationale: "high"
  classified_by: "Claude"
  classified_at: "2026-06-25T17:05:59Z"
```

## Claim(s)

1. db_row_to_review now wraps ValidationError as MarshallingError, aligning error handling with other converters
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L150](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L150)
- **Requirements Verified:** error handling consistency

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`9fdf978`](https://github.com/ImmortalDemonGod/flashcore/tree/9fdf978e7a608a573c1698cbc055db54f284c98f))

- [`flashcore/db/db_utils.py#L1-L199`](https://github.com/ImmortalDemonGod/flashcore/blob/9fdf978e7a608a573c1698cbc055db54f284c98f/flashcore/db/db_utils.py#L1-L199)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`transform_db_row_for_card`** (L1-L199): FAIL -- WARNING: No tests import or call `transform_db_row_for_card`
- **`card_to_db_params_list`** (unknown): FAIL -- WARNING: No tests import or call `card_to_db_params_list`
- **`db_row_to_card`** (unknown): FAIL -- WARNING: No tests import or call `db_row_to_card`
- **`review_to_db_params_tuple`** (unknown): FAIL -- WARNING: No tests import or call `review_to_db_params_tuple`
- **`db_row_to_review`** (unknown): PASS -- 2 test(s) call `db_row_to_review` directly
  - `tests/test_db_row_to_review_error_handling.py::test_db_row_to_review_missing_validation_error_wrapper`
  - `tests/test_db_row_to_review_error.py::test_db_row_to_review_missing_validationerror_wrapper`
- **`session_to_db_params_tuple`** (unknown): PASS -- 1 test(s) call `session_to_db_params_tuple` directly
  - `tests/test_db_coverage.py::test_session_to_db_params_tuple_with_all_fields`

**Coverage summary:** 2/6 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 33 error(s)
- **mypy:** Found 3 errors in 1 file (checked 1 source file)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | db_row_to_review now wraps ValidationError as MarshallingErr... | symbol | 2 test(s) call `db_row_to_review` | PASS VERIFIED |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 1 verified, 0 unverified, 1 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (2/6 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

wrap Review ValidationError
