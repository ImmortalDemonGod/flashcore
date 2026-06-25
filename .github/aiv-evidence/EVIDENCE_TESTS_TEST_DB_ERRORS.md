# AIV Evidence File (v1.0)

**File:** `tests/test_db_errors.py`
**Commit:** `4e4942a`
**Previous:** `24efa24`
**Generated:** 2026-06-25T19:45:36Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_db_errors.py"
  classification_rationale: "high"
  classified_by: "Claude"
  classified_at: "2026-06-25T19:45:36Z"
```

## Claim(s)

1. tests/test_db_errors.py verifies MarshallingError raised when rating missing
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L150](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L150)
- **Requirements Verified:** R2

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`4e4942a`](https://github.com/ImmortalDemonGod/flashcore/tree/4e4942ae859c67c9ecbc22191faf11db90fc35e2))

- [`tests/test_db_errors.py#L2-L10`](https://github.com/ImmortalDemonGod/flashcore/blob/4e4942ae859c67c9ecbc22191faf11db90fc35e2/tests/test_db_errors.py#L2-L10)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`test_db_row_to_review_missing_rating_raises_marshalling_error`** (L2-L10): FAIL -- WARNING: No tests import or call `test_db_row_to_review_missing_rating_raises_marshalling_error`

**Coverage summary:** 0/1 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Found 3 errors in 1 file (checked 1 source file)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | tests/test_db_errors.py verifies MarshallingError raised whe... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (0/1 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

adds test for db_row_to_review error handling
