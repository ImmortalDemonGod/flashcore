"""
Tests for the ReviewProcessor class.

The ReviewProcessor consolidates the core review submission logic that was
previously duplicated between ReviewSessionManager and _review_all_logic.py.
"""

import pytest
from datetime import datetime, timezone, date
from uuid import uuid4
from unittest.mock import MagicMock, patch

from flashcore.models import Card, CardState
from flashcore.db.database import FlashcardDatabase
from flashcore.exceptions import CardOperationError
from flashcore.scheduler import FSRS_Scheduler, SchedulerOutput
from flashcore.review_processor import ReviewProcessor


class TestReviewProcessor:
    """Test the ReviewProcessor class."""

    @pytest.fixture
    def in_memory_db(self):
        """Create an in-memory database for testing."""
        db = FlashcardDatabase(":memory:")
        db.initialize_schema()
        return db

    @pytest.fixture
    def sample_card(self):
        """Create a sample card for testing."""
        return Card(
            uuid=uuid4(),
            deck_name="Test Deck",
            front="What is 2+2?",
            back="4",
            tags={"math"}
        )

    @pytest.fixture
    def mock_scheduler_output(self):
        """Create a mock scheduler output."""
        return SchedulerOutput(
            stab=2.5,
            diff=5.0,
            next_due=date.today(),
            scheduled_days=1,
            review_type="learn",
            elapsed_days=0,
            state=CardState.Learning
        )

    def test_process_review_success(self, in_memory_db, sample_card, mock_scheduler_output):
        """Test successful review processing."""
        # Insert card
        in_memory_db.upsert_cards_batch([sample_card])

        # Create mock scheduler
        mock_scheduler = MagicMock(spec=FSRS_Scheduler)
        mock_scheduler.compute_next_state.return_value = mock_scheduler_output

        # Create processor
        processor = ReviewProcessor(in_memory_db, mock_scheduler)

        # Process review
        rating = 3  # Good
        resp_ms = 1000
        eval_ms = 500
        session_uuid = uuid4()

        updated_card = processor.process_review(
            card=sample_card,
            rating=rating,
            resp_ms=resp_ms,
            eval_ms=eval_ms,
            session_uuid=session_uuid
        )

        # Verify scheduler was called correctly
        mock_scheduler.compute_next_state.assert_called_once()
        call_args = mock_scheduler.compute_next_state.call_args
        assert call_args[1]['new_rating'] == rating

        # Verify card was updated
        assert updated_card is not None
        assert updated_card.state == CardState.Learning

        # Verify review was created
        reviews = in_memory_db.get_reviews_for_card(sample_card.uuid)
        assert len(reviews) == 1

        review = reviews[0]
        assert review.rating == rating
        assert review.resp_ms == resp_ms
        assert review.eval_ms == eval_ms
        assert review.session_uuid == session_uuid
        assert review.stab_after == mock_scheduler_output.stab
        assert review.diff == mock_scheduler_output.diff

    def test_process_review_with_default_timestamp(self, in_memory_db, sample_card, mock_scheduler_output):
        """Test that default timestamp is used when none provided."""
        # Insert card
        in_memory_db.upsert_cards_batch([sample_card])

        # Create mock scheduler
        mock_scheduler = MagicMock(spec=FSRS_Scheduler)
        mock_scheduler.compute_next_state.return_value = mock_scheduler_output

        # Create processor
        processor = ReviewProcessor(in_memory_db, mock_scheduler)

        # Process review without timestamp
        with patch('flashcore.review_processor.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_datetime.timezone = timezone

            processor.process_review(
                card=sample_card,
                rating=3
            )

        # Verify datetime.now was called
        mock_datetime.now.assert_called_once_with(timezone.utc)

        # Verify review has correct timestamp
        reviews = in_memory_db.get_reviews_for_card(sample_card.uuid)
        assert len(reviews) == 1
        assert reviews[0].ts == mock_now

    def test_process_review_with_custom_timestamp(self, in_memory_db, sample_card, mock_scheduler_output):
        """Test that custom timestamp is used when provided."""
        # Insert card
        in_memory_db.upsert_cards_batch([sample_card])

        # Create mock scheduler
        mock_scheduler = MagicMock(spec=FSRS_Scheduler)
        mock_scheduler.compute_next_state.return_value = mock_scheduler_output

        # Create processor
        processor = ReviewProcessor(in_memory_db, mock_scheduler)

        # Process review with custom timestamp
        custom_ts = datetime(2024, 6, 15, 14, 30, 0, tzinfo=timezone.utc)

        processor.process_review(
            card=sample_card,
            rating=3,
            reviewed_at=custom_ts
        )

        # Verify review has custom timestamp
        reviews = in_memory_db.get_reviews_for_card(sample_card.uuid)
        assert len(reviews) == 1
        assert reviews[0].ts == custom_ts

    def test_process_review_without_session_uuid(self, in_memory_db, sample_card, mock_scheduler_output):
        """Test review processing without session UUID."""
        # Insert card
        in_memory_db.upsert_cards_batch([sample_card])

        # Create mock scheduler
        mock_scheduler = MagicMock(spec=FSRS_Scheduler)
        mock_scheduler.compute_next_state.return_value = mock_scheduler_output

        # Create processor
        processor = ReviewProcessor(in_memory_db, mock_scheduler)

        # Process review without session UUID
        processor.process_review(
            card=sample_card,
            rating=3
        )

        # Verify review has no session UUID
        reviews = in_memory_db.get_reviews_for_card(sample_card.uuid)
        assert len(reviews) == 1
        assert reviews[0].session_uuid is None

    def test_process_review_scheduler_error(self, in_memory_db, sample_card):
        """Test error handling when scheduler fails."""
        # Insert card
        in_memory_db.upsert_cards_batch([sample_card])

        # Create mock scheduler that raises error
        mock_scheduler = MagicMock(spec=FSRS_Scheduler)
        mock_scheduler.compute_next_state.side_effect = ValueError("Invalid rating")

        # Create processor
        processor = ReviewProcessor(in_memory_db, mock_scheduler)

        # Process review should raise error
        with pytest.raises(ValueError, match="Invalid rating"):
            processor.process_review(
                card=sample_card,
                rating=5  # Invalid rating
            )

    def test_process_review_database_error(self, in_memory_db, sample_card, mock_scheduler_output):
        """Test error handling when database operation fails."""
        # Insert card
        in_memory_db.upsert_cards_batch([sample_card])

        # Create mock scheduler
        mock_scheduler = MagicMock(spec=FSRS_Scheduler)
        mock_scheduler.compute_next_state.return_value = mock_scheduler_output

        # Mock database to raise error
        with patch.object(in_memory_db, 'add_review_and_update_card') as mock_add_review:
            mock_add_review.side_effect = CardOperationError("Database error")

            # Create processor
            processor = ReviewProcessor(in_memory_db, mock_scheduler)

            # Process review should raise error
            with pytest.raises(CardOperationError, match="Database error"):
                processor.process_review(
                    card=sample_card,
                    rating=3
                )

    def test_process_review_by_uuid_success(self, in_memory_db, sample_card, mock_scheduler_output):
        """Test successful review processing by UUID."""
        # Insert card
        in_memory_db.upsert_cards_batch([sample_card])

        # Create mock scheduler
        mock_scheduler = MagicMock(spec=FSRS_Scheduler)
        mock_scheduler.compute_next_state.return_value = mock_scheduler_output

        # Create processor
        processor = ReviewProcessor(in_memory_db, mock_scheduler)

        # Process review by UUID
        updated_card = processor.process_review_by_uuid(
            card_uuid=sample_card.uuid,
            rating=3,
            resp_ms=1000,
            eval_ms=500
        )

        # Verify card was updated
        assert updated_card is not None
        assert updated_card.uuid == sample_card.uuid

        # Verify review was created
        reviews = in_memory_db.get_reviews_for_card(sample_card.uuid)
        assert len(reviews) == 1

    def test_process_review_by_uuid_card_not_found(self, in_memory_db):
        """Test error when card UUID not found."""
        # Create mock scheduler
        mock_scheduler = MagicMock(spec=FSRS_Scheduler)

        # Create processor
        processor = ReviewProcessor(in_memory_db, mock_scheduler)

        # Process review for non-existent card
        non_existent_uuid = uuid4()
        with pytest.raises(ValueError, match=f"Card {non_existent_uuid} not found"):
            processor.process_review_by_uuid(
                card_uuid=non_existent_uuid,
                rating=3
            )

    def test_review_object_creation_completeness(self, in_memory_db, sample_card, mock_scheduler_output):
        """Test that Review object is created with all required fields."""
        # Insert card
        in_memory_db.upsert_cards_batch([sample_card])

        # Create mock scheduler
        mock_scheduler = MagicMock(spec=FSRS_Scheduler)
        mock_scheduler.compute_next_state.return_value = mock_scheduler_output

        # Create processor
        processor = ReviewProcessor(in_memory_db, mock_scheduler)

        # Process review with all parameters
        rating = 4  # Easy
        resp_ms = 1500
        eval_ms = 800
        session_uuid = uuid4()
        custom_ts = datetime(2024, 6, 15, 14, 30, 0, tzinfo=timezone.utc)

        processor.process_review(
            card=sample_card,
            rating=rating,
            resp_ms=resp_ms,
            eval_ms=eval_ms,
            reviewed_at=custom_ts,
            session_uuid=session_uuid
        )

        # Verify review has all fields correctly set
        reviews = in_memory_db.get_reviews_for_card(sample_card.uuid)
        assert len(reviews) == 1

        review = reviews[0]
        assert review.card_uuid == sample_card.uuid
        assert review.session_uuid == session_uuid
        assert review.ts == custom_ts
        assert review.rating == rating
        assert review.resp_ms == resp_ms
        assert review.eval_ms == eval_ms
        # Handle NaN values properly
        import math
        if sample_card.stability is None:
            assert math.isnan(review.stab_before) or review.stab_before is None
        else:
            assert review.stab_before == sample_card.stability
        assert review.stab_after == mock_scheduler_output.stab
        assert review.diff == mock_scheduler_output.diff
        assert review.next_due == mock_scheduler_output.next_due
        assert review.elapsed_days_at_review == mock_scheduler_output.elapsed_days
        assert review.scheduled_days_interval == mock_scheduler_output.scheduled_days
        assert review.review_type == mock_scheduler_output.review_type

    def test_logging_behavior(self, in_memory_db, sample_card, mock_scheduler_output):
        """Test that appropriate logging occurs."""
        # Insert card
        in_memory_db.upsert_cards_batch([sample_card])

        # Create mock scheduler
        mock_scheduler = MagicMock(spec=FSRS_Scheduler)
        mock_scheduler.compute_next_state.return_value = mock_scheduler_output

        # Create processor
        processor = ReviewProcessor(in_memory_db, mock_scheduler)

        # Process review with logging
        with patch('flashcore.review_processor.logger') as mock_logger:
            processor.process_review(
                card=sample_card,
                rating=3
            )

            # Verify debug logging occurred
            assert mock_logger.debug.call_count >= 2  # Start and end logging

            # Check log messages contain expected content
            debug_calls = [call.args[0] for call in mock_logger.debug.call_args_list]
            assert any("Processing review for card" in msg for msg in debug_calls)
            assert any("Review processed successfully" in msg for msg in debug_calls)


class TestReviewProcessorIntegration:
    """Integration tests for ReviewProcessor with real database and scheduler."""

    @pytest.fixture
    def in_memory_db(self):
        """Create an in-memory database for testing."""
        db = FlashcardDatabase(":memory:")
        db.initialize_schema()
        return db

    @pytest.fixture
    def real_scheduler(self):
        """Create a real FSRS scheduler for integration testing."""
        return FSRS_Scheduler()

    @pytest.fixture
    def sample_card(self):
        """Create a sample card for testing."""
        return Card(
            uuid=uuid4(),
            deck_name="Integration Test Deck",
            front="What is the capital of France?",
            back="Paris",
            tags={"geography", "europe"}
        )

    def test_end_to_end_review_processing(self, in_memory_db, real_scheduler, sample_card):
        """Test complete end-to-end review processing with real components."""
        # Insert card
        in_memory_db.upsert_cards_batch([sample_card])

        # Create processor with real components
        processor = ReviewProcessor(in_memory_db, real_scheduler)

        # Process multiple reviews to test state transitions
        ratings = [3, 4, 2, 3]  # Good, Easy, Hard, Good

        for i, rating in enumerate(ratings):
            updated_card = processor.process_review(
                card=sample_card,
                rating=rating,
                resp_ms=1000 + i * 100,
                eval_ms=500 + i * 50,
                session_uuid=uuid4()
            )

            # Verify card state progresses correctly
            assert updated_card is not None
            assert updated_card.uuid == sample_card.uuid

            # Update sample_card for next iteration
            sample_card = updated_card

        # Verify all reviews were recorded
        reviews = in_memory_db.get_reviews_for_card(sample_card.uuid, order_by_ts_desc=False)
        assert len(reviews) == len(ratings)

        # Verify reviews have correct ratings (reviews are ordered chronologically)
        for i, review in enumerate(reviews):
            assert review.rating == ratings[i]
            assert review.resp_ms == 1000 + i * 100
            assert review.eval_ms == 500 + i * 50

    def test_session_uuid_consistency(self, in_memory_db, real_scheduler, sample_card):
        """Test that session UUID is consistently applied."""
        # Insert card
        in_memory_db.upsert_cards_batch([sample_card])

        # Create processor
        processor = ReviewProcessor(in_memory_db, real_scheduler)

        # Process reviews with and without session UUID
        session_uuid = uuid4()

        # Review 1: With session UUID
        processor.process_review(
            card=sample_card,
            rating=3,
            session_uuid=session_uuid
        )

        # Review 2: Without session UUID
        processor.process_review(
            card=sample_card,
            rating=2,
            session_uuid=None
        )

        # Verify session UUIDs are correctly set
        # Note: get_reviews_for_card returns newest first by default
        reviews = in_memory_db.get_reviews_for_card(sample_card.uuid, order_by_ts_desc=False)
        assert len(reviews) == 2

        # First review (chronologically) should have session_uuid
        assert reviews[0].session_uuid == session_uuid
        # Second review (chronologically) should have no session_uuid
        assert reviews[1].session_uuid is None
