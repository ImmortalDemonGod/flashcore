# Class A Evidence — Adopt Commit 1d176b1

## Summary

Baseline (1d176b1^ = `2887b02`) → HEAD (`287669945a0d7d024a8d4b32e3be6d9c9ddeaca9`)

| Metric | Baseline (2887b02) | HEAD (2876699) |
|--------|-------------------|----------------|
| tests/cli/test_vet_logic.py | 0 collected / 1 ERROR | 10 collected / 10 PASSED |
| tests/test_vet_logic_score.py | 0 collected / 1 ERROR | 1 collected / 1 PASSED |
| Total | 0 passed, 2 errors | 11 passed, 0 errors |

---

## Baseline Run (2887b02 — 1d176b1^)

`flashcore/cli/_vet_logic.py` at `2887b02` contains diff-format text (not
executable Python), starting with `*** Begin Patch`. Any test file that imports
from this module fails collection with `SyntaxError: invalid syntax` at line 1.

```
$ cd /tmp/baseline-1d176b1-parent
$ pytest tests/cli/test_vet_logic.py -v --tb=short
============================= test session starts ==============================
platform linux -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
collected 0 items / 1 error

==================================== ERRORS ====================================
_________________ ERROR collecting tests/cli/test_vet_logic.py _________________
...
E     File ".../flashcore/cli/_vet_logic.py", line 1
E       *** Begin Patch
E       ^^
E   SyntaxError: invalid syntax
========================= short test summary info ============================
ERROR tests/cli/test_vet_logic.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!!
1 error in <0.20s
```

```
$ pytest tests/test_vet_logic_score.py -v --tb=short
============================= test session starts ==============================
collected 0 items / 1 error

==================================== ERRORS ====================================
________________ ERROR collecting tests/test_vet_logic_score.py ________________
...
E     SyntaxError: unterminated string literal (detected at line 11)
1 error in <0.15s
```

**Baseline verdict:** 0 tests pass. Module is non-importable due to
diff-format-text in place of executable Python.

---

## At-1d176b1 Run (confirming restore)

Worktree at 1d176b1 (`git worktree add /tmp/baseline-1d176b1-head 1d176b1`):

```
$ cd /tmp/baseline-1d176b1-head
$ pytest tests/cli/test_vet_logic.py -v --tb=short
============================= test session starts ==============================
platform linux -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
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

10 passed in 0.13s
```

**At-1d176b1 verdict:** 10 tests pass after the restore. Module is importable.
Score-field strip was not yet in place at 1d176b1 (added later in `9c50e27`).

---

## HEAD Run (2876699)

```
$ pytest tests/cli/test_vet_logic.py tests/test_vet_logic_score.py -v --tb=short
============================= test session starts ==============================
platform linux -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
collected 11 items

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

**HEAD verdict:** 11 tests pass, 0 errors. All 10 tests from 1d176b1 continue
to pass. The score-field strip test (added in `cb9a17a`) also passes.

---

## Delta Summary

- 1d176b1 lifted 0-passing / 1-error to 10-passing / 0-errors for `tests/cli/test_vet_logic.py`.
- Subsequent commits (`9c50e27`, `cb9a17a`) added the score-field strip and
  the score-field test; both present at HEAD.
- Zero regressions from 1d176b1 to HEAD.

---

Reproduced: `git worktree add /tmp/baseline-1d176b1-parent 2887b02` and
`git worktree add /tmp/baseline-1d176b1-head 1d176b1` using the shared project
venv at `/root/flashcore-flashcore-f83/.venv`.
