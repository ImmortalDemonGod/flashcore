"""
Unit tests for the flashcore.cli.review_ui module.
"""

from datetime import date, datetime, timezone, timedelta
from unittest.mock import ANY, MagicMock, patch
from uuid import uuid4

import pytest

from flashcore.models import Card
from flashcore.cli.review_ui import start_review_flow
from flashcore.review_manager import ReviewSessionManager


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
    next_due = datetime.now(timezone.utc) + timedelta(days=3)
    mock_updated_card.next_due_date = next_due
    mock_manager.submit_review.return_value = mock_updated_card

    # Act & Assert
    with patch("rich.console.Console.input", side_effect=["", "3"]):
        start_review_flow(mock_manager)

    captured = capsys.readouterr()
    output = captured.out

    # Assert: Check for correct output
    assert "Card 1 of 1" in output
    assert "What is the capital of France?" in output
    assert "Paris" in output
    assert "Next due in 3 days" in output
    assert next_due.strftime("%Y-%m-%d") in output
    assert "Review session finished." in output

    # Assert: Check for correct method calls
    mock_manager.initialize_session.assert_called_once()
    mock_manager.get_next_card.assert_called()
    mock_manager.submit_review.assert_called_once_with(
        card_uuid=card_uuid, rating=3, resp_ms=ANY, eval_ms=ANY
    )


def test_start_review_flow_invalid_rating_input(
    mock_manager: MagicMock, capsys
):
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
    mock_updated_card.next_due_date = datetime.now(timezone.utc) + timedelta(
        days=1
    )
    mock_manager.submit_review.return_value = mock_updated_card

    # Act
    # Simulate user pressing Enter, then entering 'abc', then '5', then a valid '2'
    with patch(
        "rich.console.Console.input", side_effect=["", "abc", "5", "2"]
    ):
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


def test_start_review_flow_submit_review_exception(
    mock_manager: MagicMock, capsys
):
    """Test that submit_review exception advances the queue via skip_card (not masked by [card, None]).

    Uses a closure-based side_effect so skip_card actually empties the queue;
    this ensures the loop terminates because the card was skipped, not because
    the mock coincidentally returned None after one call.
    """
    card = Card(uuid=uuid4(), deck_name="Test", front="Q?", back="A")
    queue = [card]

    def _get_next():
        return queue[0] if queue else None

    def _skip(uuid):
        nonlocal queue
        queue = [c for c in queue if c.uuid != uuid]

    mock_manager.review_queue = list(queue)
    mock_manager.get_next_card.side_effect = _get_next
    mock_manager.skip_card.side_effect = _skip
    mock_manager.submit_review.side_effect = ValueError("Card not found")

    with patch("flashcore.cli.review_ui._display_card", return_value=1000):
        with patch(
            "flashcore.cli.review_ui._get_user_rating", return_value=(3, 500)
        ):
            result = start_review_flow(mock_manager)

    output = capsys.readouterr().out
    assert "Error submitting review" in output
    assert mock_manager.get_next_card.call_count == 2  # card once, None once
    assert mock_manager.skip_card.call_count == 1
    assert mock_manager.skip_card.call_args[0][0] == card.uuid
    assert result is False


def test_start_review_flow_card_without_next_due_date(
    mock_manager: MagicMock, capsys
):
    """Test review flow when updated_card has no next_due_date."""
    card = Card(uuid=uuid4(), deck_name="Test", front="Q?", back="A")

    mock_manager.review_queue = [card]
    mock_manager.get_next_card.side_effect = [card, None]
    mock_manager.get_due_card_count.return_value = 1

    updated_card = MagicMock()
    updated_card.next_due_date = None
    mock_manager.submit_review.return_value = updated_card

    with patch("flashcore.cli.review_ui._display_card", return_value=1000):
        with patch(
            "flashcore.cli.review_ui._get_user_rating", return_value=(3, 500)
        ):
            start_review_flow(mock_manager)

    output = capsys.readouterr().out
    assert "Reviewed." in output


