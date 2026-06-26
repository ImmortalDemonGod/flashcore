# Class A Evidence — Behavioral Test Run
## Change: flashcore-f83-adopt-4f3ce12

### Baseline (4f3ce12^ = cb5c6c3efb540cb4f592fa7314c2833956634941)
- Test file extracted: `git show cb5c6c3:flashcore/cli/tests/test_vet_logic_score_bug_red.py`
- Test file state at baseline: red test asserting buggy behavior (`assert "s" in normalized`)
- Run against: HEAD implementation (b31dcfbce4507e71b155ba5821f90e128539854e) which has the fix
- Result: **1 FAILED**

```
flashcore/cli/tests/test_vet_logic_score_bug_red.py::test_score_field_not_stripped_causes_validation_error FAILED

  flashcore/cli/tests/test_vet_logic_score_bug_red.py:11: in test_score_field_not_stripped_causes_validation_error
      assert "s" in normalized  # Expect bug: 's' not stripped
      ^^^^^^^^^^^^^^^^^^^^^^^^
  AssertionError: assert 's' in {'a': 'Answer', 'q': 'What?', 'uuid': 'efc356b0-c7e2-4088-9518-d1c0b59de89f'}

1 failed in 0.28s
```

**Interpretation:** The baseline red test asserts `"s" in normalized`. With the implementation fix present at HEAD (`mapped_card_dict.pop("s", None)` in `_validate_and_normalize_card`), the `s` field IS stripped, so the assertion fails. This confirms the fix is operative.

### HEAD (after fix-forward commit — test_vet_logic_score_bug_red.py corrected)

- Test file state at HEAD after fix-forward: correct green test using YAML-format keys (`q`/`a`/`uuid`)
- Run against: HEAD implementation (same commit)
- Result: **1 PASSED**

```
flashcore/cli/tests/test_vet_logic_score_bug_red.py::test_score_field_not_stripped_causes_validation_error PASSED

1 passed in 0.24s
```

**Interpretation:** The fix-forward commit corrected assertions to match the actual return contract of `_validate_and_normalize_card`: it returns YAML-format keys (`q`/`a`) not Card-model keys (`front`/`back`), and strips `s`.

### Runtime probe (live-fire)
```
>>> _validate_and_normalize_card({"q": "What?", "a": "Answer", "s": 2}, "test_deck")
{'a': 'Answer', 'q': 'What?', 'uuid': '<generated>'}
# keys: ['a', 'q', 'uuid'] — 's' absent, 'q'/'a' preserved in YAML format
```

### Delta
- Baseline test (red, at 4f3ce12^): FAILED (expected — impl has fix, so `"s" in normalized` is False)
- HEAD test (green, after fix-forward): PASSED
- No test that was passing at 4f3ce12^ now fails at HEAD due to 4f3ce12

### Verification method
Baseline reproduced by `git show cb5c6c3:flashcore/cli/tests/test_vet_logic_score_bug_red.py` (the
4f3ce12^ state) then running `pytest flashcore/cli/tests/test_vet_logic_score_bug_red.py -v --tb=short`
against the HEAD implementation. HEAD result reproduced by running the same command with the working-tree
test file after the fix-forward commit.
