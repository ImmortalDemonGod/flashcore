# AIV Evidence File (v1.0)

**File:** `flashcore/db/db_utils.py`
**Commit:** `bc40669`
**Generated:** 2026-06-25T16:55:01Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "flashcore/db/db_utils.py"
  classification_rationale: "medium"
  classified_by: "Claude"
  classified_at: "2026-06-25T16:55:01Z"
```

## Claim(s)

1. db_row_to_review now raises MarshallingError on validation failures, aligning error handling with other converters
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L150](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L150)
- **Requirements Verified:** error-handling

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`bc40669`](https://github.com/ImmortalDemonGod/flashcore/tree/bc40669a8bf8d0eb52d4ff8c2331c9e5ca99b33e))

- [`flashcore/db/db_utils.py#L153-L163`](https://github.com/ImmortalDemonGod/flashcore/blob/bc40669a8bf8d0eb52d4ff8c2331c9e5ca99b33e/flashcore/db/db_utils.py#L153-L163)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`db_row_to_review`** (L153-L163): PASS -- 2 test(s) call `db_row_to_review` directly
  - `tests/test_db_row_to_review_error_handling.py::test_db_row_to_review_missing_validation_error_wrapper`
  - `tests/test_db_row_to_review_error.py::test_db_row_to_review_missing_validationerror_wrapper`

**Coverage summary:** 1/1 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | db_row_to_review now raises MarshallingError on validation f... | symbol | 2 test(s) call `db_row_to_review` | PASS VERIFIED |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 1 verified, 0 unverified, 1 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (1/1 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

add MarshallingError wrapper to db_row_to_review