def test_start_review_flow_submit_returns_none(
    mock_manager: MagicMock, capsys
):
    """Test review flow when submit_review returns None."""
    card = Card(uuid=uuid4(), deck_name="Test", front="Q?", back="A")

    mock_manager.review_queue = [card]
    mock_manager.get_next_card.side_effect = [card, None]
    mock_manager.get_due_card_count.return_value = 1
    mock_manager.submit_review.return_value = None

    with patch("flashcore.cli.review_ui._display_card", return_value=1000):
        with patch(
            "flashcore.cli.review_ui._get_user_rating", return_value=(3, 500)
        ):
            start_review_flow(mock_manager)

    output = capsys.readouterr().out
    assert "Error submitting review" in output


# ---------------------------------------------------------------------------
# RED tests for Finding F82 — start_review_flow infinite retry loop
# Bug catalog: tests/cli/test_review_ui.bug-catalog.md
# ---------------------------------------------------------------------------


def test_all_submit_review_fail_output_omits_well_done_guards_against_false_success_message(
    mock_manager: MagicMock, capsys
):
    """When every submit_review call raises, 'Well done!' must NOT appear in output.

    Guards against B2 (review_ui.py:127 prints 'Well done!' unconditionally) and
    B1 (same card retried via continue+get_next_card returning queue[0]).
    The side_effect [card, card, None] explicitly simulates the real stuck-queue
    behavior: after a failed submit the failed card remains at queue[0], so the
    next get_next_card() call returns it again before the session can terminate.
    """
    card = Card(deck_name="Test", front="Q?", back="A")
    mock_manager.review_queue = [card]
    mock_manager.get_next_card.side_effect = [card, card, None]
    mock_manager.submit_review.side_effect = Exception("persistent DB error")

    with patch("flashcore.cli.review_ui._display_card", return_value=500):
        with patch(
            "flashcore.cli.review_ui._get_user_rating", return_value=(2, 300)
        ):
            start_review_flow(mock_manager)

    output = capsys.readouterr().out
    assert "Well done" not in output


def test_persistent_submit_failure_retries_same_card_guards_against_infinite_retry_loop(
    mock_manager: MagicMock, capsys
):
    """When submit_review raises, each card must be attempted exactly once.

    Guards against B1: the continue at review_ui.py:111 returns to the while
    header; get_next_card() then returns queue[0] again (review_manager.py:127)
    because _remove_card_from_queue is only called on the success path
    (review_manager.py:210), creating an unbounded infinite retry loop.

    Uses a closure-based side_effect so skip_card actually advances the queue;
    this verifies the loop is bounded because skip_card was called (not because
    of a coincidental [card, None] shortcut in the mock).
    """
    card = Card(deck_name="Test", front="Q?", back="A")
    queue = [card]

    def _get_next():
        return queue[0] if queue else None

    def _skip(uuid):
        nonlocal queue
        queue = [c for c in queue if c.uuid != uuid]

    mock_manager.review_queue = list(queue)
    mock_manager.get_next_card.side_effect = _get_next
    mock_manager.skip_card.side_effect = _skip
    mock_manager.submit_review.side_effect = Exception("persistent DB error")

    with patch("flashcore.cli.review_ui._display_card", return_value=500):
        with patch(
            "flashcore.cli.review_ui._get_user_rating", return_value=(2, 300)
        ):
            start_review_flow(mock_manager)

    # After the correct fix: skip_card advances the queue, so get_next_card
    # returns None after the first failure. submit_review is called exactly once.
    assert mock_manager.submit_review.call_count == 1


# ---------------------------------------------------------------------------
# New tests for F82 completion contract
# ---------------------------------------------------------------------------


