# AIV Evidence File (v1.0)

**File:** `flashcore/cli/_vet_logic.bug-catalog.md`
**Commit:** `b701d3a`
**Previous:** `87047af`
**Generated:** 2026-06-25T21:32:48Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "flashcore/cli/_vet_logic.bug-catalog.md"
  classification_rationale: "high"
  classified_by: "Claude"
  classified_at: "2026-06-25T21:32:48Z"
```

## Claim(s)

1. Identify missing score field removal bug
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L93](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L93)
- **Requirements Verified:** testing

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`b701d3a`](https://github.com/ImmortalDemonGod/flashcore/tree/b701d3a2993aa33308134600063605b38dc65c1a))

- [`flashcore/cli/_vet_logic.bug-catalog.md#L1`](https://github.com/ImmortalDemonGod/flashcore/blob/b701d3a2993aa33308134600063605b38dc65c1a/flashcore/cli/_vet_logic.bug-catalog.md#L1)
- [`flashcore/cli/_vet_logic.bug-catalog.md#L3-L4`](https://github.com/ImmortalDemonGod/flashcore/blob/b701d3a2993aa33308134600063605b38dc65c1a/flashcore/cli/_vet_logic.bug-catalog.md#L3-L4)
- [`flashcore/cli/_vet_logic.bug-catalog.md#L8-L11`](https://github.com/ImmortalDemonGod/flashcore/blob/b701d3a2993aa33308134600063605b38dc65c1a/flashcore/cli/_vet_logic.bug-catalog.md#L8-L11)
- [`flashcore/cli/_vet_logic.bug-catalog.md#L15-L22`](https://github.com/ImmortalDemonGod/flashcore/blob/b701d3a2993aa33308134600063605b38dc65c1a/flashcore/cli/_vet_logic.bug-catalog.md#L15-L22)

### Class A (Execution Evidence)

**WARNING:** No tests found that directly import or reference the changed file.
This file has no claim-specific execution evidence.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Found 1 error in 1 file (errors prevented further checking)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | Identify missing score field removal bug | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), pytest (no claim-specific tests found).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Bug catalog for vet logic
