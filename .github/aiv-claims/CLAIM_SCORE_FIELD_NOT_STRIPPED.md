# AIV Verification Packet

## Claim

- **ID**: CLAIM-001
- **Description**: The normalized card dict returned by `_validate_and_normalize_card` **does not** have the `s` field removed, i.e., it **contains** the `s` field.
- **Class**: C
- **Evidence**: The function returns a dict where `'s'` key is present when input includes it.

## Evidence Class C

- The output of `_validate_and_normalize_card` **contains** the `s` field, therefore it does **not** lack the `s` field as would be correct behavior.
