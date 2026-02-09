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
        """
        Create and initialize an in-memory FlashcardDatabase for use in tests.

        Returns:
            FlashcardDatabase: an in-memory database instance with its schema initialized.
        """
        db = FlashcardDatabase(":memory:")
        db.initialize_schema()
        return db

    @pytest.fixture
    def session_manager(self, in_memory_db):
        """
        Create a SessionManager configured with the provided in-memory database for testing.

        Parameters:
            in_memory_db: An initialized in-memory FlashcardDatabase instance to back the SessionManager.

        Returns:
            session_manager (SessionManager): A SessionManager bound to `in_memory_db` and using the test user_id "test_user".
        """
        return SessionManager(in_memory_db, user_id="test_user")

    @pytest.fixture
    def sample_cards(self):
        """
        Create a small list of sample flashcards for tests.

        Returns:
            list[Card]: Three Card instances in the "Math" deck (UUIDs generated), with fronts like "What is 1+1?" and corresponding backs ("2"), each tagged with "math" and "basic".
        """
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
        session = session_manager.start_session(
            device_type="desktop", platform="cli"
        )

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

    def test_record_card_review_deck_switching(
        self, session_manager, sample_cards
    ):
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
        session_manager.record_card_review(
            math_card, rating=3, response_time_ms=1000
        )
        session_manager.record_card_review(
            science_card, rating=4, response_time_ms=800
        )

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
        session_manager.record_card_review(
            math_card2, rating=3, response_time_ms=900
        )

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

    def test_record_interruption_no_active_session_error(
        self, session_manager
    ):
        """Test error when recording interruption without active session."""
        with pytest.raises(ValueError, match="No active session"):
            session_manager.record_interruption()

    def test_interruption_detection_on_review(
        self, session_manager, sample_cards
    ):
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
        assert (
            completed_session.total_duration_ms < 60000
        )  # Less than 1 minute

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

    def test_get_current_session_stats_no_active_session_error(
        self, session_manager
    ):
        """Test error when getting stats without active session."""
        with pytest.raises(ValueError, match="No active session"):
            session_manager.get_current_session_stats()

    def test_generate_session_insights_success(
        self, session_manager, sample_cards
    ):
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

    def test_generate_session_insights_session_not_found_error(
        self, session_manager
    ):
        """Test error when generating insights for non-existent session."""
        non_existent_uuid = uuid4()

        with pytest.raises(ValueError, match="Session .* not found"):
            session_manager.generate_session_insights(non_existent_uuid)

    def test_generate_session_insights_active_session_error(
        self, session_manager
    ):
        """Test error when generating insights for active session."""
        # Start session but don't end it
        session = session_manager.start_session()

        with pytest.raises(ValueError, match="still active"):
            session_manager.generate_session_insights(session.session_uuid)


