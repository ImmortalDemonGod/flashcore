"""
Unit tests for the flashcore.cli._review_all_logic module.
"""

from datetime import date, datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
import re

from flashcore.models import Card, CardState
from flashcore.cli._review_all_logic import (
    review_all_logic,
    _get_all_due_cards,
    _submit_single_review,
)


def strip_ansi_codes(text: str) -> str:
    """
    Strip ANSI escape sequences (SGR color/style codes) from the given text.

    Parameters:
        text (str): Input string that may contain ANSI escape sequences like `\x1b[31m` or `\x1b[0m`.

    Returns:
        clean_text (str): The input string with ANSI escape sequences removed.
    """
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


@pytest.fixture
def mock_db_manager():
    """Mock FlashcardDatabase instance."""
    mock_db = MagicMock()
    mock_db.initialize_schema.return_value = None
    return mock_db


@pytest.fixture
def mock_scheduler():
    """Mock FSRS_Scheduler instance."""
    mock_scheduler = MagicMock()
    return mock_scheduler


@pytest.fixture
def sample_cards():
    """
    Create three sample Card objects for use in tests.

    Each card has a unique UUID, front/back text "Question N"/"Answer N", deck names alternating between "Deck 1" and "Deck 2", tags set to ["test"], timestamps set to the current UTC time, state `CardState.New`, and review-related fields (`last_review_id`, `next_due_date`, `stability`, `difficulty`) set to None.

    Returns:
        list[Card]: A list containing the three sample Card instances.
    """
    cards = []
    for i in range(3):
        card = Card(
            uuid=uuid4(),
            front=f"Question {i+1}",
            back=f"Answer {i+1}",
            deck_name=f"Deck {i % 2 + 1}",  # Alternates between Deck 1 and Deck 2
            tags=["test"],
            added_at=datetime.now(timezone.utc),
            modified_at=datetime.now(timezone.utc),
            state=CardState.New,
            last_review_id=None,
            next_due_date=None,
            stability=None,
            difficulty=None,
        )
        cards.append(card)
    return cards