def test_start_review_flow_all_fail_suppresses_well_done(
    mock_manager: MagicMock, capsys
):
    """Three-card queue where all submit_review calls raise.

    Verifies: loop bounded (get_next_card called exactly 4 times: 3 cards + 1
    final None), skip_card called 3 times, 'Well done' absent, 'Review session
    failed' present, and return value is False.
    """
    cards = [
        Card(deck_name="Test", front=f"Q{i}?", back=f"A{i}") for i in range(3)
    ]
    queue = list(cards)

    def _get_next():
        return queue[0] if queue else None

    def _skip(uuid):
        nonlocal queue
        queue = [c for c in queue if c.uuid != uuid]

    mock_manager.review_queue = list(queue)
    mock_manager.get_next_card.side_effect = _get_next
    mock_manager.skip_card.side_effect = _skip
    mock_manager.submit_review.side_effect = Exception("persistent DB error")

    with patch("flashcore.cli.review_ui._display_card", return_value=500):
        with patch(
            "flashcore.cli.review_ui._get_user_rating", return_value=(2, 300)
        ):
            result = start_review_flow(mock_manager)

    output = capsys.readouterr().out
    assert "Well done" not in output
    assert "Review session failed" in output
    assert mock_manager.get_next_card.call_count == 4  # 3 cards + 1 final None
    assert mock_manager.skip_card.call_count == 3
    assert result is False


def test_start_review_flow_success_emits_well_done(
    mock_manager: MagicMock, capsys
):
    """One-card success path: 'Well done!' present and return value is True.

    The [card, None] pattern is valid here because we are testing the success
    path — submit_review itself (in real code) calls _remove_card_from_queue,
    so the queue is empty after success. skip_card must NOT be called.
    """
    card = Card(uuid=uuid4(), deck_name="Test", front="Q?", back="A")
    mock_manager.review_queue = [card]
    mock_manager.get_next_card.side_effect = [card, None]

    updated_card = MagicMock()
    updated_card.next_due_date = datetime.now(timezone.utc) + timedelta(days=1)
    mock_manager.submit_review.return_value = updated_card

    with patch("flashcore.cli.review_ui._display_card", return_value=1000):
        with patch(
            "flashcore.cli.review_ui._get_user_rating", return_value=(3, 500)
        ):
            result = start_review_flow(mock_manager)

    output = capsys.readouterr().out
    assert "Review session finished. Well done!" in output
    assert result is True
    mock_manager.skip_card.assert_not_called()


def test_start_review_flow_mixed_outcome_no_well_done(
    mock_manager: MagicMock, capsys
):
    """Two-card queue: first card succeeds, second fails.

    Exercises the elif (failed_count > 0, success_count > 0) branch in
    start_review_flow (review_ui.py:141-143).  Must emit 'Review session
    finished.' WITHOUT 'Well done', must NOT emit 'Review session failed.',
    and must return True.
    """
    card_ok = Card(uuid=uuid4(), deck_name="Test", front="Q1?", back="A1")
    card_fail = Card(uuid=uuid4(), deck_name="Test", front="Q2?", back="A2")
    queue = [card_ok, card_fail]

    def _get_next():
        return queue[0] if queue else None

    def _skip(uuid):
        nonlocal queue
        queue = [c for c in queue if c.uuid != uuid]

    mock_manager.review_queue = list(queue)
    mock_manager.get_next_card.side_effect = _get_next
    mock_manager.skip_card.side_effect = _skip

    updated_card = MagicMock()
    updated_card.next_due_date = datetime.now(timezone.utc) + timedelta(days=1)

    def _submit(card_uuid, rating, resp_ms, eval_ms):
        if card_uuid == card_ok.uuid:
            queue.pop(0)  # simulate _remove_card_from_queue on success
            return updated_card
        raise Exception("DB error")

    mock_manager.submit_review.side_effect = _submit

    with patch("flashcore.cli.review_ui._display_card", return_value=500):
        with patch(
            "flashcore.cli.review_ui._get_user_rating", return_value=(3, 300)
        ):
            result = start_review_flow(mock_manager)

    output = capsys.readouterr().out
    assert "Review session finished." in output
    assert "Well done" not in output
    assert "Review session failed" not in output
    assert result is True
    mock_manager.skip_card.assert_called_once_with(card_fail.uuid)
