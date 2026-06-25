# Bug Catalog for _vet_logic.py

## Summary
The `_validate_and_normalize_card` function maps fields `q` → `front` and `a` → `back` but fails to remove the `s` (score) field from the raw card data. The `Card` model (`flashcore/models.py`) defines `extra='forbid'`, causing a `ValidationError` when a card dict still contains `s`. The parser (`flashcore/parser.py`) correctly pops `s` before constructing a `Card`. Consequently, vetting cards that include a valid `s` field incorrectly raises a validation error, preventing the card from being written back.

## Bugs
| ID | Bug Description | Blast Radius | Plausibility Reason | Test Type |
|----|-----------------|--------------|---------------------|-----------|
| B1 | `_validate_and_normalize_card` does not remove the `s` (score) field, causing `ValidationError` for cards that include a score. | Any card with a score field fails vetting, leading to data loss and user confusion. | The function mirrors logic from `parser.py` but omits the `pop('s', None)` step. | Captured bug / contract pin (red test) |

## Skipped Bugs
- None – all plausible bugs around field handling are covered.

## Evaluation (to be filled after test run)
- Bugs caught:
- Bugs characterized:
- New bugs discovered during writing:
