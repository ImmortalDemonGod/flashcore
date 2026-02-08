"""
Unit and integration tests for ReviewSessionManager in flashcore.review_manager.
"""

import pytest
import uuid
from collections import deque
from datetime import date, datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from flashcore.models import Card, Review, CardState, Rating
from flashcore.db.database import FlashcardDatabase
from flashcore.exceptions import CardOperationError
from flashcore.scheduler import FSRS_Scheduler, SchedulerOutput
from flashcore.review_manager import ReviewSessionManager

# --- Fixtures ---


@pytest.fixture
def mock_db() -> MagicMock:
    """
    Create a MagicMock preconfigured to mimic a FlashcardDatabase for tests.
    
    The mock exposes a CardOperationError attribute and sensible default return values for common database methods used in tests (empty lists or None), and provides a MagicMock for add_review_and_update_card.
    
    Returns:
        MagicMock: A MagicMock with the FlashcardDatabase spec and configured defaults.
    """
    db = MagicMock(spec=FlashcardDatabase)
    db.CardOperationError = CardOperationError
    db.get_due_cards.return_value = []
    db.get_card_by_uuid.return_value = None
    db.get_reviews_for_card.return_value = []
    db.add_review_and_update_card = MagicMock()
    db.get_due_card_count.return_value = 0
    return db


@pytest.fixture
def mock_scheduler() -> MagicMock:
    """Provides a MagicMock for FSRS_Scheduler."""
    scheduler = MagicMock(spec=FSRS_Scheduler)
    scheduler.compute_next_state.return_value = SchedulerOutput(
        stab=10.0,
        diff=5.0,
        state=CardState.Review,
        next_due=date.today() + timedelta(days=10),
        scheduled_days=10,
        review_type="review",
        elapsed_days=1,
    )
    return scheduler


@pytest.fixture
def sample_card_data() -> dict:
    """
    Provide a sample card data dictionary for tests.
    
    Returns:
        dict: A dictionary representing a sample flashcard with keys:
            - uuid (UUID): Randomly generated UUID for the card.
            - deck_name (str): Name of the deck ("Test Deck").
            - front (str): Front text of the card ("Test Front").
            - back (str): Back text of the card ("Test Back").
            - added_at (datetime): UTC timestamp set to 30 days before now.
    """
    return {
        "uuid": uuid.uuid4(),
        "deck_name": "Test Deck",
        "front": "Test Front",
        "back": "Test Back",
        "added_at": datetime.now(timezone.utc) - timedelta(days=30),
    }


@pytest.fixture
def sample_card(sample_card_data: dict) -> Card:
    """
    Create a Card instance from a mapping of card fields.
    
    Parameters:
        sample_card_data (dict): Dictionary containing card attributes (e.g., "uuid", "deck_name", "front", "back", "added_at") used to construct the Card.
    
    Returns:
        Card: A Card object populated with values from `sample_card_data`.
    """
    return Card(**sample_card_data)


@pytest.fixture
def review_manager(
    mock_db: MagicMock, mock_scheduler: MagicMock
) -> ReviewSessionManager:
    """Provides a ReviewSessionManager instance with mocked DB and scheduler."""
    return ReviewSessionManager(
        db_manager=mock_db,
        scheduler=mock_scheduler,
        user_uuid=uuid.uuid4(),
        deck_name="Test Deck",
    )


@pytest.fixture
def in_memory_db() -> FlashcardDatabase:
    """
    Create a FlashcardDatabase backed by an in-memory SQLite database for integration tests.
    
    Returns:
        FlashcardDatabase: A database instance using ":memory:" with its schema initialized.
    """
    db = FlashcardDatabase(db_path=":memory:")
    db.initialize_schema()
    return db


# --- Test Cases ---


class TestReviewSessionManagerInit:
    def test_init_successful(
        self, mock_db: MagicMock, mock_scheduler: MagicMock
    ):
        """Test successful initialization of ReviewSessionManager."""
        manager = ReviewSessionManager(
            db_manager=mock_db,
            scheduler=mock_scheduler,
            user_uuid=uuid.uuid4(),
            deck_name="Test Deck",
        )
        assert manager.user_uuid is not None
        assert manager.deck_name == "Test Deck"
        assert isinstance(manager.review_queue, list)
        assert manager.current_session_card_uuids == set()


