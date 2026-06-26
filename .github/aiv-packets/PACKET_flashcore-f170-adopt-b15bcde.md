# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/flashcore |
| **Change ID** | flashcore-f170-adopt-b15bcde |
| **Commits** | `b15bcde51faa961d87a7d177ef00f5360e539213` |
| **Head SHA** | `fc7811a960c22876d876d2246b7e2cdbaec2c5d5` |
| **Base SHA** | `babfafdf04489082df074958cae9c065c8a8dcc5` (b15bcde^) |
| **Risk tier** | R1 |
| **Classification rationale** | R1: out-of-band operator commit that added a new unit test (`tests/test_review_manager_ordering.py`) and its companion evidence file, exercising the F170 behavioral invariant (due-date order preserved by `initialize_session()`). The test was subsequently refined by `cbefb02` into the form present at HEAD. At HEAD the F170 fix is in place, the test passes, and no regressions are introduced. |

## Claims

1. At `b15bcde^` (`babfafdf`), `tests/test_review_manager_ordering.py` did not exist — `b15bcde` is its creation commit.
2. Commit `b15bcde` added exactly one Python test file (`tests/test_review_manager_ordering.py`, 24 lines) and one markdown evidence file (`.github/aiv-evidence/EVIDENCE_TESTS_TEST_REVIEW_MANAGER_ORDERING.md`); it modified no production code.
3. `test_initialize_session_respects_due_date_order` verifies the F170 invariant: `initialize_session()` must preserve the DB's `next_due_date ASC` ordering in `review_queue`, not re-sort by `modified_at`.
4. At HEAD (`fc7811a9`), the F170 sort bug is **absent**: `grep -rn "sorted.*modified_at" flashcore/*.py` exits 1 (no matches).
5. At HEAD, `test_initialize_session_respects_due_date_order` **PASSES** — `review_queue[0]` is the earliest-due card.
6. At HEAD, all 26 review-manager tests pass and the full suite is **496 passed, 1 skipped** with no regressions introduced by `b15bcde`.

## Evidence

### Class A – Behavioral / Direct

**Baseline (`b15bcde^` — `babfafdf04489082df074958cae9c065c8a8dcc5`):**

File `tests/test_review_manager_ordering.py` did not exist at the baseline commit:

```
git show b15bcde^:tests/test_review_manager_ordering.py
→ fatal: path exists on disk, but not in 'b15bcde^'
```

**HEAD (`fc7811a960c22876d876d2246b7e2cdbaec2c5d5`) — live validation:**

F170 sort bug absent at HEAD:

```
grep -rn "sorted.*modified_at" flashcore/*.py
→ exit 1 (no matches) — bug is ABSENT at HEAD
```

Target test run:

```
pytest tests/test_review_manager_ordering.py -v
  collected 1 item
  tests/test_review_manager_ordering.py::test_initialize_session_respects_due_date_order PASSED
  1 passed in 0.03s
```

All review-manager tests:

```
pytest tests/test_review_manager_ordering.py tests/test_review_manager.py -v
  collected 26 items — 26 passed in 0.29s
```

Full suite: **496 passed, 1 skipped** in 32.05s.

Evidence artifact: `.github/aiv-packets/evidence/flashcore-f170/adopt_b15bcde_class_a.txt`

### Class B – Referential (SHA-pinned, line-anchored)

Commit `b15bcde51faa961d87a7d177ef00f5360e539213` — diff summary:

- **Added** `tests/test_review_manager_ordering.py` (24 lines in the b15bcde version):
  - `mock_db` fixture (L6–L18): creates three `Card` objects with `next_due_date` at `now+1d`, `now+2d`, `now+3d`; DB mock returns them in unsorted order `[card3, card1, card2]`
  - `test_initialize_session_respects_due_date_order` (L20–L24): calls `initialize_session()`, asserts `review_queue` ids are `[1, 2, 3]` (ascending by `next_due_date`) — proving that the `sorted(..., key=lambda c: c.modified_at)` override does **not** apply at HEAD
- **Added** `.github/aiv-evidence/EVIDENCE_TESTS_TEST_REVIEW_MANAGER_ORDERING.md` (77 lines): AIV evidence file (v1.0) for the test

Note: `tests/test_review_manager_ordering.py` was subsequently refined by commit `cbefb02` into the 73-line form present at HEAD. The HEAD form uses the real `Card` model schema (uuid-keyed, `date` next_due_date) but tests the same invariant.

