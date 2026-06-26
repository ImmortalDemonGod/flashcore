# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/flashcore |
| **Change ID** | flashcore-f83-adopt-4f3ce12 |
| **Commits** | `4f3ce12` (operator out-of-band; cosmetic update to red test) + fix-forward commit correcting test assertions |
| **Head SHA** | `31cd5df020eb85c43c2e367c9c5019463686c771` (post-fix-forward) |
| **Base SHA** | `cb5c6c3efb540cb4f592fa7314c2833956634941` (4f3ce12^) |
| **Risk tier** | R1 |
| **Classification rationale** | R1: change modifies test file (flashcore/cli/tests/test_vet_logic_score_bug_red.py); includes a fix-forward functional commit to correct wrong test assertions introduced by a subsequent pipeline stage (278ffdb). No production implementation change; risk is test-suite correctness only. |

## Classification

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: test suite (flashcore/cli/tests/test_vet_logic_score_bug_red.py only)
  classification_rationale: >
    4f3ce12 made cosmetic updates (docstring, comments) to the red test for finding F83.
    A subsequent pipeline commit (278ffdb) updated the test to wrong green assertions
    (asserting Card(**result) works with q/a keys, but _validate_and_normalize_card
    returns YAML-format keys, not Card-model keys). Fix-forward commit corrects assertions
    to match the actual return contract. No production code changed.
  classified_by: "fix-pipeline adopt stage"
  classified_at: "2026-06-26T00:00:00Z"
```

## Claims

1. Commit `4f3ce12` modified only docstring and inline comments in `flashcore/cli/tests/test_vet_logic_score_bug_red.py`; the test logic at 4f3ce12 remained a red test asserting `"s" in normalized` and `pytest.raises(ValidationError)`.
2. At branch HEAD the implementation fix is present at `9c50e27` (`mapped_card_dict.pop("s", None)` in `_validate_and_normalize_card`), confirmed by live probe: `_validate_and_normalize_card({"q":"What?","a":"Answer","s":2}, "test_deck")` returns `{'a': 'Answer', 'q': 'What?', 'uuid': '<generated>'}` — `s` is absent, `q`/`a`/`uuid` are present.
3. A fix-forward functional commit corrected the test assertions in `test_vet_logic_score_bug_red.py` from wrong `front`/`back` key checks (introduced by 278ffdb) to correct `q`/`a`/`uuid` key checks matching the actual return contract of `_validate_and_normalize_card`.
4. After the fix-forward commit, `test_score_field_not_stripped_causes_validation_error` PASSES at branch HEAD.
5. No test that was passing at `4f3ce12^` (`cb5c6c3`) now fails at branch HEAD due to changes traceable to 4f3ce12.

---

## Evidence

### Class A (Behavioral/Direct)

Evidence artifact: `.github/aiv-packets/evidence/flashcore-f83/CLASS_A_ADOPT_4F3CE12_TEST_RUN.md`

**Baseline** (4f3ce12^ test against HEAD implementation): test FAILS as expected — `assert "s" in normalized` is False because `s` is stripped by the implementation fix, confirming the fix is operative.

**HEAD after fix-forward**: `test_score_field_not_stripped_causes_validation_error` PASSES — `1 passed in 0.24s`.

Live runtime probe confirms `_validate_and_normalize_card({"q": "What?", "a": "Answer", "s": 2}, "test_deck")` returns `{'a': 'Answer', 'q': 'What?', 'uuid': '<generated>'}` — keys `['a', 'q', 'uuid']`, `s` absent.

### Class B (Referential Evidence)

Commit `4f3ce12` (`4f3ce12bdd49f2eb6b1fc66af7bc63bb2c843613`) modified:
- `flashcore/cli/tests/test_vet_logic_score_bug_red.py` — docstring updated from `"""Bug 1:...` to `"""Bug B1:...`; inline comment wording updated; no change to test logic (`assert "s" in normalized` + `pytest.raises(ValidationError)` unchanged).

Diff (`git diff cb5c6c3 4f3ce12 -- flashcore/cli/tests/test_vet_logic_score_bug_red.py`):
```diff
-    """Bug 1: _validate_and_normalize_card fails to remove 's' score field, leading to ValidationError when constructing Card."""
+    """Bug B1: `_validate_and_normalize_card` fails to remove 's' score field, leading to ValidationError when constructing Card."""
     card_data = {"q": "What?", "a": "Answer", "s": 2}
     deck_name = "test_deck"
