# Bug Catalog for flashcore/cli/_vet_logic.py

## Overview
This catalog lists bugs related to the card validation and normalization logic in `_vet_logic.py`, specifically focusing on the handling of the score field (`s`). The public interface of interest is the internal helper `_validate_and_normalize_card(card_data: dict, deck_name: str) -> dict` which is used by the vetting process.

## Bugs

### Bug 1: Score field not removed
- **Bug**: `_validate_and_normalize_card` maps `q` → `front` and `a` → `back` but does **not** remove the `s` (score) field from the card dict.
- **Blast radius**: Any card YAML that includes a valid `s` field (as defined in `yaml_models.py`) will raise a `ValidationError` when instantiated as a `Card`, causing the vetting command to fail incorrectly and preventing the card from being written back.
- **Why plausible**: The function mirrors logic in `parser.py` which correctly pops the `s` field. Missing the `pop` is a classic copy‑paste omission.
- **Test type(s)**: Captured bug / contract pin (unit test that verifies the function drops `s`).

## Skipped Bugs

- **No other fields**: The function correctly maps `q` and `a`; no additional field handling bugs were identified.
- **Future schema changes**: Bugs related to new fields are out of scope for this catalog.

## Evaluation (to be filled after test execution)
- Bugs caught: 
- Bugs characterized: 
- Bugs discovered during writing: 
