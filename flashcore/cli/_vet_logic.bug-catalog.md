# Bug Catalog for _vet_logic.py

## Summary
The function `_validate_and_normalize_card` incorrectly retains the `s` (score) field when mapping question/answer fields, causing `Card` validation to fail for cards that legitimately include a score.

## Bugs

| ID | Description | Blast Radius | Plausibility | Test Type |
|----|-------------|--------------|--------------|-----------|
| BUG-001 | `s` field not removed leads to ValidationError during vetting, preventing cards with scores from being processed. | Cards with scores are rejected, breaking decks that rely on scoring. | The code maps `q` to `front` and `a` to `back` but never pops `s`, unlike `parser.py`. | Captured bug / contract pin |

## Skipped

- None – all identified plausible bugs are covered.

## Evaluation (to be filled after tests)

- Bugs caught: 
- Bugs characterized: 
- Additional bugs discovered during test writing: 