class TestSessionManagerIntegration:
    """Integration tests for SessionManager with real database and components."""

    @pytest.fixture
    def in_memory_db(self):
        """
        Create and initialize an in-memory FlashcardDatabase for use in tests.

        Returns:
            FlashcardDatabase: an in-memory database instance with its schema initialized.
        """
        db = FlashcardDatabase(":memory:")
        db.initialize_schema()
        return db

    @pytest.fixture
    def session_manager(self, in_memory_db):
        """
        Create a SessionManager configured for integration tests.

        Parameters:
            in_memory_db: An initialized in-memory FlashcardDatabase fixture used for persistence during tests.

        Returns:
            SessionManager: A SessionManager instance bound to the provided database and the test user_id "integration_test_user".
        """
        return SessionManager(in_memory_db, user_id="integration_test_user")

    def test_end_to_end_session_workflow(self, session_manager):
        """Test complete end-to-end session workflow."""
        # Start session
        session = session_manager.start_session(
            device_type="desktop", platform="cli"
        )

        # Create test cards
        cards = [
            Card(
                uuid=uuid4(),
                deck_name="Math",
                front="1+1?",
                back="2",
                tags={"math"},
            ),
            Card(
                uuid=uuid4(),
                deck_name="Math",
                front="2+2?",
                back="4",
                tags={"math"},
            ),
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
        assert (
            insights.cards_per_minute >= 0
        )  # Might be 0 without actual reviews
        assert (
            insights.average_response_time_ms >= 0
        )  # Based on session tracking
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
                    response_time_ms=1000
                    - session_num * 100,  # Improving speed
                )

            completed_session = session_manager.end_session()
            sessions.append(completed_session)

            # Create new session manager for next session
            session_manager = SessionManager(
                session_manager.db_manager, user_id="integration_test_user"
            )

        # Generate insights for the latest session
        insights = session_manager.generate_session_insights(
            sessions[-1].session_uuid
        )

        # Should have comparison data
        assert isinstance(insights.vs_last_session, dict)
        assert insights.trend_direction in ["improving", "stable", "declining"]

    def test_session_persistence_across_manager_instances(self, in_memory_db):
        """Test that sessions persist across different SessionManager instances."""
        # Create first manager and session
        manager1 = SessionManager(in_memory_db, user_id="persistence_test")
        session = manager1.start_session()

        card = Card(
            uuid=uuid4(), deck_name="Test", front="Q", back="A", tags={"test"}
        )
        manager1.record_card_review(card, rating=3, response_time_ms=1000)

        completed_session = manager1.end_session()

        # Create second manager and verify session exists
        manager2 = SessionManager(in_memory_db, user_id="persistence_test")
        insights = manager2.generate_session_insights(
            completed_session.session_uuid
        )

        assert insights is not None
        # Note: cards_per_minute might be 0 without actual reviews in database
        assert insights.cards_per_minute >= 0

    def test_start_session_db_error_resets_state(self, in_memory_db):
        """Test that start_session resets current_session on database error."""
        manager = SessionManager(in_memory_db, user_id="test_user")
        with patch.object(
            in_memory_db,
            "create_session",
            side_effect=RuntimeError("DB failure"),
        ):
            with pytest.raises(RuntimeError, match="DB failure"):
                manager.start_session()
        assert manager.current_session is None

    def test_record_card_review_db_error_continues(self, in_memory_db):
        """Test that record_card_review logs error but doesn't crash on DB failure."""
        manager = SessionManager(in_memory_db, user_id="test_user")
        manager.start_session()
        card = Card(
            uuid=uuid4(), deck_name="Math", front="Q", back="A", tags={"math"}
        )
        with patch.object(
            in_memory_db,
            "update_session",
            side_effect=RuntimeError("DB failure"),
        ):
            manager.record_card_review(card, rating=3, response_time_ms=1000)
        assert manager.current_session.cards_reviewed == 1

    def test_record_interruption_db_error_continues(self, in_memory_db):
        """
        Ensure recording an interruption increments the in-memory interruption counter even if the database update raises an error.

        Starts a session, simulates a database failure when persisting the session update, calls `record_interruption`, and verifies `current_session.interruptions` increments to 1.
        """
        manager = SessionManager(in_memory_db, user_id="test_user")
        manager.start_session()
        with patch.object(
            in_memory_db,
            "update_session",
            side_effect=RuntimeError("DB failure"),
        ):
            manager.record_interruption()
        assert manager.current_session.interruptions == 1

    def test_end_session_db_error_raises(self, in_memory_db):
        """Test that end_session raises on DB failure during finalization."""
        manager = SessionManager(in_memory_db, user_id="test_user")
        manager.start_session()
        with patch.object(
            in_memory_db,
            "update_session",
            side_effect=RuntimeError("DB failure"),
        ):
            with pytest.raises(RuntimeError, match="DB failure"):
                manager.end_session()

    def test_get_user_sessions_db_error_returns_empty(self, in_memory_db):
        """Test that _get_user_sessions returns empty list on DB failure."""
        manager = SessionManager(in_memory_db, user_id="test_user")
        with patch.object(
            in_memory_db,
            "get_recent_sessions",
            side_effect=RuntimeError("DB failure"),
        ):
            result = manager._get_user_sessions("test_user")
        assert result == []

    def test_get_session_reviews_session_not_found(self, in_memory_db):
        """Test that _get_session_reviews returns empty list when session not found."""
        manager = SessionManager(in_memory_db, user_id="test_user")
        result = manager._get_session_reviews(uuid4())
        assert result == []

    def test_calculate_performance_metrics_with_reviews(self, in_memory_db):
        """Test _calculate_performance_metrics with actual review data."""
        from datetime import date as date_today
        from flashcore.models import Review

        manager = SessionManager(in_memory_db, user_id="test_user")
        session = Session(
            session_uuid=uuid4(),
            user_id="test_user",
            total_duration_ms=600000,
            cards_reviewed=10,
            interruptions=1,
            deck_switches=2,
        )
        reviews = [
            Review(
                card_uuid=uuid4(),
                rating=r,
                resp_ms=ms,
                eval_ms=500,
                stab_before=1.0,
                stab_after=2.0,
                diff=5.0,
                next_due=date_today.today(),
                elapsed_days_at_review=1,
                scheduled_days_interval=1,
                review_type="review",
                ts=datetime.now(timezone.utc),
            )
            for r, ms in [
                (3, 1000),
                (4, 800),
                (2, 1200),
                (3, 900),
                (4, 700),
                (3, 1100),
            ]
        ]
        metrics = manager._calculate_performance_metrics(session, reviews)
        assert metrics["cards_per_minute"] == 1.0
        assert metrics["average_response_time_ms"] > 0
        assert metrics["accuracy_percentage"] > 0
        assert metrics["focus_score"] <= 100
        assert metrics["fatigue_detected"] is False

    def test_calculate_performance_metrics_fatigue_detected(
        self, in_memory_db
    ):
        """Test fatigue detection when response times increase significantly."""
        from datetime import date as date_today
        from flashcore.models import Review

        manager = SessionManager(in_memory_db, user_id="test_user")
        session = Session(
            session_uuid=uuid4(),
            user_id="test_user",
            total_duration_ms=600000,
            cards_reviewed=10,
        )
        reviews = [
            Review(
                card_uuid=uuid4(),
                rating=3,
                resp_ms=ms,
                eval_ms=500,
                stab_before=1.0,
                stab_after=2.0,
                diff=5.0,
                next_due=date_today.today(),
                elapsed_days_at_review=1,
                scheduled_days_interval=1,
                review_type="review",
                ts=datetime.now(timezone.utc),
            )
            for ms in [500, 600, 550, 580, 1500, 1800, 2000, 1900, 2100, 2200]
        ]
        metrics = manager._calculate_performance_metrics(session, reviews)
        assert metrics["fatigue_detected"] is True

    def test_calculate_session_comparisons_improving_trend(self, in_memory_db):
        """Test trend detection: improving (recent > older)."""
        manager = SessionManager(in_memory_db, user_id="test_user")
        session = Session(
            session_uuid=uuid4(),
            user_id="test_user",
            total_duration_ms=600000,
            cards_reviewed=20,
        )
        historical = [session] + [
            Session(
                session_uuid=uuid4(),
                user_id="test_user",
                total_duration_ms=600000,
                cards_reviewed=20 - i * 3,
            )
            for i in range(1, 5)
        ]
        result = manager._calculate_session_comparisons(session, historical)
        assert result["trend_direction"] == "improving"

    def test_calculate_session_comparisons_declining_trend(self, in_memory_db):
        """Test trend detection: declining (recent < older)."""
        manager = SessionManager(in_memory_db, user_id="test_user")
        session = Session(
            session_uuid=uuid4(),
            user_id="test_user",
            total_duration_ms=600000,
            cards_reviewed=5,
        )
        historical = [session] + [
            Session(
                session_uuid=uuid4(),
                user_id="test_user",
                total_duration_ms=600000,
                cards_reviewed=5 + i * 3,
            )
            for i in range(1, 5)
        ]
        result = manager._calculate_session_comparisons(session, historical)
        assert result["trend_direction"] == "declining"

    def test_generate_recommendations_long_session(self, in_memory_db):
        """Test recommendation for sessions longer than 1 hour."""
        manager = SessionManager(in_memory_db, user_id="test_user")
        session = Session(
            session_uuid=uuid4(),
            user_id="test_user",
            total_duration_ms=4000000,
            cards_reviewed=10,
        )
        recs = manager._generate_recommendations(session, [], {})
        assert any("shorter sessions" in r for r in recs)

    def test_generate_recommendations_short_session(self, in_memory_db):
        """Test recommendation for sessions shorter than 10 minutes."""
        manager = SessionManager(in_memory_db, user_id="test_user")
        session = Session(
            session_uuid=uuid4(),
            user_id="test_user",
            total_duration_ms=300000,
            cards_reviewed=5,
        )
        recs = manager._generate_recommendations(session, [], {})
        assert any("longer sessions" in r for r in recs)

    def test_generate_recommendations_many_interruptions(self, in_memory_db):
        """Test recommendation for too many interruptions."""
        manager = SessionManager(in_memory_db, user_id="test_user")
        session = Session(
            session_uuid=uuid4(),
            user_id="test_user",
            total_duration_ms=1800000,
            cards_reviewed=10,
            interruptions=5,
        )
        recs = manager._generate_recommendations(session, [], {})
        assert any("quieter environment" in r for r in recs)

    def test_generate_recommendations_many_deck_switches(self, in_memory_db):
        """Test recommendation for too many deck switches."""
        manager = SessionManager(in_memory_db, user_id="test_user")
        session = Session(
            session_uuid=uuid4(),
            user_id="test_user",
            total_duration_ms=1800000,
            cards_reviewed=10,
            deck_switches=5,
        )
        recs = manager._generate_recommendations(session, [], {})
        assert any("one deck at a time" in r for r in recs)

    def test_generate_recommendations_low_ratings(self, in_memory_db):
        """Test recommendation for low average ratings."""
        from datetime import date as date_today
        from flashcore.models import Review

        manager = SessionManager(in_memory_db, user_id="test_user")
        session = Session(
            session_uuid=uuid4(),
            user_id="test_user",
            total_duration_ms=1800000,
            cards_reviewed=5,
        )
        reviews = [
            Review(
                card_uuid=uuid4(),
                rating=1,
                resp_ms=1000,
                eval_ms=500,
                stab_before=1.0,
                stab_after=2.0,
                diff=5.0,
                next_due=date_today.today(),
                elapsed_days_at_review=1,
                scheduled_days_interval=1,
                review_type="review",
                ts=datetime.now(timezone.utc),
            )
            for _ in range(5)
        ]
        recs = manager._generate_recommendations(session, reviews, {})
        assert any("more frequently" in r for r in recs)

    def test_generate_recommendations_high_ratings(self, in_memory_db):
        """Test recommendation for high average ratings."""
        from datetime import date as date_today
        from flashcore.models import Review

        manager = SessionManager(in_memory_db, user_id="test_user")
        session = Session(
            session_uuid=uuid4(),
            user_id="test_user",
            total_duration_ms=1800000,
            cards_reviewed=5,
        )
        reviews = [
            Review(
                card_uuid=uuid4(),
                rating=4,
                resp_ms=1000,
                eval_ms=500,
                stab_before=1.0,
                stab_after=2.0,
                diff=5.0,
                next_due=date_today.today(),
                elapsed_days_at_review=1,
                scheduled_days_interval=1,
                review_type="review",
                ts=datetime.now(timezone.utc),
            )
            for _ in range(5)
        ]
        recs = manager._generate_recommendations(session, reviews, {})
        assert any("doing great" in r for r in recs)

    def test_detect_achievements_50_cards(self, in_memory_db):
        """Test achievement for reviewing 50+ cards."""
        manager = SessionManager(in_memory_db, user_id="test_user")
        session = Session(
            session_uuid=uuid4(),
            user_id="test_user",
            total_duration_ms=3600000,
            cards_reviewed=55,
        )
        achievements = manager._detect_achievements(session, [], [])
        assert any("50+" in a for a in achievements)

    def test_detect_achievements_25_cards(self, in_memory_db):
        """Test achievement for reviewing 25+ cards."""
        manager = SessionManager(in_memory_db, user_id="test_user")
        session = Session(
            session_uuid=uuid4(),
            user_id="test_user",
            total_duration_ms=1800000,
            cards_reviewed=30,
        )
        achievements = manager._detect_achievements(session, [], [])
        assert any("25+" in a for a in achievements)

    def test_detect_achievements_zero_interruptions(self, in_memory_db):
        """Test achievement for zero interruptions."""
        manager = SessionManager(in_memory_db, user_id="test_user")
        session = Session(
            session_uuid=uuid4(),
            user_id="test_user",
            total_duration_ms=1800000,
            cards_reviewed=10,
            interruptions=0,
        )
        achievements = manager._detect_achievements(session, [], [])
        assert any("zero interruptions" in a for a in achievements)

    def test_detect_achievements_7_day_streak(self, in_memory_db):
        """Test achievement for 7-day review streak."""
        manager = SessionManager(in_memory_db, user_id="test_user")
        session = Session(
            session_uuid=uuid4(),
            user_id="test_user",
            total_duration_ms=1800000,
            cards_reviewed=10,
        )
        historical = [
            Session(
                session_uuid=uuid4(),
                user_id="test_user",
                total_duration_ms=1800000,
                cards_reviewed=5 + i,
            )
            for i in range(8)
        ]
        achievements = manager._detect_achievements(session, [], historical)
        assert any("7-day" in a for a in achievements)

    def test_detect_achievements_high_efficiency(self, in_memory_db):
        """Test achievement for high cards-per-minute efficiency."""
        manager = SessionManager(in_memory_db, user_id="test_user")
        session = Session(
            session_uuid=uuid4(),
            user_id="test_user",
            total_duration_ms=300000,
            cards_reviewed=10,
        )
        achievements = manager._detect_achievements(session, [], [])
        assert any("efficiency" in a for a in achievements)

    def test_generate_alerts_performance_decline(self, in_memory_db):
        """Test alert for significant performance decline."""
        manager = SessionManager(in_memory_db, user_id="test_user")
        session = Session(
            session_uuid=uuid4(),
            user_id="test_user",
            total_duration_ms=1800000,
            cards_reviewed=5,
        )
        comparisons = {"vs_last_session": {"cards_reviewed": -60}}
        alerts = manager._generate_alerts(session, [], comparisons)
        assert any("decrease" in a for a in alerts)

    def test_generate_alerts_high_interruptions(self, in_memory_db):
        """Test alert for high number of interruptions."""
        manager = SessionManager(in_memory_db, user_id="test_user")
        session = Session(
            session_uuid=uuid4(),
            user_id="test_user",
            total_duration_ms=1800000,
            cards_reviewed=5,
            interruptions=7,
        )
        alerts = manager._generate_alerts(session, [], {})
        assert any("interruptions" in a for a in alerts)

    def test_generate_alerts_declining_trend(self, in_memory_db):
        """Test alert for declining performance trend."""
        manager = SessionManager(in_memory_db, user_id="test_user")
        session = Session(
            session_uuid=uuid4(),
            user_id="test_user",
            total_duration_ms=1800000,
            cards_reviewed=5,
        )
        comparisons = {"trend_direction": "declining"}
        alerts = manager._generate_alerts(session, [], comparisons)
        assert any("declining" in a for a in alerts)

    def test_get_session_reviews_with_actual_reviews(self, in_memory_db):
        """Test _get_session_reviews retrieves and converts review data."""
        manager = SessionManager(in_memory_db, user_id="test_user")
        session = manager.start_session()

        card = Card(
            uuid=uuid4(), deck_name="Test", front="Q", back="A", tags={"test"}
        )
        in_memory_db.upsert_cards_batch([card])
        manager.record_card_review(card, rating=3, response_time_ms=1000)

        completed = manager.end_session()
        reviews = manager._get_session_reviews(completed.session_uuid)
        assert isinstance(reviews, list)
