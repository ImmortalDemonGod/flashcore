# Bug Catalog for _vet_logic.py

## Summary
The `_validate_and_normalize_card` function in `flashcore/cli/_vet_logic.py` incorrectly retains the `s` (score) field when normalizing card data. The `Card` model forbids extra fields (`extra='forbid'`), causing a `ValidationError` for cards that include a valid `s` field, even though the parser correctly removes it. This results in false errors during vetting and prevents legitimate cards from being written back.

## Cataloged Bugs

| ID | Bug Description | Blast Radius | Plausibility Reason |
|----|-----------------|--------------|---------------------|
| B1 | `s` field not removed leads to ValidationError for valid cards | Prevents valid cards from being processed, causing data loss or aborts | `_validate_and_normalize_card` mirrors logic from `parser.py` but omits `pop('s', None)` |

## Skipped Bugs

- None identified; all plausible bugs are covered.

## Test Plan

- **Test B1**: Provide a card dict containing `q`, `a`, and `s` fields to `_validate_and_normalize_card` and assert that the resulting `Card` instance is created without raising a `ValidationError`. This test should fail (red) with the current buggy implementation.
