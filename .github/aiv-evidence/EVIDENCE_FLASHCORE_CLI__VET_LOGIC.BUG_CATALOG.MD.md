# AIV Evidence File (v1.0)

**File:** `flashcore/cli/_vet_logic.bug-catalog.md`
**Commit:** `ed72871`
**Previous:** `534ce28`
**Generated:** 2026-06-25T21:42:09Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "flashcore/cli/_vet_logic.bug-catalog.md"
  classification_rationale: "primary"
  classified_by: "Claude"
  classified_at: "2026-06-25T21:42:09Z"
```

## Claim(s)

1. Bug catalog documents missing score field removal bug
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L93](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L93)
- **Requirements Verified:** test design

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`ed72871`](https://github.com/ImmortalDemonGod/flashcore/tree/ed72871739a70341b002e442074c8b347cadfee6))

- [`flashcore/cli/_vet_logic.bug-catalog.md#L1`](https://github.com/ImmortalDemonGod/flashcore/blob/ed72871739a70341b002e442074c8b347cadfee6/flashcore/cli/_vet_logic.bug-catalog.md#L1)
- [`flashcore/cli/_vet_logic.bug-catalog.md#L3-L4`](https://github.com/ImmortalDemonGod/flashcore/blob/ed72871739a70341b002e442074c8b347cadfee6/flashcore/cli/_vet_logic.bug-catalog.md#L3-L4)
- [`flashcore/cli/_vet_logic.bug-catalog.md#L7-L9`](https://github.com/ImmortalDemonGod/flashcore/blob/ed72871739a70341b002e442074c8b347cadfee6/flashcore/cli/_vet_logic.bug-catalog.md#L7-L9)
- [`flashcore/cli/_vet_logic.bug-catalog.md#L12`](https://github.com/ImmortalDemonGod/flashcore/blob/ed72871739a70341b002e442074c8b347cadfee6/flashcore/cli/_vet_logic.bug-catalog.md#L12)
- [`flashcore/cli/_vet_logic.bug-catalog.md#L15-L17`](https://github.com/ImmortalDemonGod/flashcore/blob/ed72871739a70341b002e442074c8b347cadfee6/flashcore/cli/_vet_logic.bug-catalog.md#L15-L17)

### Class A (Execution Evidence)

**WARNING:** No tests found that directly import or reference the changed file.
This file has no claim-specific execution evidence.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Found 1 error in 1 file (errors prevented further checking)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | Bug catalog documents missing score field removal bug | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), pytest (no claim-specific tests found).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Bug catalog for _vet_logic missing score handling