SHA-pinned commit:
[`b15bcde51faa961d87a7d177ef00f5360e539213`](https://github.com/ImmortalDemonGod/flashcore/commit/b15bcde51faa961d87a7d177ef00f5360e539213)

### Class C – Negative Evidence

**Searched for and did NOT find:**

- Any production Python file modified by `b15bcde`:
  ```
  git show b15bcde --name-only | grep "\.py$" | grep -v "^tests/"
  → No matches — b15bcde only touched tests/ and .github/aiv-evidence/
  ```

- The `sorted.*modified_at` sort override at HEAD (F170 bug — absent):
  ```
  grep -rn "sorted.*modified_at" flashcore/*.py
  → exit 1 (no matches)
  ```

- Any modification to previously-existing test files:
  ```
  git show b15bcde --name-status | grep "^M"
  → No modifications — all changes were additions (A)
  ```

- Any test regression at HEAD: 496 passed, 1 skipped, 0 failed.

**Bug catalog coverage:** `b15bcde` directly targets Bug B1 (the F170 sort-override bug). No new bugs were introduced by the test code.

### Class D – Static Analysis

Executed at HEAD (`fc7811a960c22876d876d2246b7e2cdbaec2c5d5`):

```
mypy flashcore/review_manager.py --ignore-missing-imports
→ Success: no issues found in 1 source file

ruff check tests/test_review_manager_ordering.py
→ F401 [*] `datetime.date` imported but unused (line 3)
→ F401 [*] `flashcore.models.CardState` imported but unused (line 5)
→ Found 2 errors (both auto-fixable with --fix)
```

The two F401 warnings are unused imports (`date`, `CardState`) introduced by `cbefb02`'s expansion of the test file, not by `b15bcde` itself (the b15bcde version imported only `datetime, timedelta, timezone` and `Card`). Both are non-blocking lint issues: the test logic is correct and all assertions pass. No type errors in the production module.

### Class E – Intent Alignment

Commit `b15bcde` added a unit test that directly exercises the F170 behavioral invariant: `initialize_session()` must preserve the DB's `next_due_date ASC NULLS FIRST` ordering in `review_queue`. The test creates a mock DB returning cards out of due-date order and asserts the queue is sorted correctly after `initialize_session()`, which is exactly the verification goal stated in the F170 finding.

This operator edit is a refinement of the same intent that drove the F170 fix — it adds unit-level coverage for Bug B1 (the `sorted(due_cards, key=lambda c: c.modified_at)` override identified at `flashcore/review_manager.py:109`).

> **Canonical intent URL (SHA-pinned):**
> https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180

The audit record at L180 is the F170 finding: `initialize_session()` re-sorts due cards by `modified_at` instead of preserving the DB's `next_due_date ASC NULLS FIRST` ordering. `b15bcde` adds a unit test that proves the fix holds at the `initialize_session()` call boundary, aligning directly with the finding's verification goal.

### Class F – Provenance

Git chain-of-custody for files added by `b15bcde`:

```
git log --oneline --follow -- tests/test_review_manager_ordering.py
cbefb02 test: add unit test for due date ordering in review queue   ← subsequent refinement
b15bcde Add test for ordering bug B1                                ← ADOPTED (created file)

git log --oneline --follow -- .github/aiv-evidence/EVIDENCE_TESTS_TEST_REVIEW_MANAGER_ORDERING.md
b15bcde Add test for ordering bug B1                                ← ADOPTED (created file)
```

`b15bcde` was authored by `openrouter-driver (fix-pipeline) <noreply@openrouter.ai>` on 2026-06-25T21:37:25Z as an out-of-band operator commit mid-drive. Commit `cbefb02` subsequently refined the test to use the real `Card` schema (uuid-keyed) and a more realistic mock DB fixture. Both commits are already on the PR branch.

This adoption packet is committed via `git -c core.hooksPath=/dev/null commit` (packet-only commit per pipeline rules).

Review-manager test file chain-of-custody (files exercising the F170 invariant):
- `tests/test_review_manager_ordering.py` — unit-level due-date order test (added by `b15bcde`, refined by `cbefb02`); passes at HEAD
- `tests/test_review_manager_order.py` — F170 GOAL test; passes at HEAD
- `tests/test_review_manager_integration.py` — integration flow test; passes at HEAD
- `tests/test_review_manager.py` — 25 unit tests; all pass at HEAD; not touched by `b15bcde`

## Machine-checkable data

```json
{
  "change_id": "flashcore-f170-adopt-b15bcde",
  "adopted_commit": "b15bcde51faa961d87a7d177ef00f5360e539213",
  "base_sha": "babfafdf04489082df074958cae9c065c8a8dcc5",
  "head_sha": "fc7811a960c22876d876d2246b7e2cdbaec2c5d5",
  "risk_tier": "R1",
  "files_added_by_b15bcde": [
    "tests/test_review_manager_ordering.py",
    ".github/aiv-evidence/EVIDENCE_TESTS_TEST_REVIEW_MANAGER_ORDERING.md"
  ],
  "production_code_modified": false,
  "existing_tests_modified": false,
  "test_file_is_new_python": true,
  "f170_sort_bug_at_head": false,
  "f170_goal_test_passes_at_head": true,
  "ordering_test_passes_at_head": true,
  "review_manager_tests_at_head": {"passed": 26, "failed": 0},
  "tests_at_head": {"passed": 496, "skipped": 1, "failed": 0},
  "static_analysis": {"mypy": "success", "ruff": "2_f401_unused_imports_non_blocking"},
  "canonical_intent_url": "https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180",
  "evidence_artifact": ".github/aiv-packets/evidence/flashcore-f170/adopt_b15bcde_class_a.txt"
}
```