class TestStartSessionAndGetNextCard:
    def test_start_session_populates_queue(
        self,
        review_manager: ReviewSessionManager,
        mock_db: MagicMock,
        sample_card: Card,
    ):
        """Test that starting a session populates the review_queue with due cards."""
        due_cards = [
            sample_card,
            Card(**{**sample_card.model_dump(), "uuid": uuid.uuid4()}),
        ]
        mock_db.get_due_cards.return_value = due_cards

        review_manager.initialize_session()

        assert len(review_manager.review_queue) == len(due_cards)
        # Compare sets of UUIDs since Card objects are not hashable
        assert {c.uuid for c in review_manager.review_queue} == {
            c.uuid for c in due_cards
        }
        assert review_manager.current_session_card_uuids == {
            c.uuid for c in due_cards
        }

    def test_start_session_clears_existing_queue(
        self,
        review_manager: ReviewSessionManager,
        mock_db: MagicMock,
        sample_card: Card,
    ):
        """Test that starting a session clears any existing cards in the queue."""
        # Pre-populate the queue
        review_manager.review_queue = deque(
            [Card(**{**sample_card.model_dump(), "uuid": uuid.uuid4()})]
        )
        review_manager.current_session_card_uuids = {
            review_manager.review_queue[0].uuid
        }

        due_cards = [sample_card]
        mock_db.get_due_cards.return_value = due_cards

        review_manager.initialize_session()

        assert len(review_manager.review_queue) == 1
        assert review_manager.review_queue[0] == sample_card

    def test_get_next_card_returns_card_from_queue(
        self, review_manager: ReviewSessionManager, sample_card: Card
    ):
        """Test get_next_card returns the first card without removing it."""
        manager = review_manager
        manager.review_queue = deque(
            [
                sample_card,
                Card(**{**sample_card.model_dump(), "uuid": uuid.uuid4()}),
            ]
        )

        next_card = manager.get_next_card()
        assert next_card == sample_card
        assert len(manager.review_queue) == 2  # Should not be removed

    def test_get_next_card_empty_queue_returns_none(
        self, review_manager: ReviewSessionManager
    ):
        """Test get_next_card returns None if the queue is empty."""
        review_manager.review_queue = deque([])
        assert review_manager.get_next_card() is None


