# AIV Evidence File (v1.0)

**File:** `tests/conftest.bug-catalog.md`
**Commit:** `8668aff`
**Generated:** 2026-06-24T06:36:16Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/conftest.bug-catalog.md"
  classification_rationale: "R1: documentation artifact that anchors the test strategy; no logic changes"
  classified_by: "Miguel Ingram"
  classified_at: "2026-06-24T06:36:16Z"
```

## Claim(s)

1. Bug catalog documents BUG-01 (NameError: timedelta not imported), BUG-02 (non-deterministic next_due), and BUG-03 (sys.path leak) with blast-radius ranking and explicit skip list
2. Skipped section enumerates four explicitly deferred bugs with deferral justifications
3. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L18](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L18)
- **Requirements Verified:** design-tests skill: deliver bug-catalog.md as first commit before writing tests

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`8668aff`](https://github.com/ImmortalDemonGod/flashcore/tree/8668affb1dc5e2aa016d350c0e49a05fef086c94))

- [`tests/conftest.bug-catalog.md#L1-L115`](https://github.com/ImmortalDemonGod/flashcore/blob/8668affb1dc5e2aa016d350c0e49a05fef086c94/tests/conftest.bug-catalog.md#L1-L115)

### Class A (Execution Evidence)

**WARNING:** No tests found that directly import or reference the changed file.
This file has no claim-specific execution evidence.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Found 1 error in 1 file (errors prevented further checking)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | Bug catalog documents BUG-01 (NameError: timedelta not impor... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | Skipped section enumerates four explicitly deferred bugs wit... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 3 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 3 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), pytest (no claim-specific tests found).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Bug catalog for conftest.py F8 finding — missing timedelta import and related fixture risks