class TestReviewAllLogic:
    """Tests for the main review_all_logic function."""

    @patch("flashcore.cli._review_all_logic.FlashcardDatabase")
    @patch("flashcore.cli._review_all_logic.FSRS_Scheduler")
    @patch("flashcore.cli._review_all_logic._get_all_due_cards")
    def test_review_all_logic_no_due_cards(
        self,
        mock_get_cards,
        _mock_scheduler_class,
        _mock_db_class,
        capsys,
        tmp_path,
    ):
        """Test review_all_logic when no cards are due."""
        # Arrange
        mock_get_cards.return_value = []

        # Act
        review_all_logic(db_path=tmp_path / "test.db", limit=10)

        # Assert
        captured = capsys.readouterr()
        assert "No cards are due for review across any deck." in captured.out
        assert "Review session finished." in captured.out
        mock_get_cards.assert_called_once()

    @patch("flashcore.cli._review_all_logic.FlashcardDatabase")
    @patch("flashcore.cli._review_all_logic.FSRS_Scheduler")
    @patch("flashcore.cli._review_all_logic._get_all_due_cards")
    @patch("flashcore.cli._review_all_logic._display_card")
    @patch("flashcore.cli._review_all_logic._get_user_rating")
    @patch("flashcore.cli._review_all_logic._submit_single_review")
    def test_review_all_logic_with_cards_success(
        self,
        mock_submit,
        mock_get_rating,
        mock_display,
        mock_get_cards,
        _mock_scheduler_class,
        _mock_db_class,
        sample_cards,
        capsys,
        tmp_path,
    ):
        """Test review_all_logic with successful card reviews."""
        # Arrange
        mock_get_cards.return_value = sample_cards[:2]  # Use first 2 cards
        mock_display.return_value = 1000  # 1 second response time
        mock_get_rating.side_effect = [
            (2, 1500),
            (3, 1200),
        ]  # (rating, eval_ms) tuples

        # Mock successful reviews
        updated_cards = []
        for card in sample_cards[:2]:
            updated_card = MagicMock()
            updated_card.next_due_date = date.today() + timedelta(days=1)
            updated_cards.append(updated_card)
        mock_submit.side_effect = updated_cards

        # Act
        review_all_logic(db_path=tmp_path / "test.db", limit=10)

        # Assert
        captured = capsys.readouterr()
        clean_output = strip_ansi_codes(captured.out)
        assert "Found 2 due cards across 2 decks:" in clean_output
        assert "Deck 1: 1 cards" in clean_output
        assert "Deck 2: 1 cards" in clean_output
        assert "Review session complete! Reviewed 2 cards." in clean_output

        # Verify all cards were processed
        assert mock_display.call_count == 2
        assert mock_get_rating.call_count == 2
        assert mock_submit.call_count == 2

    @patch("flashcore.cli._review_all_logic.FlashcardDatabase")
    @patch("flashcore.cli._review_all_logic.FSRS_Scheduler")
    @patch("flashcore.cli._review_all_logic._get_all_due_cards")
    @patch("flashcore.cli._review_all_logic._display_card")
    @patch("flashcore.cli._review_all_logic._get_user_rating")
    @patch("flashcore.cli._review_all_logic._submit_single_review")
    def test_review_all_logic_with_review_error(
        self,
        mock_submit,
        mock_get_rating,
        mock_display,
        mock_get_cards,
        _mock_scheduler_class,
        _mock_db_class,
        sample_cards,
        capsys,
        tmp_path,
    ):
        """Test review_all_logic when review submission fails."""
        # Arrange
        mock_get_cards.return_value = [sample_cards[0]]
        mock_display.return_value = 1000
        mock_get_rating.return_value = (2, 1500)  # (rating, eval_ms) tuple
        mock_submit.side_effect = Exception("Database error")

        # Act
        review_all_logic(db_path=tmp_path / "test.db", limit=10)

        # Assert
        captured = capsys.readouterr()
        clean_output = strip_ansi_codes(captured.out)
        assert "Error reviewing card: Database error" in clean_output
        assert "Review session complete! Reviewed 1 cards." in clean_output

    @patch("flashcore.cli._review_all_logic.FlashcardDatabase")
    @patch("flashcore.cli._review_all_logic.FSRS_Scheduler")
    @patch("flashcore.cli._review_all_logic._get_all_due_cards")
    @patch("flashcore.cli._review_all_logic._display_card")
    @patch("flashcore.cli._review_all_logic._get_user_rating")
    @patch("flashcore.cli._review_all_logic._submit_single_review")
    def test_review_all_logic_with_failed_review(
        self,
        mock_submit,
        mock_get_rating,
        mock_display,
        mock_get_cards,
        _mock_scheduler_class,
        _mock_db_class,
        sample_cards,
        capsys,
        tmp_path,
    ):
        """Test review_all_logic when review returns None (failed)."""
        # Arrange
        mock_get_cards.return_value = [sample_cards[0]]
        mock_display.return_value = 1000
        mock_get_rating.return_value = (2, 1500)  # (rating, eval_ms) tuple
        mock_submit.return_value = None  # Failed review

        # Act
        review_all_logic(db_path=tmp_path / "test.db", limit=10)

        # Assert
        captured = capsys.readouterr()
        clean_output = strip_ansi_codes(captured.out)
        assert (
            "Error submitting review. Card will be reviewed again later."
            in clean_output
        )


class TestGetAllDueCards:
    """Tests for the _get_all_due_cards function."""

    @patch("flashcore.cli._review_all_logic.db_row_to_card")
    def test_get_all_due_cards_success(
        self, mock_db_row_to_card, mock_db_manager, sample_cards
    ):
        """Test _get_all_due_cards with successful database query."""
        # Arrange
        mock_conn = MagicMock()
        mock_db_manager.get_connection.return_value = mock_conn

        # Mock cursor result (fetchall + description)
        mock_result = MagicMock()
        mock_result.description = [
            ("uuid",),
            ("front",),
            ("back",),
            ("deck_name",),
        ]
        mock_result.fetchall.return_value = [
            (
                str(sample_cards[0].uuid),
                sample_cards[0].front,
                sample_cards[0].back,
                sample_cards[0].deck_name,
            ),
            (
                str(sample_cards[1].uuid),
                sample_cards[1].front,
                sample_cards[1].back,
                sample_cards[1].deck_name,
            ),
        ]
        mock_conn.execute.return_value = mock_result

        # Mock db_utils.db_row_to_card
        mock_db_row_to_card.side_effect = sample_cards[:2]

        # Act
        result = _get_all_due_cards(mock_db_manager, date.today(), 10)

        # Assert
        assert len(result) == 2
        assert result == sample_cards[:2]
        mock_conn.execute.assert_called_once()

        # Verify SQL query structure
        call_args = mock_conn.execute.call_args
        sql = call_args[0][0]
        params = call_args[0][1]
        assert "WHERE next_due_date <= $1 OR next_due_date IS NULL" in sql
        assert "ORDER BY" in sql
        assert "LIMIT $2" in sql
        assert params == [date.today(), 10]

    def test_get_all_due_cards_empty_result(self, mock_db_manager):
        """Test _get_all_due_cards with empty database result."""
        # Arrange
        mock_conn = MagicMock()
        mock_db_manager.get_connection.return_value = mock_conn

        mock_result = MagicMock()
        mock_result.description = [("uuid",)]
        mock_result.fetchall.return_value = []
        mock_conn.execute.return_value = mock_result

        # Act
        result = _get_all_due_cards(mock_db_manager, date.today(), 10)

        # Assert
        assert result == []

    def test_get_all_due_cards_database_error(self, mock_db_manager, capsys):
        """Test _get_all_due_cards with database error."""
        # Arrange
        mock_conn = MagicMock()
        mock_db_manager.get_connection.return_value = mock_conn
        mock_conn.execute.side_effect = Exception("Database connection failed")

        # Act
        result = _get_all_due_cards(mock_db_manager, date.today(), 10)

        # Assert
        assert result == []
        captured = capsys.readouterr()
        assert (
            "Error fetching due cards: Database connection failed"
            in captured.out
        )


