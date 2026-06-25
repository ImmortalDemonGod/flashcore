# Bug Catalog for `flashcore/cli/_vet_logic.py`

## Public Interface
- Internal helper `_validate_and_normalize_card(card_data: dict, deck_name: str) -> dict` used by the vetting CLI to process each YAML card before constructing a `Card` model.

## Load‑bearing comments
- None identified beyond the function docstring.

## IO boundaries
- Reads a dict derived from a YAML file.
- Returns a dict that will be passed to the `Card` Pydantic model which forbids extra fields.

## Branching points / potential bug sites
1. Mapping of keys (`q` → `front`, `a` → `back`).
2. **Missing removal of the `s` (score) field** before `Card` construction.
3. Potential handling of legacy `id` → `uuid` (not present here but mentioned in audit).

## Magic‑string contracts
- `s` field is defined in `yaml_models.py` as `Optional[int]` with limits 0‑4.
- `Card` model (`models.py`) has `extra="forbid"`, so any unexpected key raises `ValidationError`.

## Existing tests
- None target `_validate_and_normalize_card` for the `s` field handling.

## Bug Catalog

### Bug 1: Score field not stripped
- **Bug**: `_validate_and_normalize_card` does not pop the `s` score field, so the resulting dict contains an unexpected key.
- **Blast radius**: Any card YAML that includes a valid `s` field will cause a `ValidationError` during vetting, incorrectly rejecting the card and preventing it from being written back.
- **Why plausible**: The function mirrors `parser.py` which correctly calls `card_data.pop("s", None)`. The omission is a classic copy‑paste mistake.
- **Test type**: Captured‑bug/contract‑pin unit test that asserts the returned dict does not contain `s` and that constructing a `Card` succeeds.

## Skipped Bugs
- No other fields are mishandled (the `q`/`a` mapping is correct).
- Legacy `id` → `uuid` handling is out of scope for this finding.

## Evaluation (to be filled after test run)
- Bugs caught:
- Bugs characterized:
- Bugs discovered during writing:
