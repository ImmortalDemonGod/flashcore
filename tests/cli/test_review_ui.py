"""
Unit tests for the flashcore.cli.review_ui module.
"""

from datetime import date, timedelta
from unittest.mock import ANY, MagicMock, patch
from uuid import uuid4

import pytest

from cultivation.scripts.flashcore.card import Card
from cultivation.scripts.flashcore.cli.review_ui import start_review_flow
from cultivation.scripts.flashcore.review_manager import ReviewSessionManager


@pytest.fixture
def mock_manager() -> MagicMock:
    """Provides a mock ReviewSessionManager."""
    manager = MagicMock(spec=ReviewSessionManager)
    manager.review_queue = []
    return manager


def test_start_review_flow_no_due_cards(mock_manager: MagicMock, capsys):
    """Tests the review flow when no cards are due."""
    # Arrange
    mock_manager.review_queue = []

    # Act
    start_review_flow(mock_manager)

    # Assert
    captured = capsys.readouterr()
    assert "No cards are due for review." in captured.out
    assert "Review session finished." in captured.out
    mock_manager.initialize_session.assert_called_once()
    mock_manager.get_next_card.assert_not_called()


def test_start_review_flow_with_one_card(mock_manager: MagicMock, capsys):
    """Tests the full review flow for a single card."""
    # Arrange
    card_uuid = uuid4()
    mock_card = MagicMock(spec=Card)
    mock_card.uuid = card_uuid
    mock_card.front = "What is the capital of France?"
    mock_card.back = "Paris"

    mock_manager.review_queue = [mock_card]
    mock_manager.get_next_card.side_effect = [mock_card, None]

    # Mock the return value of submit_review to be an updated card
    mock_updated_card = MagicMock(spec=Card)
    # Let's say the card is due in 3 days
    next_due = date.today() + timedelta(days=3)
    mock_updated_card.next_due_date = next_due
    mock_manager.submit_review.return_value = mock_updated_card

    # Act & Assert
    with patch('rich.console.Console.input', side_effect=["", "3"]):
        start_review_flow(mock_manager)

    captured = capsys.readouterr()
    output = captured.out

    # Assert: Check for correct output
    assert "Card 1 of 1" in output
    assert "What is the capital of France?" in output
    assert "Paris" in output
    assert "Next due in 3 days" in output
    assert next_due.strftime('%Y-%m-%d') in output
    assert "Review session finished." in output

    # Assert: Check for correct method calls
    mock_manager.initialize_session.assert_called_once()
    mock_manager.get_next_card.assert_called()
    mock_manager.submit_review.assert_called_once_with(
        card_uuid=card_uuid, rating=3, resp_ms=ANY, eval_ms=ANY
    )


def test_start_review_flow_invalid_rating_input(mock_manager: MagicMock, capsys):
    """Tests that the review flow handles invalid rating inputs and re-prompts."""
    # Arrange
    card_uuid = uuid4()
    mock_card = MagicMock(spec=Card)
    mock_card.uuid = card_uuid
    mock_card.front = "Question"
    mock_card.back = "Answer"

    mock_manager.review_queue = [mock_card]
    mock_manager.get_next_card.side_effect = [mock_card, None]

    # Mock the return value of submit_review to be an updated card
    mock_updated_card = MagicMock(spec=Card)
    mock_updated_card.next_due_date = date.today() + timedelta(days=1)
    mock_manager.submit_review.return_value = mock_updated_card

    # Act
    # Simulate user pressing Enter, then entering 'abc', then '5', then a valid '2'
    with patch('rich.console.Console.input', side_effect=["", "abc", "5", "2"]):
        start_review_flow(mock_manager)

    # Assert
    captured = capsys.readouterr()
    output = captured.out

    # Check that error messages were displayed for invalid inputs
    assert "Invalid input. Please enter a number." in output
    assert "Invalid rating. Please enter a number between 1 and 4." in output

    # Check that submit_review was eventually called with the valid rating
    mock_manager.submit_review.assert_called_once_with(
        card_uuid=card_uuid, rating=2, resp_ms=ANY, eval_ms=ANY
    )

    # Check that the session finished
    assert "Review session finished." in output
