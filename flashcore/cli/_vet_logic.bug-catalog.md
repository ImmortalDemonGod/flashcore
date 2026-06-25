# Bug Catalog for _vet_logic.py

## Overview
The `_validate_and_normalize_card` function processes a card dict before constructing a `Card` model. It maps `q` to `front` and `a` to `back` but fails to remove the legacy `s` (score) field. The `Card` model (models.py) forbids unknown fields (`extra='forbid'`). Consequently, any card YAML containing a valid `s` field triggers a `ValidationError` during vetting, even though `s` is allowed in the YAML schema (yaml_models.py) and should be ignored.

## Bugs Considered
| ID | Bug Description | Blast Radius | Plausibility | Test Type | Reason Skipped |
|----|-----------------|--------------|--------------|-----------|----------------|
| B1 | ValidationError is raised when vetting a card that includes a score (`s`) field. | High – valid cards are rejected, blocking import/export pipelines. | The function maps fields but never removes `s`; `Card` forbids unknown fields. | Captured bug / contract pin (unit test) | — |
| B2 | Missing removal of other unexpected fields could cause similar errors. | Medium – future schema extensions. | Pattern of not sanitizing dict before model construction. | Property‑based (inputs with extra keys) | Deferred – not required for current failure. |
| B3 | `_validate_and_normalize_card` returns mutated dict leaking internal state. | Low – internal use only. | No evidence of external mutation. | N/A — not a bug for current scope. |

## Skipped Bugs
- **B2**: Although plausible, addressing generic extra‑field handling is out of scope for this focused fix; we will add a dedicated test later if needed.
- **B3**: No observable failure; skipping.

## Test Plan
- **Test 1** (`test_vet_accepts_card_with_score_field`) – Captured bug test verifies that vetting a card containing an `s` field does **not** raise `ValidationError`. This test will currently fail, revealing the bug.

## Investigation Notes
- After adding the test, running the suite should produce a failure due to the missing `pop('s')` logic in `_validate_and_normalize_card`.
- Fixing the bug will involve adding `card_data.pop('s', None)` similar to `parser.py`.