class TestSubmitReviewAndHelpers:
    def test_submit_review_successful_new_card(
        self,
        review_manager: ReviewSessionManager,
        mock_db: MagicMock,
        sample_card: Card,
    ):
        """Test submit_review for a new card (no history)."""
        review_manager.review_queue = deque([sample_card])
        review_manager.current_session_card_uuids = {sample_card.uuid}
        mock_db.get_reviews_for_card.return_value = []

        rating = Rating.Good
        review_ts = sample_card.added_at + timedelta(days=1)
        resp_ms = 5000
        scheduler_output = (
            review_manager.scheduler.compute_next_state.return_value
        )

        # Configure the mock to return an updated card
        expected_updated_card = sample_card.model_copy(deep=True)
        expected_updated_card.state = scheduler_output.state
        expected_updated_card.next_due_date = scheduler_output.next_due
        mock_db.add_review_and_update_card.return_value = expected_updated_card

        updated_card = review_manager.submit_review(
            sample_card.uuid, rating, reviewed_at=review_ts, resp_ms=resp_ms
        )

        review_manager.scheduler.compute_next_state.assert_called_once()
        mock_db.add_review_and_update_card.assert_called_once()

        _, kwargs = mock_db.add_review_and_update_card.call_args
        actual_review: Review = kwargs["review"]
        actual_state: CardState = kwargs["new_card_state"]

        assert actual_review.card_uuid == sample_card.uuid
        assert (
            actual_review.rating == rating.value
        )  # Unified 1-4 rating scale, no conversion needed
        assert actual_review.stab_after == scheduler_output.stab
        assert actual_state == scheduler_output.state

        assert updated_card is not None
        assert updated_card.state == scheduler_output.state
        assert updated_card.next_due_date == scheduler_output.next_due

    def test_submit_review_successful_with_history(
        self,
        review_manager: ReviewSessionManager,
        mock_db: MagicMock,
        sample_card: Card,
    ):
        """Test submit_review for a card with existing review history."""
        review_manager.review_queue = deque([sample_card])
        review_manager.current_session_card_uuids = {sample_card.uuid}

        prev_review_ts = sample_card.added_at + timedelta(days=5)
        prev_next_due = prev_review_ts.date() + timedelta(days=2)
        history = [
            Review(
                review_id=100,
                card_uuid=sample_card.uuid,
                ts=prev_review_ts,
                rating=Rating.Again.value + 1,
                resp_ms=6000,
                stab_before=1.0,
                stab_after=2.5,
                diff=6.0,
                next_due=prev_next_due,
                elapsed_days_at_review=5,
                scheduled_days_interval=2,
                review_type="learn",
            )
        ]
        mock_db.get_reviews_for_card.return_value = history

        # The card's current stability should reflect the last review
        sample_card.stability = history[-1].stab_after

        rating = Rating.Easy
        review_ts = datetime.combine(
            prev_next_due + timedelta(days=1),
            datetime.min.time(),
            tzinfo=timezone.utc,
        )
        resp_ms = 3000
        scheduler_output = (
            review_manager.scheduler.compute_next_state.return_value
        )

        # Configure the mock to return an updated card
        expected_updated_card = sample_card.model_copy(deep=True)
        expected_updated_card.state = scheduler_output.state
        expected_updated_card.next_due_date = scheduler_output.next_due
        mock_db.add_review_and_update_card.return_value = expected_updated_card

        updated_card = review_manager.submit_review(
            sample_card.uuid, rating, reviewed_at=review_ts, resp_ms=resp_ms
        )

        mock_db.add_review_and_update_card.assert_called_once()
        _, kwargs = mock_db.add_review_and_update_card.call_args
        actual_review: Review = kwargs["review"]
        actual_state: CardState = kwargs["new_card_state"]

        assert actual_review.stab_before == history[-1].stab_after
        assert actual_review.stab_after == scheduler_output.stab
        assert actual_state == scheduler_output.state

        assert updated_card is not None
        assert updated_card.state == scheduler_output.state
        assert updated_card.next_due_date == scheduler_output.next_due

    def test_submit_review_card_not_in_session(
        self, review_manager: ReviewSessionManager
    ):
        """Test submit_review raises ValueError if card is not in the current session queue."""
        unknown_uuid = uuid.uuid4()
        review_manager.review_queue = deque()

        with pytest.raises(
            ValueError, match="not found in the current review session"
        ):
            review_manager.submit_review(unknown_uuid, Rating.Again)

    def test_submit_review_scheduler_error(
        self, review_manager: ReviewSessionManager, sample_card: Card
    ):
        """Test submit_review when the scheduler raises an exception."""
        review_manager.review_queue = deque([sample_card])
        review_manager.current_session_card_uuids = {sample_card.uuid}

        review_manager.scheduler.compute_next_state.side_effect = ValueError(
            "Scheduler failed"
        )

        with pytest.raises(ValueError, match="Scheduler failed"):
            review_manager.submit_review(sample_card.uuid, Rating.Hard)

    def test_submit_review_db_add_error(
        self,
        review_manager: ReviewSessionManager,
        mock_db: MagicMock,
        sample_card: Card,
    ):
        """Test submit_review when the database raises an exception."""
        review_manager.review_queue = deque([sample_card])
        review_manager.current_session_card_uuids = {sample_card.uuid}

        mock_db.add_review_and_update_card.side_effect = (
            mock_db.CardOperationError("DB connection failed")
        )

        with pytest.raises(
            mock_db.CardOperationError, match="DB connection failed"
        ):
            review_manager.submit_review(sample_card.uuid, Rating.Good)

        mock_db.add_review_and_update_card.assert_called_once()

    def test_submit_review_removes_card_from_active_queue(
        self, review_manager: ReviewSessionManager, sample_card: Card
    ):
        """Test that a successfully reviewed card is removed from the active review_queue."""
        other_card = Card(**{**sample_card.model_dump(), "uuid": uuid.uuid4()})
        review_manager.review_queue = deque([sample_card, other_card])
        review_manager.current_session_card_uuids = {
            sample_card.uuid,
            other_card.uuid,
        }

        review_manager.submit_review(
            sample_card.uuid, rating=Rating.Hard, resp_ms=1000
        )

        assert sample_card not in review_manager.review_queue
        assert other_card in review_manager.review_queue
        assert sample_card.uuid in review_manager.current_session_card_uuids


