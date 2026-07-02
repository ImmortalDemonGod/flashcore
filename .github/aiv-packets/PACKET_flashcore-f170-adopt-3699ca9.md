# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/flashcore |
| **Change ID** | flashcore-f170-adopt-3699ca9 |
| **Commits** | `3699ca9d43206fdfdaf5a16e29f0fb2a3146d045` |
| **Head SHA** | `064630607c4eed1ae531f1ff35aab0e0dcb877bd` |
| **Base SHA** | `a7fbe84e4a8982eee02b0a47da1718a0530af435` (3699ca9^) |
| **Risk tier** | R1 |
| **Classification rationale** | R1: out-of-band operator commit that added two markdown artifacts — a bug catalog (`tests/test_review_manager_order.bug-catalog.md`) cataloguing Bug B1 (the F170 `modified_at` sort override) and a companion AIV evidence file. No Python code was modified. At HEAD the bug documented in the catalog is absent (grep exit 1 on `sorted.*modified_at`) and the full suite is 496 passed, 1 skipped. |

## Claims

1. At `3699ca9^` (`a7fbe84e`), neither `tests/test_review_manager_order.bug-catalog.md` nor `.github/aiv-evidence/EVIDENCE_TESTS_TEST_REVIEW_MANAGER_ORDER.BUG_CATALOG.MD.md` existed.
2. Commit `3699ca9` added both files as documentation artifacts only — no Python production or test code was created or modified.
3. The catalog accurately documents Bug B1: `ReviewManager.initialize_session()` re-sorted the DB-ordered due-card list by `modified_at` instead of preserving the scheduler's `next_due_date ASC` ordering.
4. At HEAD (`064630607c`), the bug described in the catalog is **absent**: `grep -rn "sorted.*modified_at" flashcore/*.py` exits 1 (no matches).
5. At HEAD, the F170 GOAL test (`test_review_manager_ordering_by_due_date`) **PASSES** — `review_queue[0]` is the earliest-due card.
6. At HEAD, all 28 review-manager tests pass and the full suite is **496 passed, 1 skipped** with no regressions. `3699ca9` introduced no regression.

## Evidence

### Class A – Behavioral / Direct

**Baseline (`3699ca9^` — `a7fbe84e4a8982eee02b0a47da1718a0530af435`):**

Files added by `3699ca9` did not exist at baseline:

```
git show 3699ca9^:tests/test_review_manager_order.bug-catalog.md
→ fatal: Path 'tests/test_review_manager_order.bug-catalog.md' does not exist in 'a7fbe84'

git show 3699ca9^:.github/aiv-evidence/EVIDENCE_TESTS_TEST_REVIEW_MANAGER_ORDER.BUG_CATALOG.MD.md
→ fatal: Path does not exist in 'a7fbe84'
```

Both files are markdown documentation (not Python). No behavioral tests target them directly.

**HEAD (`064630607c4eed1ae531f1ff35aab0e0dcb877bd`) — live validation:**

Bug B1 catalogued by `3699ca9` (the `modified_at` sort override):

```
grep -rn "sorted.*modified_at" flashcore/*.py
→ exit 1 (no matches) — bug documented in catalog is ABSENT at HEAD
```

Review-manager tests exercising the catalogued invariant (all PASSED):

```
pytest tests/test_review_manager.py tests/test_review_manager_order.py \
       tests/test_review_manager_ordering.py tests/test_review_manager_integration.py -v
  collected 28 items — 28 passed in 0.38s
```

F170 GOAL test:
- `tests/test_review_manager_order.py::test_review_manager_ordering_by_due_date` PASSED

Full suite: **496 passed, 1 skipped** in 32.59s.

Evidence artifact: `.github/aiv-packets/evidence/flashcore-f170/adopt_3699ca9_class_a.txt`

### Class B – Referential (SHA-pinned, line-anchored)

Commit `3699ca9d43206fdfdaf5a16e29f0fb2a3146d045` — diff summary:

- **Added** `tests/test_review_manager_order.bug-catalog.md` (56 lines):
  - Lines 25–28: Bug Catalog table — Bug B1 (`modified_at` sort override, blast radius, plausibility, test type)
  - Lines 40–56: Evidence class stubs (A–F) to be filled by subsequent pipeline steps
- **Added** `.github/aiv-evidence/EVIDENCE_TESTS_TEST_REVIEW_MANAGER_ORDER.BUG_CATALOG.MD.md` (73 lines):
  - AIV evidence file (v1.0) for the bug catalog; documents classification and claim matrix

Both files were authored by `openrouter-driver (fix-pipeline) <noreply@openrouter.ai>` on 2026-06-25T21:41:18Z. No subsequent commit has modified either file (`git log --follow` shows only `3699ca9` for both).

### Class C – Negative Evidence

**Searched for and did NOT find:**

- Any Python file modified or deleted by `3699ca9`:
  ```
  git show 3699ca9 --name-only | grep "\.py$"
  → No matches — 3699ca9 touched only markdown files
  ```

