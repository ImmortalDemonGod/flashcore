import pytest
from flashcore.cli._vet_logic import _validate_and_normalize_card

def test_idempotent_normalization_keeps_uuid_and_no_error():
    """Bug B2: Vetting twice should be idempotent.
    The function should return the same dict (including uuid) when called on already normalized data.
    """
    raw_card = {"q": "Question", "a": "Answer"}
    first = _validate_and_normalize_card(raw_card, deck_name="Deck")
    second = _validate_and_normalize_card(first, deck_name="Deck")
    assert first == second
