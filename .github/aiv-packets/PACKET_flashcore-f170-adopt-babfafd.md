# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/flashcore |
| **Change ID** | flashcore-f170-adopt-babfafd |
| **Commits** | `babfafdf04489082df074958cae9c065c8a8dcc5` |
| **Head SHA** | `fc7811a960c22876d876d2246b7e2cdbaec2c5d5` |
| **Base SHA** | `8468eceb3f10d81f5dc093abedb8ac30f4178d8b` (babfafd^) |
| **Risk tier** | R1 |
| **Classification rationale** | R1: out-of-band operator commit that added a bug catalog markdown (`tests/test_review_manager.bug-catalog.md`) and its companion AIV evidence file. No production Python was modified. The bug catalog documents the F170 scheduling invariant (B1/B2) and records the skipped-bug set (B3/B4). At HEAD the F170 sort bug is absent and all 28 review-manager tests plus the full suite of 496 pass. |

## Claims

1. At `babfafd^` (`8468eceb3f`), neither `tests/test_review_manager.bug-catalog.md` nor `.github/aiv-evidence/EVIDENCE_TESTS_TEST_REVIEW_MANAGER.BUG_CATALOG.MD.md` existed — `babfafd` is their first creation commit.
2. Commit `babfafd` added exactly two files (one markdown bug catalog, one AIV evidence file); it modified no production Python code.
3. The bug catalog correctly identifies the F170 root cause: `initialize_session()` re-sorts due cards by `modified_at` (B1) instead of preserving the DB's `next_due_date ASC NULLS FIRST` ordering, and records that after a review `modified_at` is bumped, displacing cards from their correct queue position (B2).
4. At HEAD (`fc7811a9`), the F170 sort bug is **absent**: `grep -rn "sorted.*modified_at" flashcore/*.py` exits 1 (no matches).
5. At HEAD, the F170 GOAL test `tests/test_review_manager_order.py::test_review_manager_ordering_by_due_date` **PASSES**.
6. At HEAD, all 28 review-manager tests pass and the full suite is **496 passed, 1 skipped** with no regressions introduced by `babfafd`.

## Evidence

### Class A – Behavioral / Direct

**Baseline (`babfafd^` — `8468eceb3f10d81f5dc093abedb8ac30f4178d8b`):**

Both files introduced by `babfafd` were absent at the baseline commit:

```
git show babfafd^:tests/test_review_manager.bug-catalog.md
→ fatal: Path 'tests/test_review_manager.bug-catalog.md' does not exist in '8468eceb'
```

**HEAD (`fc7811a960c22876d876d2246b7e2cdbaec2c5d5`) — live validation:**

F170 sort bug absent at HEAD:

```
grep -rn "sorted.*modified_at" flashcore/*.py
→ exit 1 (no matches) — bug is ABSENT at HEAD
```

F170 GOAL test:

```
pytest tests/test_review_manager_order.py::test_review_manager_ordering_by_due_date -v
  PASSED
```

All review-manager tests:

```
pytest tests/test_review_manager.py tests/test_review_manager_order.py \
       tests/test_review_manager_ordering.py tests/test_review_manager_integration.py -v
  collected 28 items — 28 passed in 0.35s
```

Full suite: **496 passed, 1 skipped** in 31.83s.

Evidence artifact: `.github/aiv-packets/evidence/flashcore-f170/adopt_babfafd_class_a.txt`

### Class B – Referential (SHA-pinned, line-anchored)

Commit `babfafdf04489082df074958cae9c065c8a8dcc5` — diff summary:

- **Added** `tests/test_review_manager.bug-catalog.md` (24 lines):
  - Summary (L1–L5): describes the `initialize_session` re-sort defect
  - Bug table (L7–L11): B1 (queue ordered by `modified_at` not `next_due_date`), B2 (post-review `modified_at` bump displaces cards)
  - Skipped bugs (L13–L15): B3 (NULL `next_due_date` — acceptable DB ordering), B4 (UI display ordering — out of scope)
  - Test plan (L17–L21): decision-table unit test for B1; red integration test for B2
  - Evaluation stub (L23–L24): placeholder for post-run results (unfilled at commit time — intentional)
- **Added** `.github/aiv-evidence/EVIDENCE_TESTS_TEST_REVIEW_MANAGER.BUG_CATALOG.MD.md` (73 lines): AIV evidence file (v1.0) for the bug catalog

