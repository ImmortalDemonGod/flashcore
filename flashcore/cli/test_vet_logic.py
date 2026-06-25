import pytest
from flashcore.cli._vet_logic import _validate_and_normalize_card
from flashcore.yaml_models import CardYAML
from pydantic import ValidationError

def test_vet_accepts_card_with_score_field():
    """Bug B1: ValidationError is raised when vetting a card that includes a score ('s') field.
    The test expects no ValidationError, thus currently fails.
    """
    # Simulate a card dict as parsed from YAML with a score field
    card_data = {
        "q": "What is the capital of France?",
        "a": "Paris",
        "s": 5,  # score field that should be ignored by vetting
    }
    # The function should remove/ignore the score field before constructing Card
    normalized = _validate_and_normalize_card(card_data, deck_name="default")
    # Attempt to construct Card model (should not raise)
    try:
        card = CardYAML(**normalized, deck_name="default")
    except ValidationError as e:
        pytest.fail(f"ValidationError raised unexpectedly: {e}")
