# Class A Evidence — Behavioral Test Run
## Change: flashcore-f83-adopt-b760aaf

### Baseline (b760aaf^: 1d176b146da052ba5c05006fe41a3eddfcb007a6)

Baseline produced by: `git worktree add /tmp/baseline-b760aaf b760aaf^` with shared venv
(`source /root/flashcore-flashcore-f83/.venv/bin/activate`).

**`tests/cli/test_vet_logic.py`** — 10 tests collected, 10 passed, 0 failed:

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

10 passed in 0.10s
```

**`tests/test_vet_logic_score.py`** — COLLECTION ERROR (pre-existing syntax error at line 11,
unterminated string literal; not introduced by b760aaf — git show confirms b760aaf did not
touch this file):

```
ERROR collecting tests/test_vet_logic_score.py
SyntaxError: unterminated string literal (detected at line 11)
```

Note on b760aaf itself: at that commit, `flashcore/cli/_vet_logic.py` stores a diff-format
text literal (not valid Python). Any import raises `SyntaxError`. `ccdf7ad` immediately
reinstated parseable Python; the score-field strip was applied in `9c50e27`.

---

### HEAD (66ab5ac3a1f47a98af4acdcfde1e097d80fb1862)

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

11 passed in 0.12s
```

---

### Delta

| Metric | Baseline (b760aaf^) | HEAD |
|--------|---------------------|------|
| `tests/cli/test_vet_logic.py` collected | 10 | 10 |
| `tests/cli/test_vet_logic.py` passed | 10 | 10 |
| `tests/test_vet_logic_score.py` | COLLECTION ERROR (pre-existing) | 1 passed |
| Regressions | — | 0 |

- 0 pre-existing tests regressed.
- `tests/test_vet_logic_score.py` progressed from pre-existing collection error to 1 test
  PASSING (`test_score_field_removed_allows_card_creation`), directly verifying that a card
  carrying an `s` field is now accepted without ValidationError.