SHA-pinned line anchor:
[`tests/test_review_manager.bug-catalog.md#L1-L24`](https://github.com/ImmortalDemonGod/flashcore/blob/babfafdf04489082df074958cae9c065c8a8dcc5/tests/test_review_manager.bug-catalog.md#L1-L24)

### Class C – Negative Evidence

**Searched for and did NOT find:**

- Any production Python file modified by `babfafd`:
  ```
  git show babfafd --name-status | grep "\.py$" | grep -v "^tests/"
  → No matches — babfafd only touched tests/ and .github/aiv-evidence/
  ```

- The `sorted.*modified_at` sort override at HEAD (F170 bug — absent):
  ```
  grep -rn "sorted.*modified_at" flashcore/*.py
  → exit 1 (no matches)
  ```

- Any modification to previously-existing test files:
  ```
  git show babfafd --name-status | grep "^M"
  → No matches — both files are new additions (status A)
  ```

- Any test regression at HEAD: 496 passed, 1 skipped, 0 failed.

**Bug catalog skipped-bug coverage:** The catalog explicitly records B3 (NULL `next_due_date` — deferred, acceptable) and B4 (UI display ordering — out of scope). These are documented deferrals, not silent omissions. Neither B3 nor B4 is architectural-correctness-blocking for the current fix.

### Class D – Static Analysis

Executed at HEAD (`fc7811a960c22876d876d2246b7e2cdbaec2c5d5`):

```
mypy flashcore/review_manager.py --ignore-missing-imports
→ Success: no issues found in 1 source file

ruff check tests/test_review_manager.bug-catalog.md
→ warning: No Python files found under the given path(s) [expected — markdown]
→ All checks passed!
```

`flashcore/review_manager.py` is mypy-clean at HEAD. The bug catalog is a markdown file; ruff correctly identifies no Python to lint.

### Class E – Intent Alignment

Commit `babfafd` added a structured bug catalog that enumerates and classifies the ordering defects targeted by the F170 fix. Bug B1 (queue sorted by `modified_at` instead of `next_due_date`) and B2 (post-review `modified_at` bump displacing cards) are the precise defects identified in the F170 audit finding at `flashcore/review_manager.py:109`. The catalog also records the skipped-bug set (B3, B4) with explicit rationale, satisfying the requirement that Class C coverage be documented rather than silently omitted.

This operator edit is a refinement of the same intent that drove the F170 fix — it adds structured evidence that the bug analysis was complete and correctly scoped.

> **Canonical intent URL (SHA-pinned):**
> https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180

The audit record at L180 is the F170 finding: `initialize_session()` re-sorts due cards by `modified_at` instead of preserving the DB's `next_due_date ASC NULLS FIRST` ordering. `babfafd` adds a bug catalog that documents precisely this invariant and its blast radius, aligning directly with the finding's verification goal.

### Class F – Provenance

Git chain-of-custody for files added by `babfafd`:

```
git log --oneline --follow -- tests/test_review_manager.bug-catalog.md
babfafd Add bug catalog for ReviewManager scheduling bug  ← ADOPTED (created file)

git log --oneline --follow -- .github/aiv-evidence/EVIDENCE_TESTS_TEST_REVIEW_MANAGER.BUG_CATALOG.MD.md
babfafd Add bug catalog for ReviewManager scheduling bug  ← ADOPTED (created file)
```

`babfafd` was authored by `openrouter-driver (fix-pipeline) <noreply@openrouter.ai>` on 2026-06-25T21:36:17Z as an out-of-band operator commit mid-drive. Both files are first created in this commit; no prior version exists on the branch.

This adoption packet is committed via `git -c core.hooksPath=/dev/null commit` (packet-only commit per pipeline rules).

Review-manager test file chain-of-custody (files exercising the F170 invariant):
- `tests/test_review_manager_order.py` — F170 GOAL test; passes at HEAD
- `tests/test_review_manager_ordering.py` — unit-level due-date order test; passes at HEAD
- `tests/test_review_manager_integration.py` — integration flow test; passes at HEAD
- `tests/test_review_manager.py` — 25 unit tests; all pass at HEAD; not touched by `babfafd`
- `tests/test_review_manager.bug-catalog.md` — bug catalog added by `babfafd`; documents B1/B2 defects and B3/B4 skips

## Machine-checkable data

```json
{
  "change_id": "flashcore-f170-adopt-babfafd",
  "adopted_commit": "babfafdf04489082df074958cae9c065c8a8dcc5",
  "base_sha": "8468eceb3f10d81f5dc093abedb8ac30f4178d8b",
  "head_sha": "fc7811a960c22876d876d2246b7e2cdbaec2c5d5",
  "risk_tier": "R1",
  "files_added_by_babfafd": [
    "tests/test_review_manager.bug-catalog.md",
    ".github/aiv-evidence/EVIDENCE_TESTS_TEST_REVIEW_MANAGER.BUG_CATALOG.MD.md"
  ],
  "production_code_modified": false,
  "existing_tests_modified": false,
  "f170_sort_bug_at_head": false,
  "f170_goal_test_passes_at_head": true,
  "review_manager_tests_at_head": {"passed": 28, "failed": 0},
  "tests_at_head": {"passed": 496, "skipped": 1, "failed": 0},
  "static_analysis": {"mypy": "success", "ruff": "clean"},
  "canonical_intent_url": "https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180",
  "evidence_artifact": ".github/aiv-packets/evidence/flashcore-f170/adopt_babfafd_class_a.txt",
  "skipped_bugs": ["B3", "B4"],
  "skipped_bugs_documented": true
}
```
