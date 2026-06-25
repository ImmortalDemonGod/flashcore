import pytest
from flashcore.cli._vet_logic import _validate_and_normalize_card
from pydantic import ValidationError

def test_validate_and_normalize_card_does_not_remove_score_field_raises_error():
    """Bug B1: `_validate_and_normalize_card` should drop the `s` field.
    Currently it does not, causing ValidationError for cards with a score.
    This test asserts the current buggy behavior (expecting a ValidationError).
    """
    raw_card = {
        "q": "What is 2+2?",
        "a": "4",
        "s": 5,
    }
    with pytest.raises(ValidationError):
        _validate_and_normalize_card(raw_card, deck_name="Test Deck")
