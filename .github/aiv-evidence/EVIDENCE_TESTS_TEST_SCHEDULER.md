# AIV Evidence File (v1.0)

**File:** `tests/test_scheduler.py`
**Commit:** `3dde24b`
**Generated:** 2026-06-19T04:50:01Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_scheduler.py"
  classification_rationale: "R1: new test code only; no production logic changed; RED state is intentional per design-tests stage contract"
  classified_by: "Claude"
  classified_at: "2026-06-19T04:50:01Z"
```

## Claim(s)

1. elapsed_days is 0 instead of >0 when a CardState.Review card (stability=14.0, next_due_date=2024-03-15) is reviewed at 2024-03-15T10:00Z; root cause confirmed at scheduler.py:212 where last_review is assigned fsrs_card.due making the delta zero
2. Card.model_config extra='forbid' raises pydantic ValidationError when last_review_date is supplied to Card constructor; confirms Path A transient field is absent from flashcore/models.py at time of RED-test commit
3. 15 pre-existing tests/test_scheduler.py tests continue to pass after adding two intentionally-failing assertions (17 collected, 2 failed, 15 passed); baseline preserved with no regression
4. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/4a15a08/.aiv/launch-briefs/pr-f169-fsrs-elapsed-days/pr-f169-fsrs-elapsed-days-completion-contract.md](https://github.com/ImmortalDemonGod/flashcore/blob/4a15a08/.aiv/launch-briefs/pr-f169-fsrs-elapsed-days/pr-f169-fsrs-elapsed-days-completion-contract.md)
- **Requirements Verified:** VERIFY [1]: test_on_time_review_elapsed_days_positive added; VERIFY [2]: test_on_time_vs_same_day_review_stability_distinct added; VERIFY [5]: 15 existing tests still pass

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`3dde24b`](https://github.com/ImmortalDemonGod/flashcore/tree/3dde24b8bf64093a5ad412e47c8ecd0dd67212f8))

- [`tests/test_scheduler.py#L695-L803`](https://github.com/ImmortalDemonGod/flashcore/blob/3dde24b8bf64093a5ad412e47c8ecd0dd67212f8/tests/test_scheduler.py#L695-L803)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`test_on_time_review_elapsed_days_positive`** (L695-L803): FAIL -- WARNING: No tests import or call `test_on_time_review_elapsed_days_positive`
- **`test_on_time_vs_same_day_review_stability_distinct`** (unknown): FAIL -- WARNING: No tests import or call `test_on_time_vs_same_day_review_stability_distinct`

**Coverage summary:** 0/2 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 0 error(s)
- **mypy:** Found 4 errors in 3 files (checked 1 source file)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | elapsed_days is 0 instead of >0 when a CardState.Review card... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | Card.model_config extra='forbid' raises pydantic ValidationE... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 3 | 15 pre-existing tests/test_scheduler.py tests continue to pa... | structural | Class C not collected | REVIEW MANUAL REVIEW |
| 4 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 4 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (0/2 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

RED tests for F169: elapsed_days=0 on on-time FSRS Review-state card
