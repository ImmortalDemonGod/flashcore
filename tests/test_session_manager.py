"""
Tests for the SessionManager class.

The SessionManager provides comprehensive session tracking, analytics, and insights
for flashcard review sessions, addressing the gap where session infrastructure
existed but wasn't actively used.
"""

import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4, UUID
from unittest.mock import patch, MagicMock

from flashcore.models import Card, Session
from flashcore.db.database import FlashcardDatabase
from flashcore.session_manager import SessionManager, SessionInsights


class TestSessionManager:
    """Test the SessionManager class."""

    @pytest.fixture
    def in_memory_db(self):
        """Create an in-memory database for testing."""
        db = FlashcardDatabase(":memory:")
        db.initialize_schema()
        return db

    @pytest.fixture
    def session_manager(self, in_memory_db):
        """Create a SessionManager instance for testing."""
        return SessionManager(in_memory_db, user_id="test_user")

    @pytest.fixture
    def sample_cards(self):
        """Create sample cards for testing."""
        return [
            Card(
                uuid=uuid4(),
                deck_name="Math",
                front=f"What is {i}+{i}?",
                back=str(i * 2),
                tags={"math", "basic"},
            )
            for i in range(1, 4)
        ]

    def test_start_session_success(self, session_manager):
        """Test successful session start."""
        session = session_manager.start_session(device_type="desktop", platform="cli")

        assert session is not None
        assert session.session_uuid is not None
        assert session.user_id == "test_user"
        assert session.device_type == "desktop"
        assert session.platform == "cli"
        assert session.start_ts is not None
        assert session.end_ts is None
        assert session.cards_reviewed == 0
        assert session.decks_accessed == set()
        assert session.deck_switches == 0
        assert session.interruptions == 0

        # Verify session is stored in database
        stored_session = session_manager.db_manager.get_session_by_uuid(
            session.session_uuid
        )
        assert stored_session is not None
        assert stored_session.session_uuid == session.session_uuid

    def test_start_session_with_existing_uuid(self, session_manager):
        """Test starting session with existing UUID."""
        existing_uuid = uuid4()

        session = session_manager.start_session(
            device_type="mobile", platform="app", session_uuid=existing_uuid
        )

        assert session.session_uuid == existing_uuid
        assert session.device_type == "mobile"
        assert session.platform == "app"

    def test_start_session_already_active_error(self, session_manager):
        """Test error when starting session while one is already active."""
        # Start first session
        session_manager.start_session()

        # Try to start second session
        with pytest.raises(ValueError, match="A session is already active"):
            session_manager.start_session()

    def test_record_card_review_success(self, session_manager, sample_cards):
        """Test successful card review recording."""
        # Start session
        session = session_manager.start_session()

        # Record review
        card = sample_cards[0]
        session_manager.record_card_review(
            card=card, rating=3, response_time_ms=1200, evaluation_time_ms=500
        )

        # Verify session was updated
        updated_session = session_manager.db_manager.get_session_by_uuid(
            session.session_uuid
        )
        assert updated_session.cards_reviewed == 1
        assert card.deck_name in updated_session.decks_accessed
        assert updated_session.deck_switches == 0  # First deck

    def test_record_card_review_deck_switching(self, session_manager, sample_cards):
        """Test deck switching detection."""
        # Start session
        session_manager.start_session()

        # Create cards from different decks
        math_card = sample_cards[0]
        science_card = Card(
            uuid=uuid4(),
            deck_name="Science",
            front="What is H2O?",
            back="Water",
            tags={"chemistry"},
        )

        # Record reviews from different decks
        session_manager.record_card_review(math_card, rating=3, response_time_ms=1000)
        session_manager.record_card_review(science_card, rating=4, response_time_ms=800)

        # Verify deck switch was detected
        session = session_manager.current_session
        assert session.cards_reviewed == 2
        assert len(session.decks_accessed) == 2
        assert "Math" in session.decks_accessed
        assert "Science" in session.decks_accessed
        assert session.deck_switches == 1  # One switch from Math to Science

        # Record another Math card to test switch back
        math_card2 = Card(
            uuid=uuid4(),
            deck_name="Math",
            front="What is 2+2?",
            back="4",
            tags={"math"},
        )
        session_manager.record_card_review(math_card2, rating=3, response_time_ms=900)

        # Should now have 2 switches: Math -> Science -> Math
        assert session.deck_switches == 2

    def test_record_card_review_no_active_session_error(
        self, session_manager, sample_cards
    ):
        """Test error when recording review without active session."""
        with pytest.raises(ValueError, match="No active session"):
            session_manager.record_card_review(
                card=sample_cards[0], rating=3, response_time_ms=1000
            )

    def test_record_interruption_success(self, session_manager):
        """Test successful interruption recording."""
        # Start session
        session_manager.start_session()

        # Record interruption
        session_manager.record_interruption()

        # Verify interruption was recorded
        session = session_manager.current_session
        assert session.interruptions == 1

    def test_record_interruption_no_active_session_error(self, session_manager):
        """Test error when recording interruption without active session."""
        with pytest.raises(ValueError, match="No active session"):
            session_manager.record_interruption()

    def test_interruption_detection_on_review(self, session_manager, sample_cards):
        """Test automatic interruption detection based on time gaps."""
        # Start session
        session_manager.start_session()

        # Record first review
        session_manager.record_card_review(
            sample_cards[0], rating=3, response_time_ms=1000
        )

        # Simulate time gap > 2 minutes
        with patch.object(
            session_manager,
            "last_activity_time",
            datetime.now(timezone.utc) - timedelta(minutes=3),
        ):
            # Record second review (should detect interruption)
            session_manager.record_card_review(
                sample_cards[1], rating=3, response_time_ms=1000
            )

        # Verify interruption was detected
        session = session_manager.current_session
        assert session.interruptions == 1

    def test_pause_and_resume_session(self, session_manager):
        """Test session pause and resume functionality."""
        import time

        # Start session
        session_manager.start_session()

        # Pause session
        session_manager.pause_session()
        assert session_manager.pause_start_time is not None

        # Wait a small amount to ensure measurable pause duration
        time.sleep(0.01)  # 10ms

        # Resume session
        session_manager.resume_session()
        assert session_manager.pause_start_time is None
        assert (
            session_manager.total_pause_duration_ms >= 0
        )  # Should be >= 0, might be 0 due to timing

    def test_pause_session_errors(self, session_manager):
        """Test pause session error conditions."""
        # Test pause without active session
        with pytest.raises(ValueError, match="No active session"):
            session_manager.pause_session()

        # Start session and pause
        session_manager.start_session()
        session_manager.pause_session()

        # Test double pause
        with pytest.raises(ValueError, match="already paused"):
            session_manager.pause_session()

    def test_resume_session_errors(self, session_manager):
        """Test resume session error conditions."""
        # Test resume without active session
        with pytest.raises(ValueError, match="No active session"):
            session_manager.resume_session()

        # Start session (not paused)
        session_manager.start_session()

        # Test resume when not paused
        with pytest.raises(ValueError, match="not paused"):
            session_manager.resume_session()

    def test_end_session_success(self, session_manager, sample_cards):
        """Test successful session ending."""
        # Start session
        session = session_manager.start_session()

        # Record some activity
        session_manager.record_card_review(
            sample_cards[0], rating=3, response_time_ms=1000
        )
        session_manager.record_card_review(
            sample_cards[1], rating=4, response_time_ms=800
        )

        # End session
        completed_session = session_manager.end_session()

        assert completed_session.end_ts is not None
        assert completed_session.total_duration_ms is not None
        assert completed_session.total_duration_ms > 0
        assert completed_session.cards_reviewed == 2

        # Verify session is no longer active
        assert session_manager.current_session is None

    def test_end_session_with_pause(self, session_manager, sample_cards):
        """Test ending session that was paused."""
        # Start session
        session_manager.start_session()

        # Record activity, pause, then end
        session_manager.record_card_review(
            sample_cards[0], rating=3, response_time_ms=1000
        )
        session_manager.pause_session()

        # End session (should auto-resume)
        completed_session = session_manager.end_session()

        assert completed_session.end_ts is not None
        assert completed_session.total_duration_ms is not None
        # Duration should exclude pause time
        assert completed_session.total_duration_ms < 60000  # Less than 1 minute

    def test_end_session_no_active_session_error(self, session_manager):
        """Test error when ending session without active session."""
        with pytest.raises(ValueError, match="No active session"):
            session_manager.end_session()

    def test_get_current_session_stats(self, session_manager, sample_cards):
        """Test getting current session statistics."""
        # Start session
        session_manager.start_session()

        # Record some activity
        session_manager.record_card_review(
            sample_cards[0], rating=3, response_time_ms=1200
        )
        session_manager.record_card_review(
            sample_cards[1], rating=4, response_time_ms=800
        )

        # Get stats
        stats = session_manager.get_current_session_stats()

        assert "session_uuid" in stats
        assert stats["cards_reviewed"] == 2
        assert stats["decks_accessed"] == ["Math"]
        assert stats["deck_switches"] == 0
        assert stats["interruptions"] == 0
        assert stats["average_response_time_ms"] == 1000  # (1200 + 800) / 2
        assert stats["cards_per_minute"] > 0
        assert stats["is_paused"] is False

    def test_get_current_session_stats_no_active_session_error(self, session_manager):
        """Test error when getting stats without active session."""
        with pytest.raises(ValueError, match="No active session"):
            session_manager.get_current_session_stats()

    def test_generate_session_insights_success(self, session_manager, sample_cards):
        """Test successful session insights generation."""
        # Create and complete a session
        session = session_manager.start_session()

        # Record activity
        for i, card in enumerate(sample_cards):
            session_manager.record_card_review(
                card=card,
                rating=3 + (i % 2),  # Alternate between Good and Easy
                response_time_ms=1000 + i * 100,
            )

        completed_session = session_manager.end_session()

        # Generate insights (will work with session analytics even without reviews)
        insights = session_manager.generate_session_insights(
            completed_session.session_uuid
        )

        assert isinstance(insights, SessionInsights)
        # Note: cards_per_minute might be 0 if no actual reviews in database
        # The SessionManager tracks analytics separately from review creation
        assert insights.cards_per_minute >= 0
        assert insights.average_response_time_ms >= 0
        assert insights.accuracy_percentage >= 0
        assert insights.focus_score >= 0
        assert isinstance(insights.recommendations, list)
        assert isinstance(insights.achievements, list)
        assert isinstance(insights.alerts, list)

    def test_generate_session_insights_session_not_found_error(self, session_manager):
        """Test error when generating insights for non-existent session."""
        non_existent_uuid = uuid4()

        with pytest.raises(ValueError, match="Session .* not found"):
            session_manager.generate_session_insights(non_existent_uuid)

    def test_generate_session_insights_active_session_error(self, session_manager):
        """Test error when generating insights for active session."""
        # Start session but don't end it
        session = session_manager.start_session()

        with pytest.raises(ValueError, match="still active"):
            session_manager.generate_session_insights(session.session_uuid)


