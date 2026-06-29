# AIV Evidence File (v1.0)

**File:** `flashcore/db/schema.py`
**Commit:** `47f0ba7`
**Generated:** 2026-06-29T20:42:51Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "flashcore/db/schema.py"
  classification_rationale: "R1 schema change in the scheduling path"
  classified_by: "Miguel Ingram"
  classified_at: "2026-06-29T20:42:51Z"
```

## Claim(s)

1. cards.next_due_date and reviews.next_due are TIMESTAMP WITH TIME ZONE and cards has a step column
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/pull/58](https://github.com/ImmortalDemonGod/flashcore/pull/58)
- **Requirements Verified:** Schema must store full timestamps and the FSRS step

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`47f0ba7`](https://github.com/ImmortalDemonGod/flashcore/tree/47f0ba7d96023bd35fbcee871a300e2bec2c7b06))

- [`flashcore/db/schema.py#L17`](https://github.com/ImmortalDemonGod/flashcore/blob/47f0ba7d96023bd35fbcee871a300e2bec2c7b06/flashcore/db/schema.py#L17)
- [`flashcore/db/schema.py#L21`](https://github.com/ImmortalDemonGod/flashcore/blob/47f0ba7d96023bd35fbcee871a300e2bec2c7b06/flashcore/db/schema.py#L21)
- [`flashcore/db/schema.py#L46`](https://github.com/ImmortalDemonGod/flashcore/blob/47f0ba7d96023bd35fbcee871a300e2bec2c7b06/flashcore/db/schema.py#L46)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`<module>`** (L17): FAIL -- WARNING: No tests import or call `<module>`

**Coverage summary:** 0/1 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | cards.next_due_date and reviews.next_due are TIMESTAMP WITH ... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (0/1 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Timestamp due columns and step column
