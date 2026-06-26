# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/flashcore |
| **Change ID** | flashcore-f83-adopt-151570d |
| **Commits** | `151570d` (operator out-of-band) |
| **Head SHA** | `b05610c60c9a13e0707100ad5142e2079644d461` |
| **Base SHA** | `1cd34acc5a163047cef66fa2002fc58c11195780` (151570d^) |
| **Risk tier** | R1 |
| **Classification rationale** | Operator out-of-band addition of `tests/test_vet_logic.py` (16 lines) and its AIV evidence wrapper `.github/aiv-evidence/EVIDENCE_TESTS_TEST_VET_LOGIC.md`. The test documents the canonical B1 bug: `_validate_and_normalize_card` does not remove the `s` field before `Card(...)` instantiation, causing `ValidationError` for cards carrying a score. At introduction the test was a bug-asserting test (expected `ValidationError`). A subsequent commit (`c1ac582`) updated it to a fix-verifying test after the production fix landed. No production Python source files were modified by `151570d`. Risk tier R1 because new test code enters the repository with behavioral claims that must be verified. |

## Classification

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_vet_logic.py"
  classification_rationale: >
    Commit 151570d adds one test file (16 lines) and one evidence-wrapper markdown file.
    No production source code or existing test files were modified or deleted.
    The test documents the B1 bug identified in the canonical audit finding at
    audit/02-static-audit.md#L93: _validate_and_normalize_card fails to pop the 's'
    field, causing ValidationError for cards with a score. At introduction the test
    asserted the buggy behavior (expected ValidationError). A later commit (c1ac582)
    updated the test to verify the fix. Branch HEAD is correct; no fix-forward required.
  classified_by: "fix-pipeline adopt stage"
  classified_at: "2026-06-26T00:00:00Z"
