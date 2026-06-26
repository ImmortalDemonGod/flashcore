# Class A Evidence — Adopt 534ce28 Test Run

**Change:** flashcore-f83-adopt-534ce28
**Files changed by 534ce28:** `flashcore/cli/_vet_logic.bug-catalog.md`,
`.github/aiv-evidence/EVIDENCE_FLASHCORE_CLI__VET_LOGIC.BUG_CATALOG.MD.md`
**Type:** Documentation-only; no production code or test files modified.

---

## Baseline (534ce28^ = `fbb81709c82f95ef92e8d4c551bffd9d00fe7170`)

```
pytest flashcore/cli/test_vet_logic.py tests/cli/test_vet_logic.py -v --tb=short
```

```
============================= test session starts ==============================
platform linux -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
collected 11 items

flashcore/cli/test_vet_logic.py::test_score_field_removed_bug_catch FAILED [  9%]
tests/cli/test_vet_logic.py::test_vet_logic_no_yaml_files PASSED         [ 18%]
tests/cli/test_vet_logic.py::test_vet_logic_clean_files_check_mode PASSED [ 27%]
tests/cli/test_vet_logic.py::test_vet_logic_clean_files_modify_mode PASSED [ 36%]
tests/cli/test_vet_logic.py::test_vet_logic_dirty_files_check_mode PASSED [ 45%]
tests/cli/test_vet_logic.py::test_vet_logic_dirty_files_modify_mode PASSED [ 54%]
tests/cli/test_vet_logic.py::test_vet_logic_ignores_invalid_yaml_structure PASSED [ 63%]
tests/cli/test_vet_logic.py::test_vet_card_with_invalid_uuid PASSED      [ 72%]
tests/cli/test_vet_logic.py::test_vet_file_processing_exception PASSED   [ 81%]
tests/cli/test_vet_logic.py::test_vet_source_dir_none PASSED             [ 90%]
tests/cli/test_vet_logic.py::test_vet_non_validation_error PASSED        [100%]

FAILED flashcore/cli/test_vet_logic.py::test_score_field_removed_bug_catch
  flashcore/cli/_vet_logic.py:80: in _validate_and_normalize_card
    card_obj = Card(**mapped_card_dict, deck_name=deck_name)
  pydantic_core._pydantic_core.ValidationError: 1 validation error for Card
  s
    Extra inputs are not permitted [type=extra_forbidden]
========================= 1 failed, 10 passed in 0.12s =========================
```

**Note:** `tests/test_vet_logic_score.py` could not be collected at this commit —
SyntaxError (unterminated string literal at line 11, pre-existing defect introduced
before `534ce28`). The failure of `test_score_field_removed_bug_catch` is intentional
at this baseline: the implementation fix (`pop("s", None)`) was not yet in `_vet_logic.py`
at `fbb8170`; this test was a RED/bug-catch test documenting the defect.

Reproduction: `git worktree add /tmp/baseline-534ce28 fbb81709c82f95ef92e8d4c551bffd9d00fe7170`

---

## HEAD (`6a2bfb0ef8053a0e36a68a3af53c58a9517a4f21`)

```
pytest flashcore/cli/test_vet_logic.py tests/cli/test_vet_logic.py tests/test_vet_logic_score.py -v --tb=short
```

```
============================= test session starts ==============================
platform linux -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
collected 12 items

flashcore/cli/test_vet_logic.py::test_B1_score_field_stripped PASSED     [  8%]
tests/cli/test_vet_logic.py::test_vet_logic_no_yaml_files PASSED         [ 16%]
tests/cli/test_vet_logic.py::test_vet_logic_clean_files_check_mode PASSED [ 25%]
tests/cli/test_vet_logic.py::test_vet_logic_clean_files_modify_mode PASSED [ 33%]
tests/cli/test_vet_logic.py::test_vet_logic_dirty_files_check_mode PASSED [ 41%]
tests/cli/test_vet_logic.py::test_vet_logic_dirty_files_modify_mode PASSED [ 50%]
tests/cli/test_vet_logic.py::test_vet_logic_ignores_invalid_yaml_structure PASSED [ 58%]
tests/cli/test_vet_logic.py::test_vet_card_with_invalid_uuid PASSED      [ 66%]
tests/cli/test_vet_logic.py::test_vet_file_processing_exception PASSED   [ 75%]
tests/cli/test_vet_logic.py::test_vet_source_dir_none PASSED             [ 83%]
tests/cli/test_vet_logic.py::test_vet_non_validation_error PASSED        [ 91%]
tests/test_vet_logic_score.py::test_score_field_removed_allows_card_creation PASSED [100%]

============================== 12 passed in 0.13s ==============================
```

**Delta:** 0 regressions caused by `534ce28`. The change is documentation-only and
cannot cause test failures. The improvement from 1 fail at baseline to 0 fails at HEAD
is entirely attributable to the implementation commits that followed `534ce28` in the chain.
