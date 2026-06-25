# Bug Catalog for `_vet_logic.py`

## Overview
The `_validate_and_normalize_card` function maps question/answer fields but fails to strip the optional score field (`"s"`). This causes a `ValidationError` when the `Card` model (which forbids unknown fields) is instantiated.

## Bugs

### B1: Score field not stripped leads to ValidationError
- **Description**: `_validate_and_normalize_card` returns a dict containing the `"s"` key. The `Card` model in `flashcore/models.py` is defined with `extra = "forbid"`, so passing this dict to `Card(**dict, deck_name=...)` raises a `ValidationError`.
- **Blast radius**: Any YAML card file that includes a score will fail vetting, preventing valid cards from being processed and written back.
- **Why plausible**: The function mirrors logic in `parser.py` which correctly does `card_data.pop("s", None)`. A copy‑paste oversight left out the `pop` call.
- **Test type**: Captured bug / contract pin (red test checking that the bug is present).

## Skipped Bugs
- **S1: Missing required fields (`q` or `a`)** – already covered by existing tests in `tests/cli/test_vet_logic.py`.
- **S2: Invalid deck name handling** – out of scope for this change; separate validation exists elsewhere.

## Evaluation (pre‑implementation)
- **Bugs caught**: None yet – tests to be added will expose B1.
- **Bugs characterized**: None.
- **Bugs discovered during writing**: N/A.