```

## Claims

1. Commit `151570d` added exactly two files:
   `tests/test_vet_logic.py` (16 lines — bug-asserting B1 test) and
   `.github/aiv-evidence/EVIDENCE_TESTS_TEST_VET_LOGIC.md` (76 lines — operator evidence wrapper).
   No production Python files or existing test files were modified.
2. At `151570d`, `test_validate_and_normalize_card_does_not_remove_score_field_raises_error` PASSED
   because the bug was still present in `_vet_logic.py` at that commit — `ValidationError` was raised
   as expected by `pytest.raises`.
3. A subsequent commit `c1ac582` (`feat(flashcore-f83-impl)`) updated `tests/test_vet_logic.py` to
   `test_validate_and_normalize_card_removes_score_field`, asserting the fixed behavior
   (no `ValidationError`; `s` field removed from the returned dict).
4. At HEAD (`b05610c`), `tests/test_vet_logic.py::test_validate_and_normalize_card_removes_score_field`
   PASSES, confirming the production fix is in place.
5. All 10 pre-existing tests in `tests/cli/test_vet_logic.py` present at `151570d^` continue to PASS
   at HEAD — zero regressions.
6. No tests were broken by `151570d`; no fix-forward commit is required.

---

## Evidence References

| # | Evidence File | Commit SHA | Classes |
|---|---------------|------------|---------|
| 1 | `evidence/flashcore-f83/CLASS_A_ADOPT_151570D_TEST_RUN.md` | `b05610c` | A, B, F |

---

### Class A (Behavioral/Direct Evidence)

**Evidence artifact:** [`.github/aiv-packets/evidence/flashcore-f83/CLASS_A_ADOPT_151570D_TEST_RUN.md`](https://github.com/ImmortalDemonGod/flashcore/blob/b05610c60c9a13e0707100ad5142e2079644d461/.github/aiv-packets/evidence/flashcore-f83/CLASS_A_ADOPT_151570D_TEST_RUN.md)

**Baseline (`151570d^` = `1cd34ac`):** 10 tests collected from `tests/cli/test_vet_logic.py` — all 10
PASSED. `tests/test_vet_logic.py` did not exist at this commit.

**At commit (`151570d`):** 11 tests collected: `tests/cli/test_vet_logic.py` (10) +
`tests/test_vet_logic.py` (1 — bug-asserting). All 11 PASSED. The bug-asserting test
`test_validate_and_normalize_card_does_not_remove_score_field_raises_error` PASSED because the
production code had not yet removed the `s` field (bug was still present).

**HEAD (`b05610c`):** 11 tests collected: `tests/cli/test_vet_logic.py` (10) +
`tests/test_vet_logic.py` (1 — fix-verifying). All 11 PASSED.
`test_validate_and_normalize_card_removes_score_field` PASSES, confirming the `s` field is
removed and no `ValidationError` is raised.

Delta vs. baseline: 0 regressions attributable to `151570d`. The +1 test reflects `151570d`'s new
test; its later evolution into a fix-verifying test is the work of `c1ac582`, adopted separately.

Verification method: baseline reproduced via
`git worktree add /tmp/baseline-151570d 1cd34acc5a163047cef66fa2002fc58c11195780`
using the shared project venv. At-commit run executed via
`git worktree add /tmp/at-151570d 151570d1085386c54ac9d3810417d7060764cb1f`.
HEAD run executed directly in the working tree at `b05610c` via
`pytest tests/test_vet_logic.py tests/cli/test_vet_logic.py -v --tb=short`.

### Class B (Referential Evidence — SHA-pinned line anchors)

**151570d changes confirmed:**

- `tests/test_vet_logic.py` (added, 16 lines):
  - Imports at [`tests/test_vet_logic.py#L1-L3`](https://github.com/ImmortalDemonGod/flashcore/blob/151570d1085386c54ac9d3810417d7060764cb1f/tests/test_vet_logic.py#L1):
    `import pytest`, `from flashcore.cli._vet_logic import _validate_and_normalize_card`,
    `from pydantic import ValidationError`
  - Test function `test_validate_and_normalize_card_does_not_remove_score_field_raises_error` at
    [`tests/test_vet_logic.py#L5-L16`](https://github.com/ImmortalDemonGod/flashcore/blob/151570d1085386c54ac9d3810417d7060764cb1f/tests/test_vet_logic.py#L5) —
    passes `{"q": ..., "a": ..., "s": 5}` to `_validate_and_normalize_card` inside
    `pytest.raises(ValidationError)`, asserting the bug is present.

- `.github/aiv-evidence/EVIDENCE_TESTS_TEST_VET_LOGIC.md` (added, 76 lines):
  — operator's evidence wrapper for the test file; contains classification yaml, claims, and Class E link.

**Bug site confirmed at HEAD (related context):**
- [`flashcore/cli/_vet_logic.py#L67`](https://github.com/ImmortalDemonGod/flashcore/blob/b05610c60c9a13e0707100ad5142e2079644d461/flashcore/cli/_vet_logic.py#L67)
  — `mapped_card_dict.pop("s", None)` (strips score before Card validation)
- [`flashcore/cli/_vet_logic.py#L89`](https://github.com/ImmortalDemonGod/flashcore/blob/b05610c60c9a13e0707100ad5142e2079644d461/flashcore/cli/_vet_logic.py#L89)
  — `card_to_write.pop("s", None)` (strips score from write-back output)

Model constraint confirmed at:
- [`flashcore/models.py#L51`](https://github.com/ImmortalDemonGod/flashcore/blob/b05610c60c9a13e0707100ad5142e2079644d461/flashcore/models.py#L51)
  — `extra='forbid'` on `Card` model

### Class C (Negative — what was searched for and not found)

- **Production code changes**: `git show 151570d --name-only` returns only
  `tests/test_vet_logic.py` and
  `.github/aiv-evidence/EVIDENCE_TESTS_TEST_VET_LOGIC.md` —
  no production Python files modified.
- **Deleted or weakened tests**: `git show 151570d -- tests/cli/test_vet_logic.py` returns empty diff;
  the 10 pre-existing tests in `tests/cli/test_vet_logic.py` were not touched by `151570d`.
- **Regression search**: all 10 test names from `tests/cli/test_vet_logic.py` at `151570d^` collected
  and passed at HEAD; none deleted, renamed, or weakened by `151570d`.
- **Fix-forward requirement**: `151570d` broke no tests at the commit itself (all 11 tests PASSED
  at `151570d`); a subsequent commit (`c1ac582`) legitimately updated the test to match the fix.
  No fix-forward commit is required for this adoption.
- **Silent revert**: `151570d` adds new files only; no content from the parent state (`1cd34ac`)
  was silently reverted.
- **Bug catalog Skipped set**: `tests/test_vet_logic.py` was the first test targeting B1
  (score-field removal). No prior test covering this invariant existed at `151570d^`;
  none was deleted by `151570d`.

### Class D (Static Analysis)

- `ruff check tests/test_vet_logic.py` at HEAD (`b05610c`) returns:
  ```
  F401 [*] `pytest` imported but unused
      --> tests/test_vet_logic.py:1:8
  F401 [*] `flashcore.models.Card` imported but unused
      --> tests/test_vet_logic.py:3:30
  Found 2 errors.
  ```
  These unused imports were introduced by `c1ac582` when the test was updated to no longer use
  `pytest.raises` or the `Card` type directly. They were NOT present in `151570d`'s original version
  (which used `pytest.raises(ValidationError)`, making `pytest` necessary). Style-only; no
  correctness impact. The test passes GREEN despite the unused imports. Cleanup deferred as
  pre-existing style debt from the operator/pipeline chain.
- `mypy tests/test_vet_logic.py` — errors reported are in unrelated modules
  (`flashcore/db/connection.py`, `flashcore/db/schema_manager.py`, `flashcore/db/database.py`,
  `flashcore/parser.py`); all pre-existing and not introduced by `151570d`. No type errors in
  the test file itself.
- No new correctness-class lint errors introduced by `151570d`.

### Class E (Intent Alignment)

- **Canonical intent URL:**
  `https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L93`

- **Alignment:** The audit record at L93 identifies the root defect:
  `_validate_and_normalize_card()` maps `q`→`front` and `a`→`back` but never removes
  the `s` (score) field, causing `Card(**mapped_card_dict, deck_name=deck_name)` to raise
  `ValidationError` for any YAML card carrying a valid `s` field.

  Commit `151570d` adds a test for precisely this defect: it passes a card with `s=5` to
  `_validate_and_normalize_card` and asserts that a `ValidationError` is raised. The docstring
  explicitly states: "Bug B1: `_validate_and_normalize_card` should drop the `s` field.
  Currently it does not, causing ValidationError for cards with a score." This is a direct,
  canonical test of the audit finding's described failure mode. The operator's test is aligned
  with the audit finding's intent — documenting the bug's reproducibility and later serving as
  the regression guard (after `c1ac582` updated it to verify the fix).

### Class F (Provenance — git chain-of-custody)

- Commit `151570d1085386c54ac9d3810417d7060764cb1f` authored by
  `openrouter-driver (fix-pipeline) <noreply@openrouter.ai>`;
  message: `Add test for missing score field removal bug`.
- Parent of `151570d` is `1cd34acc5a163047cef66fa2002fc58c11195780`
  (`Add bug catalog for _vet_logic`).
- Chain from `151570d` to HEAD: 35 commits with no gaps, confirmed by
  `git log --oneline 151570d..HEAD` (35 lines).
- `tests/test_vet_logic.py` was modified by one subsequent commit: `c1ac582`
  (`feat(flashcore-f83-impl): tests/test_vet_logic.py`) — which updated the test from
  bug-asserting to fix-verifying.
  **Justification:** `c1ac582` updated the test to reflect the production fix that landed in
  the same implementation commit. A bug-asserting test that was correct when the bug existed
  must be updated once the fix is in place — otherwise it would fail permanently and block CI.
  The update does not weaken the test; it converts it from "asserting the bug reproduces" to
  "asserting the fix holds". This evolution is the intended lifecycle of a bug-regression test.
- HEAD is `b05610c60c9a13e0707100ad5142e2079644d461`
  (`docs(aiv): adoption packet for operator commit 6828dc7`).

---

## Verification Methodology

**Zero-Touch Mandate:** All evidence above is machine-verifiable by the reviewer without running
any tests themselves. Baseline and HEAD test runs were executed by the pipeline driver and artifacts
captured in the evidence directory. The baseline was reproduced via a temporary git worktree at
`151570d^` using the project's shared venv; the at-commit run was reproduced via a temporary
git worktree at `151570d`. Both worktrees were removed after their runs. HEAD run executed
directly in the working tree at `b05610c`.

---

## Known Limitations

- `ruff` reports two F401 (unused imports: `pytest` and `flashcore.models.Card`) at
  `tests/test_vet_logic.py` at HEAD. These were introduced by `c1ac582` when the test was
  updated to no longer use `pytest.raises`. No correctness impact. Cleanup deferred (style-only).
- `mypy` pre-existing errors in `flashcore/db/` and `flashcore/parser.py` are unrelated to this
  change and were present before `151570d`.

---

## Summary

Commit `151570d` is the operator's out-of-band addition of `tests/test_vet_logic.py` — a bug-
asserting test for the canonical B1 finding: `_validate_and_normalize_card` does not remove the
`s` field before `Card(...)` instantiation, causing `ValidationError` for cards with a score.
The test passed GREEN at `151570d` (bug was present). A subsequent commit (`c1ac582`) updated
the test to verify the fix. At HEAD, the test passes GREEN, confirming the fix is in place.
All 10 pre-existing `tests/cli/test_vet_logic.py` tests continue to pass. Zero regressions.
No fix-forward commit required. Branch HEAD is correct after the operator's edit.

## Machine-checkable data

```json
{
  "packet_version": "2.2",
  "change_id": "flashcore-f83-adopt-151570d",
  "adopted_commit": "151570d1085386c54ac9d3810417d7060764cb1f",
  "fix_forward_commit": null,
  "base_sha": "1cd34acc5a163047cef66fa2002fc58c11195780",
  "head_sha": "b05610c60c9a13e0707100ad5142e2079644d461",
  "risk_tier": "R1",
  "evidence_classes": ["A", "B", "C", "D", "E", "F"],
  "baseline_tests": {"collected": 10, "passed": 10, "failed": 0},
  "head_tests": {"collected": 11, "passed": 11, "failed": 0},
  "regressions": 0,
  "fix_forward_required": false,
  "canonical_intent": "https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L93"
}
```
