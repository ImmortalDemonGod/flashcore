# AIV Evidence File (v1.0)

**File:** `flashcore/cli/_vet_logic.bug-catalog.md`
**Commit:** `e0a7b39`
**Previous:** `e0a7b39`
**Generated:** 2026-06-25T17:44:50Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "flashcore/cli/_vet_logic.bug-catalog.md"
  classification_rationale: "primary-deliverable-dependency"
  classified_by: "Claude"
  classified_at: "2026-06-25T17:44:50Z"
```

## Claim(s)

1. Adds bug catalog for missing score field removal
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L93](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L93)
- **Requirements Verified:** test design

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`e0a7b39`](https://github.com/ImmortalDemonGod/flashcore/tree/e0a7b399e73eab2f4becb70b56f161628f7c9afb))

- [`flashcore/cli/_vet_logic.bug-catalog.md#L1`](https://github.com/ImmortalDemonGod/flashcore/blob/e0a7b399e73eab2f4becb70b56f161628f7c9afb/flashcore/cli/_vet_logic.bug-catalog.md#L1)
- [`flashcore/cli/_vet_logic.bug-catalog.md#L3-L4`](https://github.com/ImmortalDemonGod/flashcore/blob/e0a7b399e73eab2f4becb70b56f161628f7c9afb/flashcore/cli/_vet_logic.bug-catalog.md#L3-L4)
- [`flashcore/cli/_vet_logic.bug-catalog.md#L8-L10`](https://github.com/ImmortalDemonGod/flashcore/blob/e0a7b399e73eab2f4becb70b56f161628f7c9afb/flashcore/cli/_vet_logic.bug-catalog.md#L8-L10)
- [`flashcore/cli/_vet_logic.bug-catalog.md#L12`](https://github.com/ImmortalDemonGod/flashcore/blob/e0a7b399e73eab2f4becb70b56f161628f7c9afb/flashcore/cli/_vet_logic.bug-catalog.md#L12)
- [`flashcore/cli/_vet_logic.bug-catalog.md#L14`](https://github.com/ImmortalDemonGod/flashcore/blob/e0a7b399e73eab2f4becb70b56f161628f7c9afb/flashcore/cli/_vet_logic.bug-catalog.md#L14)
- [`flashcore/cli/_vet_logic.bug-catalog.md#L16`](https://github.com/ImmortalDemonGod/flashcore/blob/e0a7b399e73eab2f4becb70b56f161628f7c9afb/flashcore/cli/_vet_logic.bug-catalog.md#L16)
- [`flashcore/cli/_vet_logic.bug-catalog.md#L18-L20`](https://github.com/ImmortalDemonGod/flashcore/blob/e0a7b399e73eab2f4becb70b56f161628f7c9afb/flashcore/cli/_vet_logic.bug-catalog.md#L18-L20)

### Class A (Execution Evidence)

**WARNING:** No tests found that directly import or reference the changed file.
This file has no claim-specific execution evidence.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Found 1 error in 1 file (errors prevented further checking)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | Adds bug catalog for missing score field removal | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), pytest (no claim-specific tests found).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Bug catalog for missing score field
