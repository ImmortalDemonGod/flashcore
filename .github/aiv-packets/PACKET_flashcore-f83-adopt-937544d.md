# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/flashcore |
| **Change ID** | flashcore-f83-adopt-937544d |
| **Commits** | `937544d` (operator out-of-band) + `58f970f` (fix-forward) |
| **Head SHA** | `58f970f943cc760acde5589abbff97d307d27715` |
| **Base SHA** | `534ce28bf4f070a0921cb0c8fb929a80c05b9cb9` (937544d^) |
| **Risk tier** | R1 |
| **Classification rationale** | Operator commit modifies a test file (`flashcore/cli/test_vet_logic.py`) and its AIV evidence wrapper. The test introduced incorrect key assertions (`"front"`/`"back"` instead of `"q"`/`"a"`) that caused failure at HEAD. Fix-forward commit `58f970f` corrects the assertions without reverting the operator's change. Net result: the test now correctly verifies the `s`-field strip invariant required by the canonical finding. |

## Classification

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "flashcore/cli/test_vet_logic.py"
  classification_rationale: >
    937544d modifies flashcore/cli/test_vet_logic.py (test-only) and
    .github/aiv-evidence/EVIDENCE_FLASHCORE_CLI_TEST_VET_LOGIC.md (documentation).
    No production code was changed. The operator's intent was to strengthen
    the test — renaming it to test_B1_score_field_stripped and adding assertions
    about the expected output shape. The assertions were incorrect for the
    function's actual return format (YAML-format q/a keys, not Card model
    front/back keys). Fix-forward commit 58f970f corrects this. R1 because the
    change touches a test that pins the primary deliverable correctness invariant
    (s-field strip before Card validation).
  classified_by: "fix-pipeline adopt stage"
  classified_at: "2026-06-26T00:00:00Z"
```

## Claims

1. Commit `937544d` changed exactly two files: `flashcore/cli/test_vet_logic.py`
   (test rename + assertion strengthening) and
   `.github/aiv-evidence/EVIDENCE_FLASHCORE_CLI_TEST_VET_LOGIC.md` (metadata update).
   No production Python code was modified.
2. The new assertions introduced by `937544d` (`"front" in result`,
   `"back" in result`, `Card(**result, deck_name="TestDeck")`) were incorrect:
   `_validate_and_normalize_card` returns YAML-format keys (`q`/`a`), not Card
   model keys (`front`/`back`). This caused `test_B1_score_field_stripped` to
   FAIL at HEAD (`fd2e72b`) at `flashcore/cli/test_vet_logic.py:17`.
3. Fix-forward commit `58f970f` corrects the assertions to `"q" in result and
   "a" in result and "uuid" in result` and removes the incorrect
   `Card(**result, deck_name="TestDeck")` call. The operator's test name
   (`test_B1_score_field_stripped`) and core intent (verify `s` is stripped) are
   preserved.
4. At HEAD (`58f970f`), `test_B1_score_field_stripped` PASSES. All 12
   vet-logic tests pass. Zero regressions caused by `937544d` or the fix-forward.
5. The core invariant — `_validate_and_normalize_card` strips the `s` field before
   `Card(...)` instantiation — is verified by `test_B1_score_field_stripped` passing
   at HEAD.

---

## Evidence References

| # | Evidence File | Commit SHA | Classes |
|---|---------------|------------|---------|
| 1 | `evidence/flashcore-f83/CLASS_A_ADOPT_937544D_TEST_RUN.md` | `58f970f` | A, B, F |

---

### Class A (Behavioral/Direct Evidence)

**Evidence artifact:** [`.github/aiv-packets/evidence/flashcore-f83/CLASS_A_ADOPT_937544D_TEST_RUN.md`](https://github.com/ImmortalDemonGod/flashcore/blob/58f970f943cc760acde5589abbff97d307d27715/.github/aiv-packets/evidence/flashcore-f83/CLASS_A_ADOPT_937544D_TEST_RUN.md)

**Baseline (937544d^ = `534ce28`):** 1 test collected in
`flashcore/cli/test_vet_logic.py` (`test_score_field_removed_bug_catch`), FAILED.
Failure reason: `_vet_logic.py` at `534ce28` did not yet contain `pop("s", None)`;
the implementation fix came later at `9c50e27`. The test was intentionally RED at
baseline — it documented the bug before the fix.

**HEAD before fix-forward (`fd2e72b`):** 1 test collected
(`test_B1_score_field_stripped`), FAILED. Failure at line 17:
`assert ('front' in {'a': '4', 'q': 'What is 2+2?', 'uuid': '...'})`.
The implementation fix WAS present but the assertion checked the wrong keys.

**HEAD after fix-forward (`58f970f`):** 12 tests collected across
`flashcore/cli/test_vet_logic.py` (1), `tests/cli/test_vet_logic.py` (10), and
`tests/test_vet_logic_score.py` (1). All 12 PASSED. Zero failures.

Delta vs. baseline: `test_B1_score_field_stripped` now passes (intent of 937544d
achieved); 11 additional tests from `tests/` also verified green.

Verification method: baseline reproduced via `git worktree add /tmp/baseline-937544d 534ce28`
using the shared project venv. Fix-forward HEAD run executed directly in the working
tree at `58f970f` via `pytest flashcore/cli/test_vet_logic.py tests/cli/test_vet_logic.py tests/test_vet_logic_score.py -v`.

### Class B (Referential Evidence — SHA-pinned line anchors)

**937544d changes confirmed:**

- Renamed test: `test_score_field_removed_bug_catch` (at `534ce28`) →
  `test_B1_score_field_stripped` (at `937544d`)
- Added import: `from flashcore.models import Card`
  at [`flashcore/cli/test_vet_logic.py#L3`](https://github.com/ImmortalDemonGod/flashcore/blob/937544ddc75f05f5162c5eb135e3f509ac1f06a1/flashcore/cli/test_vet_logic.py#L3)