class TestSubmitSingleReview:
    """Tests for the _submit_single_review function."""

    def test_submit_single_review_success(
        self, mock_db_manager, mock_scheduler, sample_cards
    ):
        """Test _submit_single_review with successful review submission."""
        # Arrange
        card = sample_cards[0]
        rating = 2
        resp_ms = 1500
        review_ts = datetime.now(timezone.utc)

        # Mock review history
        mock_db_manager.get_reviews_for_card.return_value = []

        # Mock scheduler output
        mock_scheduler_output = MagicMock()
        mock_scheduler_output.stab = 2.5
        mock_scheduler_output.diff = 5.0
        mock_scheduler_output.next_due = date.today() + timedelta(days=1)
        mock_scheduler_output.elapsed_days = 0
        mock_scheduler_output.scheduled_days = 1
        mock_scheduler_output.review_type = "learn"
        mock_scheduler_output.state = CardState.Learning
        mock_scheduler.compute_next_state.return_value = mock_scheduler_output

        # Mock database update
        updated_card = MagicMock()
        mock_db_manager.add_review_and_update_card.return_value = updated_card

        # Act
        result = _submit_single_review(
            mock_db_manager,
            mock_scheduler,
            card,
            rating,
            resp_ms,
            eval_ms=1000,
            reviewed_at=review_ts,
        )

        # Assert
        assert result == updated_card
        mock_scheduler.compute_next_state.assert_called_once()
        mock_db_manager.add_review_and_update_card.assert_called_once()

        # Verify review object creation
        call_args = mock_db_manager.add_review_and_update_card.call_args
        review = call_args[1]["review"]
        assert review.card_uuid == card.uuid
        assert (
            review.rating == rating
        )  # Unified 1-4 rating scale, no conversion needed
        assert review.resp_ms == resp_ms
        assert review.eval_ms == 1000
        assert review.ts == review_ts

    def test_submit_single_review_default_timestamp(
        self, mock_db_manager, mock_scheduler, sample_cards
    ):
        """Test _submit_single_review with default timestamp."""
        # Arrange
        card = sample_cards[0]
        mock_db_manager.get_reviews_for_card.return_value = []

        mock_scheduler_output = MagicMock()
        mock_scheduler_output.state = CardState.Learning
        mock_scheduler_output.stab = 2.0
        mock_scheduler_output.diff = 5.0
        mock_scheduler_output.next_due = date.today() + timedelta(days=1)
        mock_scheduler_output.elapsed_days = 0
        mock_scheduler_output.scheduled_days = 1
        mock_scheduler_output.review_type = "learn"
        mock_scheduler.compute_next_state.return_value = mock_scheduler_output

        updated_card = MagicMock()
        mock_db_manager.add_review_and_update_card.return_value = updated_card

        # Act
        with patch("flashcore.review_processor.datetime") as mock_datetime:
            mock_now = datetime.now(timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_datetime.timezone = timezone  # Preserve timezone reference

            result = _submit_single_review(
                mock_db_manager, mock_scheduler, card, 2
            )

        # Assert
        assert result == updated_card
        mock_datetime.now.assert_called_once_with(timezone.utc)

    def test_submit_single_review_database_error(
        self, mock_db_manager, mock_scheduler, sample_cards, capsys
    ):
        """Test _submit_single_review with database error."""
        # Arrange
        card = sample_cards[0]
        mock_db_manager.get_reviews_for_card.return_value = []

        mock_scheduler_output = MagicMock()
        mock_scheduler_output.state = CardState.Learning
        mock_scheduler_output.stab = 2.0
        mock_scheduler_output.diff = 5.0
        mock_scheduler_output.next_due = date.today() + timedelta(days=1)
        mock_scheduler_output.elapsed_days = 0
        mock_scheduler_output.scheduled_days = 1
        mock_scheduler_output.review_type = "learn"
        mock_scheduler.compute_next_state.return_value = mock_scheduler_output

        mock_db_manager.add_review_and_update_card.side_effect = Exception(
            "Database error"
        )

        # Act
        result = _submit_single_review(
            mock_db_manager, mock_scheduler, card, 2
        )

        # Assert
        assert result is None
        captured = capsys.readouterr()
        assert "Error submitting review: Database error" in captured.out

    def test_submit_single_review_scheduler_error(
        self, mock_db_manager, mock_scheduler, sample_cards, capsys
    ):
        """Test _submit_single_review with scheduler error."""
        # Arrange
        card = sample_cards[0]
        mock_db_manager.get_reviews_for_card.return_value = []
        mock_scheduler.compute_next_state.side_effect = Exception(
            "Scheduler error"
        )

        # Act
        result = _submit_single_review(
            mock_db_manager, mock_scheduler, card, 2
        )

        # Assert
        assert result is None
        captured = capsys.readouterr()
        assert "Error submitting review: Scheduler error" in captured.out


class TestIntegration:
    """Integration tests for the review-all functionality."""

    @patch("flashcore.cli._review_all_logic.FlashcardDatabase")
    @patch("flashcore.cli._review_all_logic.FSRS_Scheduler")
    @patch("flashcore.cli._review_all_logic._display_card")
    @patch("flashcore.cli._review_all_logic._get_user_rating")
    @patch("flashcore.cli._review_all_logic.db_row_to_card")
    def test_review_all_logic_integration(
        self,
        mock_db_row_to_card,
        mock_get_rating,
        mock_display,
        mock_scheduler_class,
        mock_db_class,
        sample_cards,
        tmp_path,
    ):
        """Integration test for the complete review-all workflow."""
        # Arrange - configure context manager to return mock_db
        mock_db = mock_db_class.return_value
        mock_db.__enter__ = MagicMock(return_value=mock_db)
        mock_db.__exit__ = MagicMock(return_value=False)
        mock_scheduler = mock_scheduler_class.return_value

        # Create a test card that will be returned by db_row_to_card
        test_card = sample_cards[0].model_copy(deep=True)
        test_card.tags = set()  # Empty tags to match actual behavior

        # Mock database connection and query
        mock_conn = MagicMock()
        mock_db.get_connection.return_value = mock_conn
        mock_result = MagicMock()
        mock_result.description = [
            ("uuid",),
            ("front",),
            ("back",),
            ("deck_name",),
        ]
        mock_result.fetchall.return_value = [
            (
                str(sample_cards[0].uuid),
                sample_cards[0].front,
                sample_cards[0].back,
                sample_cards[0].deck_name,
            ),
        ]
        mock_conn.execute.return_value = mock_result
        mock_db_row_to_card.return_value = test_card

        # Mock review components
        mock_display.return_value = 1000
        mock_get_rating.return_value = (2, 1500)  # (rating, eval_ms) tuple
        mock_db.get_reviews_for_card.return_value = []

        # Mock scheduler
        mock_scheduler_output = MagicMock()
        mock_scheduler_output.state = CardState.Learning
        mock_scheduler_output.stab = 2.0
        mock_scheduler_output.diff = 5.0
        mock_scheduler_output.next_due = date.today() + timedelta(days=1)
        mock_scheduler_output.elapsed_days = 0
        mock_scheduler_output.scheduled_days = 1
        mock_scheduler_output.review_type = "learn"
        mock_scheduler.compute_next_state.return_value = mock_scheduler_output

        # Mock successful database update
        updated_card = MagicMock()
        updated_card.next_due_date = date.today() + timedelta(days=1)
        mock_db.add_review_and_update_card.return_value = updated_card

        # Act
        review_all_logic(db_path=tmp_path / "test.db", limit=1)

        # Assert - verify the complete workflow
        mock_db.initialize_schema.assert_called_once()
        mock_conn.execute.assert_called_once()
        mock_display.assert_called_once_with(test_card)
        mock_get_rating.assert_called_once()
        mock_scheduler.compute_next_state.assert_called_once()
        mock_db.add_review_and_update_card.assert_called_once()
