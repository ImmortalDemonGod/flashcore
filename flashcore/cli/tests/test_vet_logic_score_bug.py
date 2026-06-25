import pytest
from flashcore.cli._vet_logic import _validate_and_normalize_card
from flashcore.models import Card
from pydantic import ValidationError

def test_score_field_not_stripped_causes_validation_error():
    """Bug 1: _validate_and_normalize_card fails to remove 's' score field, leading to ValidationError when constructing Card."""
    card_data = {"q": "What?", "a": "Answer", "s": 2}
    deck_name = "test_deck"
    normalized = _validate_and_normalize_card(card_data, deck_name)
    # The normalized dict should still contain 's', causing Card validation to fail.
    assert "s" in normalized
    with pytest.raises(ValidationError):
        Card(**normalized, deck_name=deck_name)
