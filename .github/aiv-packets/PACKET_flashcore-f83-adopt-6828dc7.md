# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/flashcore |
| **Change ID** | flashcore-f83-adopt-6828dc7 |
| **Commits** | `6828dc7` (operator out-of-band) |
| **Head SHA** | `22d8b6c42a7c46aff3d68bc44d59833023d03caf` |
| **Base SHA** | `151570d1085386c54ac9d3810417d7060764cb1f` (6828dc7^) |
| **Risk tier** | R1 |
| **Classification rationale** | Operator out-of-band addition of `tests/test_vet_logic_idempotent.py` (11 lines) and its AIV evidence wrapper `.github/aiv-evidence/EVIDENCE_TESTS_TEST_VET_LOGIC_IDEMPOTENT.md`. The test verifies the idempotence property of `_validate_and_normalize_card`: calling the function twice on the same card produces an identical output dict (stable UUID, no churn). No production Python source files were modified. The test exercises the function that received the primary bug fix (score-field `pop` at `_vet_logic.py:67,89`) and strengthens the correctness envelope around the canonical finding. |

## Classification

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/test_vet_logic_idempotent.py"
  classification_rationale: >
    Commit 6828dc7 adds one test file (11 lines) and one evidence-wrapper markdown file.
    No production source code or existing test files were modified or deleted.
    The idempotence test is a refinement of the canonical audit finding at
    audit/02-static-audit.md#L93: it exercises the same function (_validate_and_normalize_card)
    that was defective and verifies an additional correctness property (UUID stability across
    repeated normalization passes). Test passes GREEN at HEAD. Risk tier R1 because new test
    code enters the repository with behavioral claims that must be verified.
  classified_by: "fix-pipeline adopt stage"
  classified_at: "2026-06-26T00:00:00Z"
```

## Claims

1. Commit `6828dc7` added exactly two files:
   `tests/test_vet_logic_idempotent.py` (11 lines — idempotence test) and
   `.github/aiv-evidence/EVIDENCE_TESTS_TEST_VET_LOGIC_IDEMPOTENT.md` (76 lines — operator evidence wrapper).
   No production Python files or existing test files were modified.
2. `test_idempotent_normalization_keeps_uuid_and_no_error` at
   [`tests/test_vet_logic_idempotent.py#L4`](https://github.com/ImmortalDemonGod/flashcore/blob/22d8b6c42a7c46aff3d68bc44d59833023d03caf/tests/test_vet_logic_idempotent.py#L4)
   calls `_validate_and_normalize_card` twice on the same card data and asserts the outputs are equal,
   verifying the idempotence (no UUID churn) invariant of the normalization function.
3. The test passes GREEN at HEAD (`22d8b6c`) with `pytest tests/test_vet_logic_idempotent.py -v`.
4. All 10 pre-existing tests in `tests/cli/test_vet_logic.py` present at `6828dc7^` pass at HEAD — zero regressions.
5. No tests were broken by `6828dc7`; no fix-forward commit is required.

---

## Evidence References

| # | Evidence File | Commit SHA | Classes |
|---|---------------|------------|---------|
| 1 | `evidence/flashcore-f83/CLASS_A_ADOPT_6828DC7_TEST_RUN.md` | `22d8b6c` | A, B, F |

---

### Class A (Behavioral/Direct Evidence)