class TestGetDueCardCount:
    @patch("flashcore.review_manager.date")
    def test_get_due_card_count_calls_db(
        self,
        mock_date: MagicMock,
        review_manager: ReviewSessionManager,
        mock_db: MagicMock,
    ):
        """Test get_due_card_count calls the database method and returns its result."""
        test_date = date(2025, 6, 20)
        mock_date.today.return_value = test_date

        expected_count = 42
        mock_db.get_due_card_count.return_value = expected_count

        count = review_manager.get_due_card_count()

        assert count == expected_count
        mock_db.get_due_card_count.assert_called_once_with(
            on_date=test_date, deck_name="Test Deck"
        )
        mock_db.get_due_cards.assert_not_called()  # Ensure the less efficient method is not called.


class TestReviewSessionManagerIntegration:
    def test_e2e_session_flow(
        self, in_memory_db: FlashcardDatabase, sample_card_data: dict
    ):
        """Test the end-to-end flow of a review session using an in-memory DB."""
        # 1. Setup: Initialize schema and add cards to the in-memory DB
        in_memory_db.initialize_schema(force_recreate_tables=True)
        today = date.today()
        now_utc = datetime.now(timezone.utc)

        # Card 1: Due today (based on sample_card_data's default next_due_date)
        card1_uuid = uuid.uuid4()
        card1_data = {
            **sample_card_data,
            "uuid": card1_uuid,
            "front": "Card 1 Due Today",
            "added_at": now_utc - timedelta(days=2),
        }
        card1 = Card(**card1_data)
        in_memory_db.upsert_cards_batch([card1])
        # Add a review to make the card due tomorrow
        review1 = Review(
            card_uuid=card1.uuid,
            ts=now_utc - timedelta(days=10),
            rating=3,
            stab_before=1.0,
            stab_after=2.5,
            diff=6.0,
            next_due=today - timedelta(days=1),
            elapsed_days_at_review=0,
            scheduled_days_interval=1,
            review_type="learn",
        )
        in_memory_db.add_review_and_update_card(review1, CardState.Review)

        # Card 2: Due in the future
        card2_uuid = uuid.uuid4()
        card2_data = {
            **sample_card_data,
            "uuid": card2_uuid,
            "front": "Card 2 Due Future",
            "added_at": now_utc - timedelta(days=10),
        }
        card2 = Card(**card2_data)
        in_memory_db.upsert_cards_batch([card2])

        # Add a review to make card2 due in the future
        review_for_card2 = Review(
            card_uuid=card2_uuid,
            ts=now_utc - timedelta(days=5),
            rating=2,
            stab_after=5.0,
            diff=5.0,  # Example FSRS values
            next_due=today + timedelta(days=3),  # Explicitly due in 3 days
            elapsed_days_at_review=0,
            scheduled_days_interval=8,
            review_type="review",
        )
        in_memory_db.add_review_and_update_card(
            review_for_card2, CardState.Review
        )  # This will also update card2's next_due_date in DB

        # 2. Initialize ReviewSessionManager with the real DB and a real scheduler
        scheduler = FSRS_Scheduler()
        manager = ReviewSessionManager(
            db_manager=in_memory_db,
            scheduler=scheduler,
            user_uuid=uuid.uuid4(),
            deck_name="Test Deck",
        )

        # 3. Start session & verify due counts
        # get_due_cards_count uses `next_due_date <= on_date`
        assert (
            manager.get_due_card_count() == 1
        ), f"Expected 1 due card, found {manager.get_due_card_count()}. Card1 due: {card1.next_due_date}, Card2 due: {in_memory_db.get_card_by_uuid(card2_uuid).next_due_date}"

        manager.initialize_session(limit=10)
        assert len(manager.review_queue) == 1
        assert manager.review_queue[0].uuid == card1_uuid

        # 4. Get next card
        next_card_to_review = manager.get_next_card()
        assert next_card_to_review is not None
        assert next_card_to_review.uuid == card1_uuid

        # 5. Submit review for the card
        rating = Rating.Easy  # Corresponds to value 3
        review_ts = datetime.now(timezone.utc)  # Use current time for review
        resp_ms = 4000
        updated_card = manager.submit_review(
            card_uuid=card1_uuid,
            rating=rating,
            reviewed_at=review_ts,
            resp_ms=resp_ms,
        )

        # 6. Verify the results
        # Assert properties of the returned (and updated) Card object
        assert updated_card is not None
        assert updated_card.uuid == card1_uuid
        assert updated_card.next_due_date > today
        assert updated_card.state == CardState.Review
        assert updated_card.last_review_id is not None

        # Assert properties of the Review object that was created in the DB
        latest_review = in_memory_db.get_latest_review_for_card(card1_uuid)
        assert latest_review is not None
        assert latest_review.review_id == updated_card.last_review_id
        assert (
            latest_review.rating == rating.value
        )  # Unified 1-4 rating scale, no conversion needed
        assert latest_review.review_type == "review"

        # 6. Verify DB state
        card1_reviews = in_memory_db.get_reviews_for_card(card1_uuid)
        assert len(card1_reviews) == 2
        assert (
            card1_reviews[0].review_id == updated_card.last_review_id
        )  # DB generates review_id

        updated_card1_from_db = in_memory_db.get_card_by_uuid(card1_uuid)
        assert updated_card1_from_db is not None
        assert (
            updated_card1_from_db.last_review_id == updated_card.last_review_id
        )
        assert (
            updated_card1_from_db.next_due_date == updated_card.next_due_date
        )

        # 7. Verify manager state after review
        assert card1_uuid not in [
            c.uuid for c in manager.review_queue
        ]  # Card removed from active queue
        assert manager.get_next_card() is None  # Queue should be empty now

        # 8. Verify due card count again (card1 should no longer be due today)
        assert manager.get_due_card_count() == 0


