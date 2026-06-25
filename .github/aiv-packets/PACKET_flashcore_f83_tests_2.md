# AIV Verification Packet

## Claim

- **ID**: CLAIM-001
- **Description**: The normalized card dict returned by `_validate_and_normalize_card` does not remove the `s` field, causing ValidationError.
- **Class**: C

## Evidence

### Class A
- Executed test `flashcore/cli/tests/test_vet_logic_score_bug_red.py` asserting presence of `s` and expecting ValidationError.

### Class B
- Git diff includes changes to `flashcore/cli/_vet_logic.py` (none yet) and added test file.

### Class C
- The test demonstrates the bug (absence of stripping `s`).

### Class D
- Lint (ruff) and type checking (mypy) passed.

### Class E
- https://github.com/ImmortalDemonGod/flashcore/blob/fb1ae5a1c1893939f4ff4f82cbd09d4e90f8e965/audit/02-static-audit.md#L93

### Class F
- Claim created in this change, linked to commit SHA.