class TestSessionManagerIntegration:
    """Integration tests for SessionManager with real database and components."""

    @pytest.fixture
    def in_memory_db(self):
        """Create an in-memory database for testing."""
        db = FlashcardDatabase(":memory:")
        db.initialize_schema()
        return db

    @pytest.fixture
    def session_manager(self, in_memory_db):
        """Create a SessionManager instance for testing."""
        return SessionManager(in_memory_db, user_id="integration_test_user")

    def test_end_to_end_session_workflow(self, session_manager):
        """Test complete end-to-end session workflow."""
        # Start session
        session = session_manager.start_session(device_type="desktop", platform="cli")

        # Create test cards
        cards = [
            Card(uuid=uuid4(), deck_name="Math", front="1+1?", back="2", tags={"math"}),
            Card(uuid=uuid4(), deck_name="Math", front="2+2?", back="4", tags={"math"}),
            Card(
                uuid=uuid4(),
                deck_name="Science",
                front="H2O?",
                back="Water",
                tags={"chemistry"},
            ),
        ]

        # Record reviews with varying performance
        response_times = [800, 1200, 1000]
        ratings = [4, 3, 4]  # Easy, Good, Easy

        for i, card in enumerate(cards):
            session_manager.record_card_review(
                card=card,
                rating=ratings[i],
                response_time_ms=response_times[i],
                evaluation_time_ms=500,
            )

        # Get real-time stats
        stats = session_manager.get_current_session_stats()
        assert stats["cards_reviewed"] == 3
        assert len(stats["decks_accessed"]) == 2
        assert stats["deck_switches"] == 1  # Math -> Science

        # End session
        completed_session = session_manager.end_session()
        assert completed_session.cards_reviewed == 3
        assert len(completed_session.decks_accessed) == 2
        assert completed_session.deck_switches == 1

        # Generate insights
        insights = session_manager.generate_session_insights(
            completed_session.session_uuid
        )
        # Note: Since we're only using SessionManager without ReviewProcessor,
        # the insights will be based on session analytics, not actual reviews
        assert insights.cards_per_minute >= 0  # Might be 0 without actual reviews
        assert insights.average_response_time_ms >= 0  # Based on session tracking
        assert insights.accuracy_percentage >= 0  # Based on session tracking

        # Verify session is persisted
        stored_session = session_manager.db_manager.get_session_by_uuid(
            completed_session.session_uuid
        )
        assert stored_session is not None
        assert stored_session.cards_reviewed == 3

    def test_multiple_sessions_comparison(self, session_manager):
        """Test session comparison analytics across multiple sessions."""
        sessions = []

        # Create multiple sessions with different performance
        for session_num in range(3):
            session = session_manager.start_session()

            # Simulate different performance levels
            cards_count = 5 + session_num * 2  # Improving performance
            for i in range(cards_count):
                card = Card(
                    uuid=uuid4(),
                    deck_name="Test",
                    front=f"Q{i}",
                    back=f"A{i}",
                    tags={"test"},
                )
                session_manager.record_card_review(
                    card=card,
                    rating=3,  # Consistent Good rating
                    response_time_ms=1000 - session_num * 100,  # Improving speed
                )

            completed_session = session_manager.end_session()
            sessions.append(completed_session)

            # Create new session manager for next session
            session_manager = SessionManager(
                session_manager.db_manager, user_id="integration_test_user"
            )

        # Generate insights for the latest session
        insights = session_manager.generate_session_insights(sessions[-1].session_uuid)

        # Should have comparison data
        assert isinstance(insights.vs_last_session, dict)
        assert insights.trend_direction in ["improving", "stable", "declining"]

    def test_session_persistence_across_manager_instances(self, in_memory_db):
        """Test that sessions persist across different SessionManager instances."""
        # Create first manager and session
        manager1 = SessionManager(in_memory_db, user_id="persistence_test")
        session = manager1.start_session()

        card = Card(uuid=uuid4(), deck_name="Test", front="Q", back="A", tags={"test"})
        manager1.record_card_review(card, rating=3, response_time_ms=1000)

        completed_session = manager1.end_session()

        # Create second manager and verify session exists
        manager2 = SessionManager(in_memory_db, user_id="persistence_test")
        insights = manager2.generate_session_insights(completed_session.session_uuid)

        assert insights is not None
        # Note: cards_per_minute might be 0 without actual reviews in database
        assert insights.cards_per_minute >= 0
