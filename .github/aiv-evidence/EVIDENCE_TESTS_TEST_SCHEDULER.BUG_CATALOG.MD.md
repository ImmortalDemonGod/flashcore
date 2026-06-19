# AIV Evidence File (v1.0)

**File:** `tests/test_scheduler.bug-catalog.md`
**Commit:** `4739dde`
**Generated:** 2026-06-19T04:47:00Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_scheduler.bug-catalog.md"
  classification_rationale: "R1: no logic changes; catalog is the planning artifact governing the subsequent test code commit"
  classified_by: "Claude"
  classified_at: "2026-06-19T04:47:00Z"
```

## Claim(s)

1. catalog identifies B1 (last_review=due yields elapsed_days=0 for on-time FSRS reviews) as sole in-scope finding; six entries in Skipped section with explicit reasons
2. catalog designates Path A (last_review_date transient field on Card) as the correction path with one-sentence rationale contrasting Path B approximation limitations
3. test design section for B1-A and B1-B passes all four design-tests criteria: failure under non-trivial defect introduction, pass under behavior-preserving refactor, observable behavior, public interface only
4. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/4a15a08/.aiv/launch-briefs/pr-f169-fsrs-elapsed-days/pr-f169-fsrs-elapsed-days-completion-contract.md](https://github.com/ImmortalDemonGod/flashcore/blob/4a15a08/.aiv/launch-briefs/pr-f169-fsrs-elapsed-days/pr-f169-fsrs-elapsed-days-completion-contract.md)
- **Requirements Verified:** VERIFY [1]-[2]: test contracts for test_on_time_review_elapsed_days_positive and test_on_time_vs_same_day_review_stability_distinct established in catalog before test code

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`4739dde`](https://github.com/ImmortalDemonGod/flashcore/tree/4739dde568fe5bd3c6a55855792f2a49a4c89deb))

- [`tests/test_scheduler.bug-catalog.md#L1-L249`](https://github.com/ImmortalDemonGod/flashcore/blob/4739dde568fe5bd3c6a55855792f2a49a4c89deb/tests/test_scheduler.bug-catalog.md#L1-L249)

### Class A (Execution Evidence)

**WARNING:** No tests found that directly import or reference the changed file.
This file has no claim-specific execution evidence.

### Code Quality (Linting & Types)

- **ruff:** 0 error(s)
- **mypy:** Found 1 error in 1 file (errors prevented further checking)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | catalog identifies B1 (last_review=due yields elapsed_days=0... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | catalog designates Path A (last_review_date transient field ... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 3 | test design section for B1-A and B1-B passes all four design... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 4 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 4 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), pytest (no claim-specific tests found).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Design-tests catalog for F169 elapsed_days scheduler finding
