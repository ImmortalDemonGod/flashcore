import pytest
from flashcore.cli._vet_logic import _validate_and_normalize_card
from pydantic import ValidationError

def test_score_field_not_stripped_causes_validation_error():
    """Bug 1: _validate_and_normalize_card fails to remove 's' score field, leading to ValidationError when constructing Card."""
    card_data = {"q": "What?", "a": "Answer", "s": 2}
    deck_name = "test_deck"
    # The function currently returns dict with 's' present; this should cause ValidationError when creating Card
    normalized = _validate_and_normalize_card(card_data, deck_name)
    assert "s" in normalized  # Expect bug: 's' not stripped
    with pytest.raises(ValidationError):
        # Attempt to construct Card should raise due to extra field
        from flashcore.models import Card
        Card(**normalized, deck_name=deck_name)
