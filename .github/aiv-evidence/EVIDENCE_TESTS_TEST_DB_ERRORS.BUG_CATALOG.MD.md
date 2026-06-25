# AIV Evidence File (v1.0)

**File:** `tests/test_db_errors.bug-catalog.md`
**Commit:** `c3f6adc`
**Previous:** `766f26f`
**Generated:** 2026-06-25T16:37:15Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_db_errors.bug-catalog.md"
  classification_rationale: "R1"
  classified_by: "Claude"
  classified_at: "2026-06-25T16:37:15Z"
```

## Claim(s)

1. Ensure db_row_to_review raises MarshallingError on invalid rows
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L150](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L150)
- **Requirements Verified:** Error handling coverage

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`c3f6adc`](https://github.com/ImmortalDemonGod/flashcore/tree/c3f6adc91a6a7d80393fb434a37ac845960924cf))

- [`tests/test_db_errors.bug-catalog.md#L4`](https://github.com/ImmortalDemonGod/flashcore/blob/c3f6adc91a6a7d80393fb434a37ac845960924cf/tests/test_db_errors.bug-catalog.md#L4)
- [`tests/test_db_errors.bug-catalog.md#L6`](https://github.com/ImmortalDemonGod/flashcore/blob/c3f6adc91a6a7d80393fb434a37ac845960924cf/tests/test_db_errors.bug-catalog.md#L6)
- [`tests/test_db_errors.bug-catalog.md#L8-L10`](https://github.com/ImmortalDemonGod/flashcore/blob/c3f6adc91a6a7d80393fb434a37ac845960924cf/tests/test_db_errors.bug-catalog.md#L8-L10)
- [`tests/test_db_errors.bug-catalog.md#L12`](https://github.com/ImmortalDemonGod/flashcore/blob/c3f6adc91a6a7d80393fb434a37ac845960924cf/tests/test_db_errors.bug-catalog.md#L12)
- [`tests/test_db_errors.bug-catalog.md#L14`](https://github.com/ImmortalDemonGod/flashcore/blob/c3f6adc91a6a7d80393fb434a37ac845960924cf/tests/test_db_errors.bug-catalog.md#L14)
- [`tests/test_db_errors.bug-catalog.md#L16-L22`](https://github.com/ImmortalDemonGod/flashcore/blob/c3f6adc91a6a7d80393fb434a37ac845960924cf/tests/test_db_errors.bug-catalog.md#L16-L22)

### Class A (Execution Evidence)

**WARNING:** No tests found that directly import or reference the changed file.
This file has no claim-specific execution evidence.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Found 1 error in 1 file (errors prevented further checking)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | Ensure db_row_to_review raises MarshallingError on invalid r... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), pytest (no claim-specific tests found).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Bug catalog for missing MarshallingError
