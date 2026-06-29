# AIV Evidence File (v1.0)

**File:** `flashcore/cli/review_ui.py`
**Commit:** `103312d`
**Previous:** `1287d7c`
**Generated:** 2026-06-29T20:45:06Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "flashcore/cli/review_ui.py"
  classification_rationale: "R1 CLI in the review path"
  classified_by: "Miguel Ingram"
  classified_at: "2026-06-29T20:45:06Z"
```

## Claim(s)

1. start_review_flow computes days-until-due from next_due_date.date() so it works with datetime dues
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/flashcore/pull/58](https://github.com/ImmortalDemonGod/flashcore/pull/58)
- **Requirements Verified:** The CLI must handle datetime next_due_date when printing days-until-due

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`103312d`](https://github.com/ImmortalDemonGod/flashcore/tree/103312d2e75181178b9c761c1cf8babdbb7c7807))

- [`flashcore/cli/review_ui.py#L125-L127`](https://github.com/ImmortalDemonGod/flashcore/blob/103312d2e75181178b9c761c1cf8babdbb7c7807/flashcore/cli/review_ui.py#L125-L127)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`start_review_flow`** (L125-L127): PASS -- 11 test(s) call `start_review_flow` directly
  - `tests/cli/test_review_ui.py::test_start_review_flow_no_due_cards`
  - `tests/cli/test_review_ui.py::test_start_review_flow_with_one_card`
  - `tests/cli/test_review_ui.py::test_start_review_flow_invalid_rating_input`
  - `tests/cli/test_review_ui.py::test_start_review_flow_submit_review_exception`
  - `tests/cli/test_review_ui.py::test_start_review_flow_card_without_next_due_date`
  - `tests/cli/test_review_ui.py::test_start_review_flow_submit_returns_none`
  - `tests/cli/test_review_ui.py::test_all_submit_review_fail_output_omits_well_done_guards_against_false_success_message`
  - `tests/cli/test_review_ui.py::test_persistent_submit_failure_retries_same_card_guards_against_infinite_retry_loop`
  - `tests/cli/test_review_ui.py::test_start_review_flow_all_fail_suppresses_well_done`
  - `tests/cli/test_review_ui.py::test_start_review_flow_success_emits_well_done`

**Coverage summary:** 1/1 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | start_review_flow computes days-until-due from next_due_date... | symbol | 11 test(s) call `start_review_flow` | PASS VERIFIED |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 1 verified, 0 unverified, 1 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (1/1 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

CLI days-until-due from datetime due