- New assertion (incorrect): `assert "front" in result and "back" in result and "uuid" in result`
  at [`flashcore/cli/test_vet_logic.py#L17`](https://github.com/ImmortalDemonGod/flashcore/blob/937544ddc75f05f5162c5eb135e3f509ac1f06a1/flashcore/cli/test_vet_logic.py#L17)
- New call (incorrect): `Card(**result, deck_name="TestDeck")`
  at [`flashcore/cli/test_vet_logic.py#L18`](https://github.com/ImmortalDemonGod/flashcore/blob/937544ddc75f05f5162c5eb135e3f509ac1f06a1/flashcore/cli/test_vet_logic.py#L18)

**Function return format confirmed at HEAD (`58f970f`):**

`_validate_and_normalize_card` builds its return value from `raw_card_dict.copy()` at
[`flashcore/cli/_vet_logic.py#L87`](https://github.com/ImmortalDemonGod/flashcore/blob/58f970f943cc760acde5589abbff97d307d27715/flashcore/cli/_vet_logic.py#L87),
preserving YAML-format keys (`q`/`a`), not mapped Card model keys (`front`/`back`).
The `s` field is stripped at
[`flashcore/cli/_vet_logic.py#L67`](https://github.com/ImmortalDemonGod/flashcore/blob/58f970f943cc760acde5589abbff97d307d27715/flashcore/cli/_vet_logic.py#L67)
and
[`flashcore/cli/_vet_logic.py#L89`](https://github.com/ImmortalDemonGod/flashcore/blob/58f970f943cc760acde5589abbff97d307d27715/flashcore/cli/_vet_logic.py#L89).

**Fix-forward change at `58f970f`:**

Corrected assertion at
[`flashcore/cli/test_vet_logic.py#L17`](https://github.com/ImmortalDemonGod/flashcore/blob/58f970f943cc760acde5589abbff97d307d27715/flashcore/cli/test_vet_logic.py#L17):
`assert "q" in result and "a" in result and "uuid" in result`

Removed incorrect `Card(**result, deck_name="TestDeck")` call (was line 18 at `937544d`).

Model constraint confirmed at:
- [`flashcore/models.py#L51`](https://github.com/ImmortalDemonGod/flashcore/blob/58f970f943cc760acde5589abbff97d307d27715/flashcore/models.py#L51)
  — `extra='forbid'` on `Card` model; any unrecognized field raises `ValidationError`

### Class C (Negative — what was searched for and not found)

- **Production code changes**: `git show 937544d --name-only` returns only
  `flashcore/cli/test_vet_logic.py` and
  `.github/aiv-evidence/EVIDENCE_FLASHCORE_CLI_TEST_VET_LOGIC.md` — no production
  Python files modified. `flashcore/cli/_vet_logic.py` not touched by `937544d`.
- **Regression search**: all 10 tests in `tests/cli/test_vet_logic.py` (10) and
  `tests/test_vet_logic_score.py` (1) pass at HEAD (`58f970f`) — no regressions
  caused by `937544d` or the fix-forward `58f970f`.
- **Silent revert**: `937544d` was not silently reverted. The operator's test name
  (`test_B1_score_field_stripped`) and docstring are preserved unchanged at HEAD;
  no rename or deletion of operator content occurred.
- **Bug B1 at HEAD**: no code path exists where the `s` field reaches `Card(...)`;
  `_vet_logic.py:67` and `#L89` both pop `s` before instantiation and write-back.
  Confirmed by `test_B1_score_field_stripped` PASSING at HEAD.
- **Bug catalog `Skipped` set**: no items — the bug catalog identifies bug B1 as the
  sole plausible defect and records it as covered. No new skipped bugs introduced by
  `937544d` or `58f970f`.

### Class D (Static Analysis)

**On `flashcore/cli/test_vet_logic.py` at HEAD (`58f970f`):**

`flake8 flashcore/cli/test_vet_logic.py`:
```
flashcore/cli/test_vet_logic.py:1:1: F401 'pytest' imported but unused
flashcore/cli/test_vet_logic.py:3:1: F401 'flashcore.models.Card' imported but unused
flashcore/cli/test_vet_logic.py:5:1: E302 expected 2 blank lines, found 1
flashcore/cli/test_vet_logic.py:7:80: E501 line too long (94 > 79 characters)
```

- **F401 (unused imports)**: `import pytest` and `from flashcore.models import Card`
  were added by `937544d` and became unused after the fix-forward removed the
  `Card(**result)` call. These are style-only issues; no correctness impact.
  Cleanup deferred (nice-to-have, not a correctness defect).
- **E302**: pre-existing style issue from `937544d` (missing blank lines before function).
- **E501**: pre-existing style issue from `937544d` (long docstring line).
- None of these issues were introduced by the fix-forward `58f970f` itself.

`mypy flashcore/cli/test_vet_logic.py`: N/A — mypy is not configured for this module
in `pyproject.toml`.

No new correctness errors introduced. `tests/cli/test_vet_logic.py` (10 tests) has no
style issues introduced by this change set.

### Class E (Intent Alignment)

- **Canonical intent URL:**
  `https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L93`

- **Alignment:** The audit record at L93 identifies the root defect:
  `_validate_and_normalize_card()` maps `q`→`front` and `a`→`back` but never removes
  the `s` (score) field, causing `Card(**mapped_card_dict, deck_name=deck_name)` to
  raise `ValidationError` for any YAML card carrying a valid `s` field.

  Commit `937544d` is the operator's refinement of the test that documents this defect.
  The operator's intent — to verify that `_validate_and_normalize_card` strips the `s`
  field and returns a valid card dict — is sound and fully aligned with the audit
  finding. The incorrect key assertions (`front`/`back` instead of `q`/`a`) were a
  technical mistake in the implementation of that intent, not a divergence from it.

  Fix-forward `58f970f` corrects the assertions while fully preserving the operator's
  intent. At HEAD, `test_B1_score_field_stripped` verifies exactly what the audit
  finding requires: that cards with a valid `s` field are processed without
  `ValidationError` and the `s` field is absent from the output.

### Class F (Provenance — git chain-of-custody)

- Commit `937544ddc75f05f5162c5eb135e3f509ac1f06a1` authored by
  `openrouter-driver (fix-pipeline) <noreply@openrouter.ai>`;
  message: `Add test for score field removal`.
- Parent of `937544d` is `534ce28` (`Add bug catalog for _vet_logic`).
- Immediate child of `937544d`: `65fb0f9` (`docs(aiv): verification packet for
  change 'flashcore-f83-tests'`).
- Fix-forward `58f970f` (`fix(flashcore-f83): correct test_B1_score_field_stripped
  key assertions`) is a direct child of `fd2e72b` (current HEAD before this adoption
  packet) and is now the branch HEAD.
- Chain: `937544d` → `65fb0f9` → `ed72871` → `5843fd7` → `6c6705b` → `f0730af` →
  ... → `9c50e27` → ... → `41bfd02` → ... → `485930b` → `fd2e72b` → `58f970f` (HEAD)
  — continuous chain with no gaps.
- `git log --oneline 937544d..HEAD` confirms 27 commits from `937544d` to HEAD
  with no missing links.
- `flashcore/cli/test_vet_logic.py` was touched by `937544d` and corrected by
  `58f970f`. Chain-of-custody is complete and auditable.

---

## Verification Methodology

**Zero-Touch Mandate:** All evidence above is machine-verifiable by the reviewer
without running any tests themselves. Baseline and HEAD test runs were executed by
the pipeline driver and artifacts captured in the evidence directory. The baseline
was reproduced via a temporary git worktree at `534ce28` using the project's shared
venv; the worktree was removed after the run. HEAD runs executed directly in the
working tree at `58f970f`.

---

## Known Limitations

- `import pytest` and `from flashcore.models import Card` are now unused in
  `flashcore/cli/test_vet_logic.py` (F401). These were introduced by `937544d`
  and became unused after the fix-forward removed `Card(**result)`. Style-only;
  no correctness impact. Deferred cleanup (nice-to-have).
- `mypy` is not configured for this module; Class D mypy coverage is N/A.

---

## Summary

Commit `937544d` is an operator out-of-band refinement of the test for the
`s`-field strip invariant in `_validate_and_normalize_card`. The operator renamed
the test to `test_B1_score_field_stripped`, strengthened it with additional
assertions about the output shape, and updated the AIV evidence metadata. The
additional assertions were incorrect: the function returns YAML-format keys (`q`/`a`),
not Card model keys (`front`/`back`), causing the test to fail at HEAD.

Fix-forward commit `58f970f` corrects the key assertions (`"front"` → `"q"`,
`"back"` → `"a"`) and removes the invalid `Card(**result, deck_name="TestDeck")`
call, while fully preserving the operator's intent and test name. At HEAD
(`58f970f`), `test_B1_score_field_stripped` passes and all 12 vet-logic tests
pass. Branch HEAD is correct after both the operator's edit and the fix-forward.

## Machine-checkable data

```json
{
  "packet_version": "2.2",
  "change_id": "flashcore-f83-adopt-937544d",
  "adopted_commit": "937544ddc75f05f5162c5eb135e3f509ac1f06a1",
  "fix_forward_commit": "58f970f943cc760acde5589abbff97d307d27715",
  "base_sha": "534ce28bf4f070a0921cb0c8fb929a80c05b9cb9",
  "head_sha": "58f970f943cc760acde5589abbff97d307d27715",
  "risk_tier": "R1",
  "evidence_classes": ["A", "B", "C", "D", "E", "F"],
  "baseline_tests": {"collected": 1, "passed": 0, "failed": 1},
  "head_tests": {"collected": 12, "passed": 12, "failed": 0},
  "regressions": 0,
  "fix_forward_required": true,
  "fix_forward_commit_message": "fix(flashcore-f83): correct test_B1_score_field_stripped key assertions",
  "canonical_intent": "https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L93"
}
```
