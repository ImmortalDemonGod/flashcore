# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/flashcore |
| **Change ID** | flashcore-f170-adopt-8de67de |
| **Commits** | `8de67de7809d9862d9e47473823bbb7904363cec` |
| **Head SHA** | `438931cb7225f1cf89fbe356c871f7b2aca3cedc` |
| **Base SHA** | `b15bcde51faa961d87a7d177ef00f5360e539213` (8de67de^) |
| **Risk tier** | R1 |
| **Classification rationale** | R1: out-of-band operator commit that added a new integration test (`tests/test_review_manager_integration.py`) and its companion evidence file. The test verifies that after submitting a review for card1, `get_next_card()` returns card2 (earliest due) rather than card1 (whose `modified_at` would have been bumped if the F170 bug were still present). At HEAD the bug is absent and the test passes. Full suite is 496 passed, 1 skipped with no regressions. |

## Claims

1. At `8de67de^` (`b15bcde51f`), `tests/test_review_manager_integration.py` as authored by `8de67de` did not exist in that exact form — `8de67de` is its first creation commit.
2. Commit `8de67de` added exactly one Python test file (`tests/test_review_manager_integration.py`) and one markdown evidence file; it modified no production code.
3. `test_review_flow_maintains_due_date_order` verifies the F170 invariant end-to-end: after reviewing card1 (which updates `modified_at`), the next card returned is card2 (earliest `next_due_date`), not card1.
4. At HEAD (`438931cb`), the F170 sort bug is **absent**: `grep -rn "sorted.*modified_at" flashcore/*.py` exits 1 (no matches).
5. At HEAD, `test_review_flow_maintains_due_date_order` **PASSES** — `review_queue[0]` ordering is preserved correctly.
6. At HEAD, all 28 review-manager tests pass and the full suite is **496 passed, 1 skipped** with no regressions introduced by `8de67de`.

## Evidence

### Class A – Behavioral / Direct

**Baseline (`8de67de^` — `b15bcde51faa961d87a7d177ef00f5360e539213`):**

File `tests/test_review_manager_integration.py` as introduced by `8de67de` did not exist at the baseline commit:

```
git show 8de67de^:tests/test_review_manager_integration.py
→ (no output — file was not present at b15bcde^)
```

**HEAD (`438931cb7225f1cf89fbe356c871f7b2aca3cedc`) — live validation:**

F170 sort bug absent at HEAD:

```
grep -rn "sorted.*modified_at" flashcore/*.py
→ exit 1 (no matches) — bug is ABSENT at HEAD
```

Integration test run:

```
pytest tests/test_review_manager_integration.py -v
  collected 1 item
  tests/test_review_manager_integration.py::test_review_flow_maintains_due_date_order PASSED
  1 passed in 0.02s
```

All review-manager tests:

```
pytest tests/test_review_manager.py tests/test_review_manager_order.py \
       tests/test_review_manager_ordering.py tests/test_review_manager_integration.py -v
  collected 28 items — 28 passed in 0.38s
```

F170 GOAL test: `tests/test_review_manager_order.py::test_review_manager_ordering_by_due_date` PASSED

Full suite: **496 passed, 1 skipped** in 32.44s.

Evidence artifact: `.github/aiv-packets/evidence/flashcore-f170/adopt_8de67de_class_a.txt`

### Class B – Referential (SHA-pinned, line-anchored)

Commit `8de67de7809d9862d9e47473823bbb7904363cec` — diff summary:

- **Added** `tests/test_review_manager_integration.py` (36 lines):
  - `mock_db` fixture (L7–L20): creates three `Card` objects with `next_due_date` at +1/+2/+3 days; `update_review` side-effect bumps `modified_at` on the card, simulating a real review event
  - `mock_scheduler` helper (L22–L24): returns a bare `MagicMock` scheduler
  - `test_review_flow_maintains_due_date_order` (L26–L36): calls `initialize_session()`, asserts `get_next_card()` returns card1, calls `submit_review(card1, rating=1)`, then asserts `get_next_card()` returns card2 — proving that post-review `modified_at` update does **not** re-sort the queue
- **Added** `.github/aiv-evidence/EVIDENCE_TESTS_TEST_REVIEW_MANAGER_INTEGRATION.md` (79 lines): AIV evidence file (v1.0) for the test

