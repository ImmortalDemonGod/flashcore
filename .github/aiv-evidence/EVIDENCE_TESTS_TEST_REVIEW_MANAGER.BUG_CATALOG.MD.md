# AIV Evidence File (v1.0)

**File:** `tests/test_review_manager.bug-catalog.md`
**Commit:** `babfafdf`
**Generated:** 2026-06-25T21:35:42Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_review_manager.bug-catalog.md"
  classification_rationale: "high"
  classified_by: "Claude"
  classified_at: "2026-06-25T21:35:42Z"
```

## Claim(s)

1. Bug catalog enumerates ordering bugs
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180)
- **Requirements Verified:** testing

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`babfafdf`](https://github.com/ImmortalDemonGod/flashcore/tree/babfafdf04489082df074958cae9c065c8a8dcc5))

- [`tests/test_review_manager.bug-catalog.md#L1-L24`](https://github.com/ImmortalDemonGod/flashcore/blob/babfafdf04489082df074958cae9c065c8a8dcc5/tests/test_review_manager.bug-catalog.md#L1-L24)

### Class A (Execution Evidence)

**WARNING:** No tests found that directly import or reference the changed file.
This file has no claim-specific execution evidence.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Found 1 error in 1 file (errors prevented further checking)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | Bug catalog enumerates ordering bugs | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), pytest (no claim-specific tests found).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Bug catalog for ordering bug
