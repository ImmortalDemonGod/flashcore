# AIV Evidence File (v1.0)

**File:** `flashcore/cli/_vet_logic.bug-catalog.md`
**Commit:** `e2a86ef`
**Previous:** `2ce872f`
**Generated:** 2026-06-25T17:34:51Z
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
  classified_at: "2026-06-25T17:34:51Z"
```

## Claim(s)

1. Catalog documents bug where score field not removed causing validation errors
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L93](https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L93)
- **Requirements Verified:** test design

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`e2a86ef`](https://github.com/ImmortalDemonGod/flashcore/tree/e2a86ef5bbdf703ada526557f49fbcbb03713e6d))

- [`flashcore/cli/_vet_logic.bug-catalog.md#L1`](https://github.com/ImmortalDemonGod/flashcore/blob/e2a86ef5bbdf703ada526557f49fbcbb03713e6d/flashcore/cli/_vet_logic.bug-catalog.md#L1)
- [`flashcore/cli/_vet_logic.bug-catalog.md#L3-L4`](https://github.com/ImmortalDemonGod/flashcore/blob/e2a86ef5bbdf703ada526557f49fbcbb03713e6d/flashcore/cli/_vet_logic.bug-catalog.md#L3-L4)
- [`flashcore/cli/_vet_logic.bug-catalog.md#L6-L7`](https://github.com/ImmortalDemonGod/flashcore/blob/e2a86ef5bbdf703ada526557f49fbcbb03713e6d/flashcore/cli/_vet_logic.bug-catalog.md#L6-L7)
- [`flashcore/cli/_vet_logic.bug-catalog.md#L9-L10`](https://github.com/ImmortalDemonGod/flashcore/blob/e2a86ef5bbdf703ada526557f49fbcbb03713e6d/flashcore/cli/_vet_logic.bug-catalog.md#L9-L10)
- [`flashcore/cli/_vet_logic.bug-catalog.md#L12-L17`](https://github.com/ImmortalDemonGod/flashcore/blob/e2a86ef5bbdf703ada526557f49fbcbb03713e6d/flashcore/cli/_vet_logic.bug-catalog.md#L12-L17)
- [`flashcore/cli/_vet_logic.bug-catalog.md#L19-L38`](https://github.com/ImmortalDemonGod/flashcore/blob/e2a86ef5bbdf703ada526557f49fbcbb03713e6d/flashcore/cli/_vet_logic.bug-catalog.md#L19-L38)

### Class A (Execution Evidence)

**WARNING:** No tests found that directly import or reference the changed file.
This file has no claim-specific execution evidence.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Found 1 error in 1 file (errors prevented further checking)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | Catalog documents bug where score field not removed causing ... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), pytest (no claim-specific tests found).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Bug catalog for _vet_logic
