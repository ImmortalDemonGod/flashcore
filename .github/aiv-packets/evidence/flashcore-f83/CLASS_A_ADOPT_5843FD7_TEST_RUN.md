# Class A Evidence — Behavioral Test Run
## Change: flashcore-f83-adopt-5843fd7

### Baseline (5843fd7^: 534ce28e — "Add bug catalog for _vet_logic")

Baseline produced by: `git worktree add /tmp/baseline-5843fd7 534ce28` with shared venv
(`source /root/flashcore-flashcore-f83/.venv/bin/activate`).

Command: `pytest tests/cli/test_vet_logic.py tests/test_vet_logic_idempotent.py -v --tb=short`

Note: `tests/test_vet_logic_score.py` had a SyntaxError (unterminated string literal, line 11)
at commit 534ce28 and could not be collected. It was excluded from the baseline run.
`tests/test_vet_logic_idempotent.py` was present and collected instead.

**11 tests collected, 11 passed, 0 failed:**

```
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
tests/test_vet_logic_idempotent.py::test_idempotent_normalization_keeps_uuid_and_no_error PASSED

11 passed in 0.09s
```

Note: 5843fd7 changed only documentation files (bug catalog markdown and its evidence
wrapper). No production code or test files were modified. The baseline test results are
identical to what existed at 5843fd7^ for all vet-logic-relevant tests.

---

### HEAD (46eaf81cbb14502f77360539f38eb9005a5aeb19)

Command: `pytest tests/cli/test_vet_logic.py tests/test_vet_logic_score.py -v --tb=short`

**11 tests collected, 11 passed, 0 failed:**

```
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
tests/test_vet_logic_score.py::test_score_field_removed_allows_card_creation PASSED

11 passed in 0.11s
```

**Delta:** 0 regressions. The set of 10 vet-logic tests in `tests/cli/test_vet_logic.py`
is identical between baseline and HEAD. At HEAD, `tests/test_vet_logic_score.py` is a
valid, parseable file (the SyntaxError was corrected in a later commit) and its single
test (`test_score_field_removed_allows_card_creation`) passes, directly verifying that
`_validate_and_normalize_card` strips the `s` field before `Card(...)` instantiation.