SHA-pinned line anchor:
[`tests/test_review_manager_integration.py#L26-L36`](https://github.com/ImmortalDemonGod/flashcore/blob/8de67de7809d9862d9e47473823bbb7904363cec/tests/test_review_manager_integration.py#L26-L36)

### Class C – Negative Evidence

**Searched for and did NOT find:**

- Any production Python file modified by `8de67de`:
  ```
  git show 8de67de --name-only | grep "\.py$" | grep -v "^tests/"
  → No matches — 8de67de only touched tests/ and .github/aiv-evidence/
  ```

- The `sorted.*modified_at` sort override at HEAD (F170 bug — absent):
  ```
  grep -rn "sorted.*modified_at" flashcore/*.py
  → exit 1 (no matches)
  ```

- Any modification to previously-existing test files:
  ```
  git show 8de67de --name-only | grep "^tests/" | grep "\.py$"
  → tests/test_review_manager_integration.py (ADDED, not modified)
  ```
  No pre-existing test file was modified or deleted by `8de67de`.

- Any test regression at HEAD: 496 passed, 1 skipped, 0 failed.

**Bug catalog coverage:** `8de67de` addresses the F170 sort-override bug (Bug B1 in the pipeline's bug catalog). No additional bugs were identified in the introduced test code.

### Class D – Static Analysis

Executed at HEAD (`438931cb7225f1cf89fbe356c871f7b2aca3cedc`):

```
mypy flashcore/review_manager.py --ignore-missing-imports
→ Success: no issues found in 1 source file

ruff check tests/test_review_manager_integration.py
→ All checks passed!
```

`tests/test_review_manager_integration.py` passes ruff linting with no warnings or errors. The production module `flashcore/review_manager.py` is mypy-clean at HEAD.

### Class E – Intent Alignment

Commit `8de67de` added an integration test that exercises the F170 finding's behavioral invariant end-to-end: that after any review event updates a card's `modified_at`, the review queue continues to prioritize cards by `next_due_date ASC` (the scheduler's intended ordering) rather than sorting by `modified_at` (the defect documented in F170). This test directly validates the behavioral contract broken by the `sorted(due_cards, key=lambda c: c.modified_at)` line identified at `flashcore/review_manager.py:109`.

The operator's edit is a refinement of the same intent that drove the F170 fix — it strengthens the evidence chain by adding a submit-review-flow scenario that unit tests cannot cover.

> **Canonical intent URL (SHA-pinned):**
> https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180

The audit record at L180 is the F170 finding: `initialize_session()` re-sorts due cards by `modified_at` instead of preserving the DB's `next_due_date ASC NULLS FIRST` ordering. `8de67de` adds an integration-level test scenario that proves the fix holds through a complete review cycle, aligning directly with the finding's verification goal.

### Class F – Provenance

Git chain-of-custody for files added by `8de67de`:

```
git log --oneline --follow -- tests/test_review_manager_integration.py
46274bd test: fix integration test for due date ordering   ← later refinement of fixture
8de67de test(flashcore-f170-tests): tests/test_review_manager_integration.py  ← ADOPTED (created file)

git log --oneline --follow -- .github/aiv-evidence/EVIDENCE_TESTS_TEST_REVIEW_MANAGER_INTEGRATION.md
46274bd test: fix integration test for due date ordering
8de67de test(flashcore-f170-tests): tests/test_review_manager_integration.py  ← ADOPTED (created file)
```

`8de67de` was authored by `Claude <noreply@anthropic.com>` on 2026-06-25T21:38:55Z as an out-of-band operator commit mid-drive. Commit `46274bd` subsequently refined the test fixture (updated `mock_scheduler` from a bare function to a `pytest.fixture` decorator and corrected the `submit_review` call signature). Both commits are already on the PR branch and adopted into the evidence chain.

This adoption packet is committed via `git -c core.hooksPath=/dev/null commit` (packet-only commit per pipeline rules).

Review-manager test file chain-of-custody (files exercising the F170 invariant):
- `tests/test_review_manager_order.py` — F170 GOAL test; passes at HEAD
- `tests/test_review_manager_ordering.py` — unit-level due-date order test; passes at HEAD
- `tests/test_review_manager_integration.py` — integration flow test (added by `8de67de`, refined by `46274bd`); passes at HEAD
- `tests/test_review_manager.py` — 25 unit tests; all pass at HEAD; not touched by `8de67de`

## Machine-checkable data

```json
{
  "change_id": "flashcore-f170-adopt-8de67de",
  "adopted_commit": "8de67de7809d9862d9e47473823bbb7904363cec",
  "base_sha": "b15bcde51faa961d87a7d177ef00f5360e539213",
  "head_sha": "438931cb7225f1cf89fbe356c871f7b2aca3cedc",
  "risk_tier": "R1",
  "files_added_by_8de67de": [
    "tests/test_review_manager_integration.py",
    ".github/aiv-evidence/EVIDENCE_TESTS_TEST_REVIEW_MANAGER_INTEGRATION.md"
  ],
  "production_code_modified": false,
  "existing_tests_modified": false,
  "test_file_is_new_python": true,
  "f170_sort_bug_at_head": false,
  "f170_goal_test_passes_at_head": true,
  "integration_test_passes_at_head": true,
  "review_manager_tests_at_head": {"passed": 28, "failed": 0},
  "tests_at_head": {"passed": 496, "skipped": 1, "failed": 0},
  "static_analysis": {"mypy": "success", "ruff": "clean"},
  "canonical_intent_url": "https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180",
  "evidence_artifact": ".github/aiv-packets/evidence/flashcore-f170/adopt_8de67de_class_a.txt"
}
```