- The `sorted.*modified_at` sort pattern at HEAD (F170 sort bug — absent):
  ```
  grep -rn "sorted.*modified_at" flashcore/*.py
  → exit 1 (no matches)
  ```

- Any modification to existing test files by `3699ca9`:
  ```
  git show 3699ca9 --name-only | grep "^tests/" | grep "\.py$"
  → No matches — 3699ca9 only created a .md catalog file under tests/
  ```

**Skipped from bug catalog:** `3699ca9` added documentation artifacts only. No existing code or tests were modified. Bug B1 itself was already remediated by prior commits on this branch.

**No test regressions at HEAD:** 496 passed, 1 skipped.

### Class D – Static Analysis

Executed at HEAD (`064630607c4eed1ae531f1ff35aab0e0dcb877bd`):

```
mypy flashcore/review_manager.py --ignore-missing-imports
→ Success: no issues found in 1 source file

ruff check tests/test_review_manager_order.bug-catalog.md \
           .github/aiv-evidence/EVIDENCE_TESTS_TEST_REVIEW_MANAGER_ORDER.BUG_CATALOG.MD.md
→ warning: No Python files found under the given path(s)
→ All checks passed!
```

The files added by `3699ca9` are markdown, not Python — ruff finds no Python to check and reports clean. The production module `flashcore/review_manager.py` is clean at HEAD.

### Class E – Intent Alignment

Commit `3699ca9` added a bug catalog documenting Bug B1 — that `ReviewManager.initialize_session()` re-sorted the DB-ordered due-card list by `modified_at` (line 109 of `review_manager.py`) instead of preserving the scheduler's `next_due_date ASC NULLS FIRST` ordering returned by `get_due_cards()`. The catalog is a required upstream artifact in the pipeline: it defines the blast radius, plausibility, and test strategy for the finding before test code is written.

This is a direct refinement of the F170 finding, aligning to the same canonical intent record.

> **Canonical intent URL (SHA-pinned):**
> https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180

The audit record at L180 documents the F170 finding (incorrect `modified_at` sort override). `3699ca9` is the catalog step in the same remediation chain — it formalizes the bug scope so downstream test and fix steps can cite it.

### Class F – Provenance

Git chain-of-custody for files added by `3699ca9`:

```
git log --oneline --follow -- tests/test_review_manager_order.bug-catalog.md
3699ca9  Add bug catalog for ReviewManager sorting bug   ← ADOPTED (created file, 56 lines)

git log --oneline --follow -- .github/aiv-evidence/EVIDENCE_TESTS_TEST_REVIEW_MANAGER_ORDER.BUG_CATALOG.MD.md
3699ca9  Add bug catalog for ReviewManager sorting bug   ← ADOPTED (created file, 73 lines)
```

`3699ca9` was authored by `openrouter-driver (fix-pipeline) <noreply@openrouter.ai>` on 2026-06-25T21:41:18Z as an out-of-band operator commit mid-drive. No subsequent commit modified either file. This adoption packet is committed via `git -c core.hooksPath=/dev/null commit` (packet-only commit per pipeline rules).

Test file chain-of-custody for files exercising the catalogued bug:
- `tests/test_review_manager_order.py` — created by `c503023`, rewritten by `5942a36`; F170 GOAL test passes at HEAD
- `tests/test_review_manager_ordering.py` — passes at HEAD; not modified by `3699ca9`
- `tests/test_review_manager_integration.py` — passes at HEAD; not modified by `3699ca9`
- `tests/test_review_manager.py` — 25 tests; all pass at HEAD; not modified by `3699ca9`

## Machine-checkable data

```json
{
  "change_id": "flashcore-f170-adopt-3699ca9",
  "adopted_commit": "3699ca9d43206fdfdaf5a16e29f0fb2a3146d045",
  "base_sha": "a7fbe84e4a8982eee02b0a47da1718a0530af435",
  "head_sha": "064630607c4eed1ae531f1ff35aab0e0dcb877bd",
  "risk_tier": "R1",
  "files_added_by_3699ca9": [
    "tests/test_review_manager_order.bug-catalog.md",
    ".github/aiv-evidence/EVIDENCE_TESTS_TEST_REVIEW_MANAGER_ORDER.BUG_CATALOG.MD.md"
  ],
  "files_are_python": false,
  "files_existed_at_baseline": false,
  "python_code_modified_by_3699ca9": false,
  "bug_b1_description": "ReviewManager re-sorts due cards by modified_at instead of next_due_date",
  "f170_sort_bug_at_head": false,
  "f170_goal_test_passes_at_head": true,
  "review_manager_tests_at_head": {"passed": 28, "failed": 0},
  "tests_at_head": {"passed": 496, "skipped": 1, "failed": 0},
  "static_analysis": {"mypy": "success", "ruff": "clean (no Python files in changed set)"},
  "canonical_intent_url": "https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L180",
  "evidence_artifact": ".github/aiv-packets/evidence/flashcore-f170/adopt_3699ca9_class_a.txt"
}
```
