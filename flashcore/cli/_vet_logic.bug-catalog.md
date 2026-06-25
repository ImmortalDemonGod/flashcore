# Bug Catalog for _vet_logic

## Public Interface
- Functions: `_validate_and_normalize_card`, `_validate_and_process_cards`, `_sort_and_format_data`, `_process_single_file`.

## Load-bearing comments
- None significant.

## IO Boundaries
- Reads/writes YAML files, generates UUIDs, prints to console.

## Branching points
- Alias mapping for `q`/`a`.
- Removal of empty UUIDs.
- Conversion of string UUIDs.
- Validation via `Card` model.
- Preparation of dict for YAML write.

## Magic-string contracts
- No explicit magic strings besides field names.

## Existing tests
- None for vet logic.

## Bug Catalog
### Bug 1: Score field (`s`) not removed during validation
- **Failure mode**: Cards containing a valid `s` (score) field cause `Card` model validation to fail because `extra='forbid'` forbids unknown fields.
- **Blast radius**: Entire deck fails vetting, preventing legitimate cards with scores from being processed.
- **Why plausible**: `_validate_and_normalize_card` mirrors logic in `parser.py` but omitted the `pop('s', None)` step.
- **Test type**: Captured bug / contract pin (unit test calling the function with a card containing `s`).

### Skipped
- N/A

## Evaluation (to be filled after testing)
- Bugs caught:
- Bugs characterized:
- Bugs discovered during writing:
