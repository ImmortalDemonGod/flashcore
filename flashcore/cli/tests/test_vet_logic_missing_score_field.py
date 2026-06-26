import pytest
from flashcore.cli._vet_logic import _validate_and_normalize_card
from flashcore.models import Card
from pydantic import ValidationError

def test_validate_and_normalize_card_preserves_score_field_without_error():
    """Bug: _validate_and_normalize_card does not drop the 's' score field, causing ValidationError.
    Expected behavior: function should remove 's' before Card creation, so no error is raised.
    This test will FAIL (raise ValidationError) until the bug is fixed.
    """
    card_data = {"q": "Question?", "a": "Answer.", "s": 3}
    deck_name = "test_deck"
    # The function returns a dict suitable for Card; we expect no ValidationError when constructing Card.
    normalized = _validate_and_normalize_card(card_data, deck_name)
    # Should not contain 's'
    assert "s" not in normalized
    # Should have front and back
    assert "front" in normalized
    assert "back" in normalized
    # Attempt to create Card should succeed
    try:
        Card(**normalized, deck_name=deck_name)
    except ValidationError as e:
        pytest.fail(f"Card validation failed unexpectedly: {e}")
