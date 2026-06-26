# Class A Evidence — Adoption of Commit 151570d

**Change ID:** flashcore-f83-adopt-151570d  
**Adopted commit:** `151570d1085386c54ac9d3810417d7060764cb1f`  
**Evidence class:** A (Behavioral/Direct)  
**Captured at HEAD:** `b05610c60c9a13e0707100ad5142e2079644d461`

---

## Baseline Run (151570d^ = `1cd34acc`)

At baseline, `tests/test_vet_logic.py` did NOT exist — it was introduced by `151570d`.

Command:
```
git worktree add /tmp/baseline-151570d 1cd34acc5a163047cef66fa2002fc58c11195780
source .venv/bin/activate
pytest tests/cli/test_vet_logic.py -v --tb=short
```

Result:
```
collected 10 items

tests/cli/test_vet_logic.py::test_vet_logic_no_yaml_files PASSED
tests/cli/test_vet_logic.py::test_vet_logic_clean_files_check_mode PASSED
tests/cli/test_vet_logic.py::test_vet_logic_clean_files_modify_mode PASSED
tests/cli/test_vet_logic.py::test_vet_logic_dirty_files_check_mode PASSED
tests/cli/test_vet_logic.py::test_vet_logic_dirty_files_modify_mode PASSED
tests/cli/test_vet_logic.py::test_vet_logic_ignores_invalid_yaml_structure PASSED
tests/cli/test_vet_logic.py::test_vet_card_with_invalid_uuid PASSED
tests/cli/test_vet_logic.py::test_vet_file_processing_exception PASSED
tests/cli/test_vet_logic.py::test_vet_source_dir_none PASSED
tests/cli/test_vet_logic.py::test_vet_non_validation_error PASSED

10 passed in 0.10s
```

**Baseline:** 10 collected, 10 passed, 0 failed.

---

## At-Commit Run (at 151570d)

Verified that `151570d` did not break existing tests and that its new test PASSED at the commit
itself (the bug was present, so the bug-asserting test passed as expected).

Command:
```
git worktree add /tmp/at-151570d 151570d1085386c54ac9d3810417d7060764cb1f
source .venv/bin/activate
pytest tests/test_vet_logic.py tests/cli/test_vet_logic.py -v --tb=short
```

Result:
```
collected 11 items

tests/test_vet_logic.py::test_validate_and_normalize_card_does_not_remove_score_field_raises_error PASSED
tests/cli/test_vet_logic.py::test_vet_logic_no_yaml_files PASSED
tests/cli/test_vet_logic.py::test_vet_logic_clean_files_check_mode PASSED
tests/cli/test_vet_logic.py::test_vet_logic_clean_files_modify_mode PASSED
tests/cli/test_vet_logic.py::test_vet_logic_dirty_files_check_mode PASSED
tests/cli/test_vet_logic.py::test_vet_logic_dirty_files_modify_mode PASSED
tests/cli/test_vet_logic.py::test_vet_logic_ignores_invalid_yaml_structure PASSED
tests/cli/test_vet_logic.py::test_vet_card_with_invalid_uuid PASSED
tests/cli/test_vet_logic.py::test_vet_file_processing_exception PASSED
tests/cli/test_vet_logic.py::test_vet_source_dir_none PASSED
tests/cli/test_vet_logic.py::test_vet_non_validation_error PASSED

11 passed in 0.11s
```

**At 151570d:** 11 collected, 11 passed, 0 failed. The bug-asserting test PASSED because the
production code (`_vet_logic.py`) had not yet been updated to remove the `s` field.

---

## HEAD Run (b05610c)

At HEAD, `tests/test_vet_logic.py` has been updated by subsequent commit `c1ac582`
(`feat(flashcore-f83-impl)`) to reflect the fixed behavior — the test now asserts that
`_validate_and_normalize_card` REMOVES the `s` field (verifies the fix) rather than
asserting it raises `ValidationError` (asserting the bug).

Command:
```
source .venv/bin/activate
pytest tests/test_vet_logic.py tests/cli/test_vet_logic.py -v --tb=short
```

Result:
```
collected 11 items

tests/test_vet_logic.py::test_validate_and_normalize_card_removes_score_field PASSED
tests/cli/test_vet_logic.py::test_vet_logic_no_yaml_files PASSED
tests/cli/test_vet_logic.py::test_vet_logic_clean_files_check_mode PASSED
tests/cli/test_vet_logic.py::test_vet_logic_clean_files_modify_mode PASSED
tests/cli/test_vet_logic.py::test_vet_logic_dirty_files_check_mode PASSED
tests/cli/test_vet_logic.py::test_vet_logic_dirty_files_modify_mode PASSED
tests/cli/test_vet_logic.py::test_vet_logic_ignores_invalid_yaml_structure PASSED
tests/cli/test_vet_logic.py::test_vet_card_with_invalid_uuid PASSED
tests/cli/test_vet_logic.py::test_vet_file_processing_exception PASSED
tests/cli/test_vet_logic.py::test_vet_source_dir_none PASSED
tests/cli/test_vet_logic.py::test_vet_non_validation_error PASSED

11 passed in 0.12s
```

**HEAD:** 11 collected, 11 passed, 0 failed.

---

## Delta Summary

| Phase | Collected | Passed | Failed | Notes |
|-------|-----------|--------|--------|-------|
| Baseline (`151570d^`) | 10 | 10 | 0 | `tests/test_vet_logic.py` did not exist |
| At commit (`151570d`) | 11 | 11 | 0 | Bug-asserting test PASSED (bug present) |
| HEAD (`b05610c`) | 11 | 11 | 0 | Fix-verifying test PASSES (fix applied) |

**Regressions attributable to `151570d`: 0.** Branch HEAD is correct.
