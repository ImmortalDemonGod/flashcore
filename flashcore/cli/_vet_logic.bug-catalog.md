# Bug Catalog for _vet_logic.py

## Summary
The `_validate_and_normalize_card` function maps question (`q`) to `front` and answer (`a`) to `back` but fails to remove the optional `s` (score) field from the raw card data before constructing a `Card` model. The `Card` model (see `flashcore/models.py`) defines `extra='forbid'`, causing a `pydantic.ValidationError` when the `s` field is present. This results in false validation errors during vetting and prevents legitimately scored cards from being processed.

## Bugs

| ID | Description | Blast Radius | Plausibility | Test Type |
|----|-------------|--------------|--------------|-----------|
| B1 | `_validate_and_normalize_card` does not drop the `s` (score) field, causing `Card` instantiation to raise `ValidationError` for any card containing `s`. | Prevents valid cards with scores from being vetted; blocks import/export pipelines. | `s` field is defined in `yaml_models.py` as a valid attribute and other parsers correctly pop it. | Captured bug / contract pin (unit test) |
| B2 | Vetting a card twice should be idempotent – running `_validate_and_normalize_card` on an already‑normalized card should not change its UUID or raise errors. | Duplicate processing could cause UUID churn and inconsistent state. | Current implementation mutates input dict; missing `s` handling may affect idempotence. | Invariant test |

## Skipped Bugs

- **Trailing whitespace handling** – trivial string handling, covered by linter.
- **Missing optional fields other than `s`** – `Card` model already forbids unknown fields; behaviour is exercised by existing validation tests.

## Evaluation (to be filled after test execution)

- Bugs caught:
- Bugs characterized:
- New bugs discovered during test authoring:
