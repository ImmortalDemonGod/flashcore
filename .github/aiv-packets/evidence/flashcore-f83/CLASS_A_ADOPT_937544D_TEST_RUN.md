# Class A Evidence — Adoption of Commit 937544d

## Summary

Operator commit `937544d` ("Add test for score field removal") renamed
`test_score_field_removed_bug_catch` → `test_B1_score_field_stripped` and
strengthened assertions. The new assertions were incorrect: the function
`_validate_and_normalize_card` returns YAML-format keys (`q`/`a`), not Card
model keys (`front`/`back`). A fix-forward commit `58f970f` corrected the
assertions.

---

## Baseline Run (937544d^ = `534ce28`)

**Command:**
```
pytest /tmp/baseline-937544d/flashcore/cli/test_vet_logic.py -v --tb=short
```

**Result:**
```
collected 1 item

../../tmp/baseline-937544d/flashcore/cli/test_vet_logic.py::test_score_field_removed_bug_catch FAILED [100%]

FAILED — pydantic_core._pydantic_core.ValidationError: 1 validation error for Card
s
  Extra inputs are not permitted [type=extra_forbidden, input_value=5, input_type=int]

========================= 1 failed in 0.26s =========================
```

**Interpretation:** At baseline (`534ce28`), `_vet_logic.py` did NOT yet contain
the `s`-field pop. The test was intentionally RED — documenting the bug before
the implementation fix. The baseline test `test_score_field_removed_bug_catch`
correctly detected the missing `pop("s", None)`.

---

## HEAD Run Before Fix-Forward (`fd2e72b`)

**Command:**
```
pytest flashcore/cli/test_vet_logic.py -v --tb=short
```

**Result:**
```
collected 1 item

flashcore/cli/test_vet_logic.py::test_B1_score_field_stripped FAILED [100%]

flashcore/cli/test_vet_logic.py:17: in test_B1_score_field_stripped
    assert "front" in result and "back" in result and "uuid" in result
AssertionError: assert ('front' in {'a': '4', 'q': 'What is 2+2?', 'uuid': 'd0827482-...'})

========================= 1 failed in 0.17s =========================
```

**Root cause:** The implementation fix (`pop("s", None)`) WAS in place at this
point (introduced by `9c50e27`). The test failure was caused by an incorrect
assertion in 937544d: `"front" in result` when the function returns YAML-format
keys `q`/`a` (it transforms internally for Card validation but returns the
original key names for YAML write-back).

---

## HEAD Run After Fix-Forward (`58f970f`)

**Command:**
```
pytest flashcore/cli/test_vet_logic.py tests/cli/test_vet_logic.py tests/test_vet_logic_score.py -v
```

**Result:**
```
collected 12 items

flashcore/cli/test_vet_logic.py::test_B1_score_field_stripped PASSED     [  8%]
tests/cli/test_vet_logic.py::test_vet_logic_no_yaml_files PASSED         [ 16%]
tests/cli/test_vet_logic.py::test_vet_logic_clean_files_check_mode PASSED [ 25%]
tests/cli/test_vet_logic.py::test_vet_logic_dirty_files_check_mode PASSED [ 40%]
tests/cli/test_vet_logic.py::test_vet_logic_dirty_files_modify_mode PASSED [ 50%]
tests/cli/test_vet_logic.py::test_vet_logic_clean_files_modify_mode PASSED [ 33%]
tests/cli/test_vet_logic.py::test_vet_logic_ignores_invalid_yaml_structure PASSED [ 58%]
tests/cli/test_vet_logic.py::test_vet_card_with_invalid_uuid PASSED      [ 66%]
tests/cli/test_vet_logic.py::test_vet_file_processing_exception PASSED   [ 75%]
tests/cli/test_vet_logic.py::test_vet_source_dir_none PASSED             [ 83%]
tests/cli/test_vet_logic.py::test_vet_non_validation_error PASSED        [ 91%]
tests/test_vet_logic_score.py::test_score_field_removed_allows_card_creation PASSED [100%]

========================= 12 passed in 0.13s =========================
```

**Delta vs. baseline:** +11 tests collected (full vet-logic suite now discovered).
`test_B1_score_field_stripped` PASSES after the fix-forward. Zero regressions.

---

## Worktree Chain-of-Custody

- Baseline worktree created at `534ce28` via `git worktree add /tmp/baseline-937544d 534ce28`
- Baseline run used the shared project venv (`.venv/`)
- Worktree removed after baseline capture
- HEAD runs executed directly in the working tree at `58f970f`
