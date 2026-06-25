# AIV Evidence File (v1.0)

**File:** `tests/test_db_errors.py`
**Commit:** `e6af49a`
**Previous:** `22523fc`
**Generated:** 2026-06-25T16:37:50Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_db_errors.py"
  classification_rationale: "R1"
  classified_by: "Claude"
  classified_at: "2026-06-25T16:37:50Z"
```

## Claim(s)

1. Test ensures MarshallingError is raised for invalid row
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L150](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L150)
- **Requirements Verified:** Error handling test

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`e6af49a`](https://github.com/ImmortalDemonGod/flashcore/tree/e6af49aa162fc45ccb085df66254c2d70a3464cb))

- [`tests/test_db_errors.py#L3-L20`](https://github.com/ImmortalDemonGod/flashcore/blob/e6af49aa162fc45ccb085df66254c2d70a3464cb/tests/test_db_errors.py#L3-L20)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`test_db_row_to_review_missing_rating_raises_marshalling_error`** (L3-L20): FAIL -- WARNING: No tests import or call `test_db_row_to_review_missing_rating_raises_marshalling_error`

**Coverage summary:** 0/1 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 13 error(s)
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | Test ensures MarshallingError is raised for invalid row | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (0/1 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Test MarshallingError on missing rating