**Evidence artifact:** [`.github/aiv-packets/evidence/flashcore-f83/CLASS_A_ADOPT_6828DC7_TEST_RUN.md`](https://github.com/ImmortalDemonGod/flashcore/blob/22d8b6c42a7c46aff3d68bc44d59833023d03caf/.github/aiv-packets/evidence/flashcore-f83/CLASS_A_ADOPT_6828DC7_TEST_RUN.md)

**Baseline (6828dc7^ = `151570d`):** 10 tests collected from `tests/cli/test_vet_logic.py` — all 10 PASSED.
`tests/test_vet_logic_idempotent.py` did not exist at this commit. `tests/test_vet_logic_score.py`
had a pre-existing SyntaxError and was excluded from the baseline run.

**HEAD (`22d8b6c`):** 12 tests collected: `tests/cli/test_vet_logic.py` (10) +
`tests/test_vet_logic_idempotent.py` (1) + `tests/test_vet_logic_score.py` (1). All 12 PASSED.
Zero failures.

Delta vs. baseline: 0 regressions attributable to `6828dc7`. The +2 tests reflect `6828dc7`'s
new idempotence test and the later SyntaxError fix (in the chain after `6828dc7`); neither
test existed at the baseline.

Verification method: baseline reproduced via
`git worktree add /tmp/baseline-6828dc7b 151570d1085386c54ac9d3810417d7060764cb1f`
using the shared project venv. HEAD run executed directly in the working tree at `22d8b6c` via
`pytest tests/test_vet_logic_idempotent.py tests/cli/test_vet_logic.py tests/test_vet_logic_score.py -v --tb=short`.

### Class B (Referential Evidence — SHA-pinned line anchors)

**6828dc7 changes confirmed:**

- `tests/test_vet_logic_idempotent.py` (added, 11 lines):
  - Import at [`tests/test_vet_logic_idempotent.py#L1-L2`](https://github.com/ImmortalDemonGod/flashcore/blob/6828dc70bbc135d65e4daacb44c64d562ce36165/tests/test_vet_logic_idempotent.py#L1)
    — `import pytest` (unused, ruff F401) and `from flashcore.cli._vet_logic import _validate_and_normalize_card`
  - Test function `test_idempotent_normalization_keeps_uuid_and_no_error` at
    [`tests/test_vet_logic_idempotent.py#L4-L11`](https://github.com/ImmortalDemonGod/flashcore/blob/6828dc70bbc135d65e4daacb44c64d562ce36165/tests/test_vet_logic_idempotent.py#L4)
    — calls `_validate_and_normalize_card` twice and asserts `first == second`

- `.github/aiv-evidence/EVIDENCE_TESTS_TEST_VET_LOGIC_IDEMPOTENT.md` (added, 76 lines):
  — operator's evidence wrapper for the test file; contains classification yaml, claims, and Class E link.

**Materialized fix confirmed at HEAD (related context):**
- [`flashcore/cli/_vet_logic.py#L67`](https://github.com/ImmortalDemonGod/flashcore/blob/22d8b6c42a7c46aff3d68bc44d59833023d03caf/flashcore/cli/_vet_logic.py#L67)
  — `mapped_card_dict.pop("s", None)` (strips score before Card validation)
- [`flashcore/cli/_vet_logic.py#L89`](https://github.com/ImmortalDemonGod/flashcore/blob/22d8b6c42a7c46aff3d68bc44d59833023d03caf/flashcore/cli/_vet_logic.py#L89)
  — `card_to_write.pop("s", None)` (strips score from write-back output)

Model constraint confirmed at:
- [`flashcore/models.py#L51`](https://github.com/ImmortalDemonGod/flashcore/blob/22d8b6c42a7c46aff3d68bc44d59833023d03caf/flashcore/models.py#L51)
  — `extra='forbid'` on `Card` model

### Class C (Negative — what was searched for and not found)

- **Production code changes**: `git show 6828dc7 --name-only` returns only
  `tests/test_vet_logic_idempotent.py` and
  `.github/aiv-evidence/EVIDENCE_TESTS_TEST_VET_LOGIC_IDEMPOTENT.md` —
  no production Python files modified.
- **Deleted or weakened tests**: `git show 6828dc7 -- tests/cli/test_vet_logic.py` returns empty diff;
  the 10 pre-existing tests in `tests/cli/test_vet_logic.py` were not touched by `6828dc7`.
- **Regression search**: all 10 test names from `tests/cli/test_vet_logic.py` at `6828dc7^` collected
  and passed at HEAD; none deleted, renamed, or weakened.
- **Bug catalog Skipped set**: the prior adoption packet for `534ce28` documented the operator
  removing B2 (idempotence) from the bug catalog in that commit. Commit `6828dc7` adds a test
  exercising the idempotence property anyway — a refinement, not a contradiction.
  No existing test covering idempotence existed at `6828dc7^`; none was deleted by `6828dc7`.
- **Fix-forward requirement**: `6828dc7` broke no tests and introduced no defects;
  the new test passes GREEN at HEAD. No fix-forward commit is required.
- **Silent revert**: `6828dc7` adds new files only; no content from the parent state (`151570d`)
  was silently reverted.
- **Unused `import pytest`**: ruff F401 at `tests/test_vet_logic_idempotent.py:1`. Pre-existing
  in the file as added by `6828dc7`; not introduced by any subsequent commit. Style-only;
  no correctness impact. Deferred (pre-existing style debt from the operator's edit).

### Class D (Static Analysis)

- `ruff check tests/test_vet_logic_idempotent.py` at HEAD returns:
  ```
  F401 [*] `pytest` imported but unused
      --> tests/test_vet_logic_idempotent.py:1:8
  Found 1 error.
  ```
  This is a style issue (unused import) introduced by `6828dc7` and present at HEAD. It is
  fixable and has no correctness impact. The test passes GREEN despite the unused import.
  Cleanup deferred — this is the operator's file; a style cleanup would require a separate commit.
- `mypy tests/test_vet_logic_idempotent.py` — mypy errors reported are in unrelated modules
  (`flashcore/db/connection.py`, `flashcore/db/schema_manager.py`, `flashcore/db/database.py`,
  `flashcore/parser.py`); all pre-existing and not introduced by `6828dc7`. No type errors in
  the test file itself.
- No new correctness-class lint errors introduced by `6828dc7`.

### Class E (Intent Alignment)

- **Canonical intent URL:**
  `https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L93`

- **Alignment:** The audit record at L93 identifies the root defect:
  `_validate_and_normalize_card()` maps `q`→`front` and `a`→`back` but never removes
  the `s` (score) field, causing `Card(**mapped_card_dict, deck_name=deck_name)` to raise
  `ValidationError` for any YAML card carrying a valid `s` field.

  Commit `6828dc7` adds a test for the idempotence property of the same function
  (`_validate_and_normalize_card`) that was defective. The test verifies that calling the
  function twice on the same card data produces an identical output dict — specifically that
  the UUID is preserved (no churn) on a second normalization pass. This is a refinement of the
  correctness envelope around the canonical finding: the fix at `_vet_logic.py:67,89` must not
  only remove the `s` field on first pass but also leave the card in a stable state where
  a second pass is a no-op. The operator's test directly exercises that stability invariant
  on the fixed function. The change is aligned with the audit finding's intent: ensure
  `_validate_and_normalize_card` is correct and safe for repeated application.

### Class F (Provenance — git chain-of-custody)

- Commit `6828dc70bbc135d65e4daacb44c64d562ce36165` authored by
  `openrouter-driver (fix-pipeline) <noreply@openrouter.ai>`;
  message: `Add idempotence test for _validate_and_normalize_card`.
- Parent of `6828dc7` is `151570d1085386c54ac9d3810417d7060764cb1f`
  (`Add test for missing score field removal bug`).
- Chain from `6828dc7` to HEAD: 33 commits with no gaps, confirmed by
  `git log --oneline 6828dc7..HEAD` (33 lines).
- `tests/test_vet_logic_idempotent.py` was not modified by any commit after `6828dc7`:
  `git log --oneline 6828dc7..HEAD -- tests/test_vet_logic_idempotent.py` returns empty.
  Chain-of-custody for the test file is unbroken.
- HEAD is `22d8b6c42a7c46aff3d68bc44d59833023d03caf` (`docs(aiv): adoption packet for operator commit 534ce28`).

---

## Verification Methodology

**Zero-Touch Mandate:** All evidence above is machine-verifiable by the reviewer without running
any tests themselves. Baseline and HEAD test runs were executed by the pipeline driver and artifacts
captured in the evidence directory. The baseline was reproduced via a temporary git worktree at
`6828dc7^` using the project's shared venv; the worktree was removed after the run. HEAD run
executed directly in the working tree at `22d8b6c`.

---

## Known Limitations

- `ruff` reports F401 (unused `import pytest`) at `tests/test_vet_logic_idempotent.py:1` — introduced
  by the operator's commit `6828dc7`. No correctness impact. Cleanup deferred (style-only).
- `mypy` pre-existing errors in `flashcore/db/` and `flashcore/parser.py` are unrelated to this change
  and were present before `6828dc7`.
- `tests/test_vet_logic_score.py` had a SyntaxError at the baseline commit (`151570d`); the baseline
  run excluded it. The SyntaxError was present before `6828dc7` and resolved by a later commit in the chain.

---

## Summary

Commit `6828dc7` is the operator's out-of-band addition of an idempotence test for
`_validate_and_normalize_card` in `tests/test_vet_logic_idempotent.py`. The test calls the
function twice on `{"q": "Question", "a": "Answer"}` and asserts the two outputs are equal
(stable UUID, no mutation on second pass). The test passes GREEN at HEAD. No production code
was modified. All 10 pre-existing `tests/cli/test_vet_logic.py` tests continue to pass at HEAD.
Zero regressions. No fix-forward commit required. Branch HEAD is correct after the operator's edit.

## Machine-checkable data

```json
{
  "packet_version": "2.2",
  "change_id": "flashcore-f83-adopt-6828dc7",
  "adopted_commit": "6828dc70bbc135d65e4daacb44c64d562ce36165",
  "fix_forward_commit": null,
  "base_sha": "151570d1085386c54ac9d3810417d7060764cb1f",
  "head_sha": "22d8b6c42a7c46aff3d68bc44d59833023d03caf",
  "risk_tier": "R1",
  "evidence_classes": ["A", "B", "C", "D", "E", "F"],
  "baseline_tests": {"collected": 10, "passed": 10, "failed": 0},
  "head_tests": {"collected": 12, "passed": 12, "failed": 0},
  "regressions": 0,
  "fix_forward_required": false,
  "canonical_intent": "https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L93"
}
```