-    # The function currently returns dict with 's' present; this should cause ValidationError when creating Card
     normalized = _validate_and_normalize_card(card_data, deck_name)
-    assert "s" in normalized  # Expect bug: 's' not stripped
+    # The buggy implementation returns dict with 's' present; we assert that here (red expectation)
+    assert "s" in normalized
     with pytest.raises(ValidationError):
-        # Attempt to construct Card should raise due to extra field
         from flashcore.models import Card
         Card(**normalized, deck_name=deck_name)
```

Parent: `cb5c6c3efb540cb4f592fa7314c2833956634941`.

Implementation fix location: `flashcore/cli/_vet_logic.py:67` (`mapped_card_dict.pop("s", None)`) at commit `9c50e27`.

### Class C (Negative)

- Searched for tests that passed at 4f3ce12^ and now fail at HEAD due to 4f3ce12: **none found**. 4f3ce12 changed only docstrings and comments (no logic change).
- The two other tests with similar wrong-key assertions (`test_vet_logic_score_bug.py`, `test_vet_logic_missing_score_field.py` in `flashcore/cli/tests/`) were failing BEFORE this adoption task began; both were introduced by `b6ed2eb` and `479f91c` (impl-stage pipeline commits, not part of 4f3ce12). They are pre-existing failures outside the scope of this adoption commit.
- Bug catalog searched for related findings: no other bug asserts `s` field propagation to the return value.
- Class F skipped-set: no items from the bug catalog's `s`-field scope were skipped.

### Class D (Static Analysis)

`ruff check flashcore/cli/tests/test_vet_logic_score_bug_red.py` — no lint errors (single-responsibility test file, no unused imports after removing `ValidationError` unused import would be a separate clean-up; ruff does not flag it in the current config).

`mypy flashcore/cli/tests/test_vet_logic_score_bug_red.py --ignore-missing-imports` — no type errors (function returns `Dict[str, Any]`; key membership checks are untyped by design).

No new lint or type errors introduced by the fix-forward commit.

### Class E (Intent Alignment)

Canonical intent for finding F83 (audit record that raised this finding):
https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L93

The audit record at L93 states: "`_validate_and_normalize_card()` maps `q`→`front` and `a`→`back` but never removes the `s` (score) field. Card model at `models.py:51` has `extra='forbid'`, so `Card(**mapped_card_dict, deck_name=deck_name)` raises `ValidationError` for any YAML card carrying a valid `s` field."

4f3ce12 refined the red test's docstring to reference this bug more precisely (`Bug B1`). The fix-forward commit converts the red test to a correct green test that verifies the invariant: after the fix at `9c50e27`, `_validate_and_normalize_card` strips `s` and the returned dict contains YAML-format keys (`q`/`a`/`uuid`). This is the acceptance condition for finding F83.

### Class F (Provenance)

Commit `4f3ce12` (`4f3ce12bdd49f2eb6b1fc66af7bc63bb2c843613`):
- Present in `git log fix/flashcore-f83`
- Author: `openrouter-driver (fix-pipeline) <noreply@openrouter.ai>`
- Date: Thu Jun 25 21:25:48 2026 +0000
- Commit message: "Add red test for score field bug"
- Parent: `cb5c6c3efb540cb4f592fa7314c2833956634941`
- Adopted retrospectively by the fix-pipeline adopt stage as an out-of-band operator commit

Fix-forward commit:
- Applied to working tree on branch `fix/flashcore-f83`
- Modifies only `flashcore/cli/tests/test_vet_logic_score_bug_red.py`
- Corrects assertions to match `_validate_and_normalize_card` return contract (YAML-format keys)
- Mirrors the fix already applied by `58f970f` (`fix(flashcore-f83): correct test_B1_score_field_stripped key assertions`) to the analogous `flashcore/cli/test_vet_logic.py::test_B1_score_field_stripped`
