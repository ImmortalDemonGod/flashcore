# AIV Evidence File (v1.0)

**File:** `flashcore/scheduler.py`
**Commit:** `b5e1c4b`
**Generated:** 2026-06-18T19:57:39Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R2
  sod_mode: S1
  critical_surfaces: []
  blast_radius: "flashcore/scheduler.py"
  classification_rationale: "Touches the core scheduling engine consumed by review_processor; behavioral change to every real review -> component blast radius. Additive optional param defaults to prior behavior, but production output changes, so round up to R2 per spec."
  classified_by: "Claude"
  classified_at: "2026-06-18T19:57:39Z"
```

## Claim(s)

1. compute_next_state accepts an optional last_review_ts; when provided, fsrs_card.last_review is set from it (UTC-normalized) rather than the due date
2. An on-time review (review_ts == next_due_date) with a prior-review timestamp 7 days earlier yields SchedulerOutput.elapsed_days == 7, not 0
3. When last_review_ts is None, behavior is unchanged (new cards and history-less callers fall back to the due-date approximation)
4. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/blob/b5e1c4b983b33602e8531340f382c72626a0fb59/flashcore/scheduler.py#L212](https://github.com/ImmortalDemonGod/flashcore/blob/b5e1c4b983b33602e8531340f382c72626a0fb59/flashcore/scheduler.py#L212)
- **Requirements Verified:** FSRS retrievability must derive from the real interval since the prior review, not the due date (corpus C2)

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`b5e1c4b`](https://github.com/ImmortalDemonGod/flashcore/tree/b5e1c4b983b33602e8531340f382c72626a0fb59))

- [`flashcore/scheduler.py#L191-L195`](https://github.com/ImmortalDemonGod/flashcore/blob/b5e1c4b983b33602e8531340f382c72626a0fb59/flashcore/scheduler.py#L191-L195)
- [`flashcore/scheduler.py#L199-L211`](https://github.com/ImmortalDemonGod/flashcore/blob/b5e1c4b983b33602e8531340f382c72626a0fb59/flashcore/scheduler.py#L199-L211)
- [`flashcore/scheduler.py#L228-L234`](https://github.com/ImmortalDemonGod/flashcore/blob/b5e1c4b983b33602e8531340f382c72626a0fb59/flashcore/scheduler.py#L228-L234)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`FSRS_Scheduler`** (L191-L195): PASS -- 13 test(s) call `FSRS_Scheduler` directly
  - `tests/test_session_analytics_gaps.py::test_review_session_manager_now_creates_session_objects`
  - `tests/test_session_analytics_gaps.py::test_review_workflows_now_have_session_integration`
  - `tests/test_session_analytics_gaps.py::test_missing_session_lifecycle_management`
  - `tests/test_session_analytics_gaps.py::test_missing_session_performance_analytics`
  - `tests/test_session_analytics_gaps.py::test_missing_real_time_session_tracking`
  - `tests/test_review_manager.py::test_e2e_session_flow`
  - `tests/test_scheduler.py::test_mature_card_lapse`
  - `tests/test_scheduler.py::test_config_impact_on_scheduling`
  - `tests/test_rating_system_inconsistency.py::test_review_manager_uses_unified_rating_scale`
  - `tests/test_rating_system_inconsistency.py::test_review_all_logic_uses_unified_rating_scale`
- **`FSRS_Scheduler.compute_next_state`** (L199-L211): PASS -- 12 test(s) call `compute_next_state` directly
  - `tests/test_scheduler.py::test_first_review_new_card`
  - `tests/test_scheduler.py::test_invalid_rating_input`
  - `tests/test_scheduler.py::test_rating_impact_on_interval`
  - `tests/test_scheduler.py::test_multiple_reviews_stability_increase`
  - `tests/test_scheduler.py::test_review_lapsed_card`
  - `tests/test_scheduler.py::test_review_early_card`
  - `tests/test_scheduler.py::test_mature_card_lapse`
  - `tests/test_scheduler.py::test_compute_next_state_with_unknown_fsrs_state`
  - `tests/test_scheduler.py::test_compute_next_state_review_card_fallback_no_now_kw`
  - `tests/test_scheduler.py::test_config_impact_on_scheduling`

**Coverage summary:** 2/2 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 0 error(s)
- **mypy:** 

### Class C (Negative Evidence)

**Search methodology:** Ran `git diff --cached` and scanned for regression indicators.

- Test file deletions: **none**
- Test file modifications: **none**
- Deleted assertions (`assert` removals in diff): **none found**
- Added skip markers (`@pytest.mark.skip`, `@unittest.skip`): **none found**

### Class F (Provenance Evidence)

**Test file chain-of-custody:**

| File | Commits | Created By | Last Modified By | Assertions |
|------|---------|------------|------------------|------------|
| `tests/test_rating_system_inconsistency.py` | 8 | Miguel Ingram (a82479a) | Miguel Ingram (7666fca) | 24 |
| `tests/test_review_logic_duplication.py` | 8 | Miguel Ingram (a82479a) | Miguel Ingram (1a30b74) | 31 |
| `tests/test_review_manager.py` | 10 | Miguel Ingram (a82479a) | Miguel Ingram (b9b2383) | 61 |
| `tests/test_review_processor.py` | 12 | Miguel Ingram (a82479a) | Miguel Ingram (8ad8660) | 46 |
| `tests/test_scheduler.py` | 1 | Miguel Ingram (667ecd2) | Miguel Ingram (667ecd2) | 53 |
| `tests/test_session_analytics_gaps.py` | 8 | Miguel Ingram (a82479a) | Miguel Ingram (ac4561a) | 32 |

**Recent test directory history** (`git log --oneline -5 -- tests/`):

```
6fdbab2 style: fix trailing whitespace and reformat tests/test_session_manager.py with black -l 79
ac4561a style: fix trailing whitespace and reformat tests/test_session_analytics_gaps.py with black -l 79
8ad8660 style: fix trailing whitespace and reformat tests/test_review_processor.py with black -l 79
b9b2383 style: fix trailing whitespace and reformat tests/test_review_manager.py with black -l 79
1a30b74 style: fix trailing whitespace and reformat tests/test_review_logic_duplication.py with black -l 79
```

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | compute_next_state accepts an optional last_review_ts; when ... | symbol | 12 test(s) call `FSRS_Scheduler.compute_next_state` | PASS VERIFIED |
| 2 | An on-time review (review_ts == next_due_date) with a prior-... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 3 | When last_review_ts is None, behavior is unchanged (new card... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 4 | No existing tests were modified or deleted during this chang... | structural | Class C: all structural indicators clean | PASS VERIFIED |

**Verdict summary:** 2 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (2/2 symbols verified), anti-cheat scan.
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Scheduler measures elapsed days against the prior review timestamp