# More test classes and methods will follow for other functionalities...


class TestReviewManagerCoverageGaps:
    """Tests targeting specific uncovered lines in review_manager.py."""

    def test_initialize_session_with_tags(
        self, mock_db, mock_scheduler, sample_card_data
    ):
        """Test initialize_session logs tags when provided."""
        card = Card(**sample_card_data)
        mock_db.get_due_cards.return_value = [card]
        manager = ReviewSessionManager(
            db_manager=mock_db,
            scheduler=mock_scheduler,
            user_uuid=uuid.uuid4(),
            deck_name="Test Deck",
        )
        manager.initialize_session(tags=["math", "science"])
        mock_db.get_due_cards.assert_called_once()

    def test_session_analytics_start_failure(self, mock_db, mock_scheduler):
        """Test that session analytics failure in initialize_session doesn't crash."""
        mock_db.get_due_cards.return_value = []
        mock_db.create_session.side_effect = RuntimeError("DB error")
        manager = ReviewSessionManager(
            db_manager=mock_db,
            scheduler=mock_scheduler,
            user_uuid=uuid.uuid4(),
            deck_name="Test Deck",
        )
        manager.initialize_session()
        assert manager._session_started is False

    def test_record_session_analytics_failure(
        self, mock_db, mock_scheduler, sample_card_data
    ):
        """Test that session analytics recording failure doesn't crash submit_review."""
        card = Card(**sample_card_data)
        mock_db.get_due_cards.return_value = [card]
        mock_db.get_card_by_uuid.return_value = card
        mock_db.get_reviews_for_card.return_value = []
        mock_db.add_review_and_update_card.return_value = card

        manager = ReviewSessionManager(
            db_manager=mock_db,
            scheduler=mock_scheduler,
            user_uuid=uuid.uuid4(),
            deck_name="Test Deck",
        )
        manager.initialize_session()
        manager._session_started = True
        mock_db.update_session.side_effect = RuntimeError("Analytics failure")

        result = manager.submit_review(
            card_uuid=card.uuid,
            rating=3,
            resp_ms=1000,
            eval_ms=500,
        )
        assert result is not None

    def test_get_session_stats_with_analytics(
        self, mock_db, mock_scheduler, sample_card_data
    ):
        """Test get_session_stats includes analytics when session started."""
        card = Card(**sample_card_data)
        mock_db.get_due_cards.return_value = [card]
        manager = ReviewSessionManager(
            db_manager=mock_db,
            scheduler=mock_scheduler,
            user_uuid=uuid.uuid4(),
            deck_name="Test Deck",
        )
        manager.initialize_session()
        manager._session_started = True

        mock_session_manager = MagicMock()
        mock_session_manager.get_current_session_stats.return_value = {
            "duration_seconds": 120,
            "average_response_time_ms": 1500,
        }
        manager.session_manager = mock_session_manager

        stats = manager.get_session_stats()
        assert "total_cards" in stats
        assert "duration_seconds" in stats

    def test_get_session_stats_analytics_failure(
        self, mock_db, mock_scheduler, sample_card_data
    ):
        """Test get_session_stats handles analytics failure gracefully."""
        card = Card(**sample_card_data)
        mock_db.get_due_cards.return_value = [card]
        manager = ReviewSessionManager(
            db_manager=mock_db,
            scheduler=mock_scheduler,
            user_uuid=uuid.uuid4(),
            deck_name="Test Deck",
        )
        manager.initialize_session()
        manager._session_started = True

        mock_session_manager = MagicMock()
        mock_session_manager.get_current_session_stats.side_effect = (
            RuntimeError("fail")
        )
        manager.session_manager = mock_session_manager

        stats = manager.get_session_stats()
        assert "total_cards" in stats

    def test_end_session_with_insights_no_session(
        self, mock_db, mock_scheduler
    ):
        """Test end_session_with_insights when no session is active."""
        manager = ReviewSessionManager(
            db_manager=mock_db,
            scheduler=mock_scheduler,
            user_uuid=uuid.uuid4(),
            deck_name="Test Deck",
        )
        result = manager.end_session_with_insights()
        assert "error" in result

    def test_end_session_with_insights_success(self, mock_db, mock_scheduler):
        """Test end_session_with_insights returns full insight data."""
        from flashcore.session_manager import SessionInsights

        manager = ReviewSessionManager(
            db_manager=mock_db,
            scheduler=mock_scheduler,
            user_uuid=uuid.uuid4(),
            deck_name="Test Deck",
        )
        manager._session_started = True

        mock_session = MagicMock()
        mock_session.session_uuid = uuid.uuid4()
        mock_session.total_duration_ms = 600000
        mock_session.cards_reviewed = 10
        mock_session.decks_accessed = {"Math"}
        mock_session.deck_switches = 1
        mock_session.interruptions = 0

        mock_insights = SessionInsights(
            cards_per_minute=1.0,
            average_response_time_ms=1000,
            median_response_time_ms=900,
            accuracy_percentage=80.0,
            total_review_time_ms=10000,
            deck_switch_efficiency=90.0,
            interruption_impact=0.0,
            focus_score=100.0,
            improvement_rate=0.0,
            learning_velocity=0.8,
            retention_score=80.0,
            fatigue_detected=False,
            optimal_session_length=30,
            peak_performance_time=None,
            recommendations=["Keep it up!"],
            achievements=["Perfect focus!"],
            alerts=[],
            vs_last_session={},
            vs_average={},
            trend_direction="stable",
        )

        mock_session_manager = MagicMock()
        mock_session_manager.end_session.return_value = mock_session
        mock_session_manager.generate_session_insights.return_value = (
            mock_insights
        )
        manager.session_manager = mock_session_manager

        result = manager.end_session_with_insights()
        assert "session" in result
        assert "insights" in result
        assert result["insights"]["performance"]["cards_per_minute"] == 1.0

    def test_end_session_with_insights_failure(self, mock_db, mock_scheduler):
        """Test end_session_with_insights handles exception gracefully."""
        manager = ReviewSessionManager(
            db_manager=mock_db,
            scheduler=mock_scheduler,
            user_uuid=uuid.uuid4(),
            deck_name="Test Deck",
        )
        manager._session_started = True

        mock_session_manager = MagicMock()
        mock_session_manager.end_session.side_effect = RuntimeError("DB crash")
        manager.session_manager = mock_session_manager

        result = manager.end_session_with_insights()
        assert "error" in result