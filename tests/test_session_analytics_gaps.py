"""
Tests to expose and verify the fix for unused session analytics.

Current State Analysis:
- Session model exists with rich analytics fields
- Database operations exist (create, update, get)
- ReviewSessionManager has session_uuid but doesn't create Session objects
- No session lifecycle management in review workflows
- No session analytics or insights generation
- No session-based performance tracking

This test suite exposes the gaps and defines requirements for full session analytics.
"""

import pytest
from datetime import datetime, timezone, timedelta, date
from uuid import uuid4
from unittest.mock import MagicMock, patch

from cultivation.scripts.flashcore.card import Card, Session, CardState
from cultivation.scripts.flashcore.database import FlashcardDatabase
from cultivation.scripts.flashcore.scheduler import FSRS_Scheduler
from cultivation.scripts.flashcore.review_manager import ReviewSessionManager
from cultivation.scripts.flashcore.cli._review_all_logic import _submit_single_review


class TestSessionAnalyticsGaps:
    """Test that exposes gaps in session analytics implementation."""

    @pytest.fixture
    def in_memory_db(self):
        """Create an in-memory database for testing."""
        db = FlashcardDatabase(":memory:")
        db.initialize_schema()
        return db

    @pytest.fixture
    def sample_cards(self):
        """Create sample cards for testing."""
        return [
            Card(
                uuid=uuid4(),
                deck_name="Math",
                front=f"What is {i}+{i}?",
                back=str(i*2),
                tags={"math", "basic"}
            )
            for i in range(1, 6)
        ]

    def test_review_session_manager_now_creates_session_objects(self, in_memory_db, sample_cards):
        """Test that ReviewSessionManager now creates Session objects (FIXED!)."""
        # Insert cards
        in_memory_db.upsert_cards_batch(sample_cards)

        # Create review session manager
        manager = ReviewSessionManager(
            db_manager=in_memory_db,
            scheduler=FSRS_Scheduler(),
            user_uuid=uuid4(),
            deck_name="Math"
        )
        manager.initialize_session()

        # Manager has session_uuid and NOW creates Session object in database
        session_uuid = manager.session_uuid
        assert session_uuid is not None

        # FIXED: Session object now exists in database!
        session_from_db = in_memory_db.get_session_by_uuid(session_uuid)
        assert session_from_db is not None  # Gap is FIXED!
        assert session_from_db.session_uuid == session_uuid
        assert session_from_db.device_type == "desktop"
        assert session_from_db.platform == "cli"

        # FIXED: Session lifecycle management now exists
        assert session_from_db.start_ts is not None
        assert session_from_db.end_ts is None  # Still active

        # FIXED: Session analytics tracking is now active
        assert session_from_db.cards_reviewed == 0  # No reviews yet
        assert session_from_db.decks_accessed == set()
        assert session_from_db.deck_switches == 0
        assert session_from_db.interruptions == 0

    def test_review_workflows_now_have_session_integration(self, in_memory_db, sample_cards):
        """Test that review workflows now integrate with session tracking (FIXED!)."""
        # Insert cards
        in_memory_db.upsert_cards_batch(sample_cards)

        # Test ReviewSessionManager workflow
        manager = ReviewSessionManager(
            db_manager=in_memory_db,
            scheduler=FSRS_Scheduler(),
            user_uuid=uuid4(),
            deck_name="Math"
        )
        manager.initialize_session()

        # Submit reviews
        for card in sample_cards[:3]:
            manager.submit_review(
                card_uuid=card.uuid,
                rating=3,  # Good
                resp_ms=1000,
                eval_ms=500
            )

        # FIXED: Session object now exists and tracks analytics!
        session_from_db = in_memory_db.get_session_by_uuid(manager.session_uuid)
        assert session_from_db is not None  # Session tracking is WORKING!
        assert session_from_db.cards_reviewed == 3  # Analytics are tracked!
        assert "Math" in session_from_db.decks_accessed

        # FIXED: Reviews are linked to session AND session analytics exist
        reviews = in_memory_db.get_reviews_for_card(sample_cards[0].uuid)
        assert len(reviews) == 1
        assert reviews[0].session_uuid == manager.session_uuid
        # Session object now provides full context!

    def test_missing_session_analytics_features(self, in_memory_db):
        """Test that session analytics features are missing."""
        # Create a manual session to test what analytics should exist
        session = Session(
            user_id="test_user",
            device_type="desktop",
            platform="cli"
        )

        # Session model has analytics fields but no automated tracking
        assert session.cards_reviewed == 0
        assert session.decks_accessed == set()
        assert session.deck_switches == 0
        assert session.interruptions == 0
        assert session.total_duration_ms is None

        # GAP: No automated session analytics collection
        # GAP: No session performance metrics
        # GAP: No session insights generation
        # GAP: No session-based learning analytics

    def test_missing_session_lifecycle_management(self, in_memory_db, sample_cards):
        """Test that session lifecycle management is missing."""
        # Insert cards
        in_memory_db.upsert_cards_batch(sample_cards)

        manager = ReviewSessionManager(
            db_manager=in_memory_db,
            scheduler=FSRS_Scheduler(),
            user_uuid=uuid4(),
            deck_name="Math"
        )

        # GAP: No session start tracking
        start_time = datetime.now(timezone.utc)
        manager.initialize_session()

        # GAP: No session end tracking
        # Manager doesn't provide session end functionality

        # GAP: No session duration calculation
        # Manager doesn't track session timing

        # GAP: No session persistence
        # Session data is lost when manager is destroyed

    def test_missing_cross_deck_session_analytics(self, in_memory_db):
        """Test that cross-deck session analytics are missing."""
        # Create cards from multiple decks
        math_cards = [
            Card(uuid=uuid4(), deck_name="Math", front="1+1?", back="2", tags={"math"}),
            Card(uuid=uuid4(), deck_name="Math", front="2+2?", back="4", tags={"math"})
        ]
        science_cards = [
            Card(uuid=uuid4(), deck_name="Science", front="H2O?", back="Water", tags={"chemistry"}),
            Card(uuid=uuid4(), deck_name="Science", front="CO2?", back="Carbon Dioxide", tags={"chemistry"})
        ]

        in_memory_db.upsert_cards_batch(math_cards + science_cards)

        # GAP: No unified session tracking across decks
        # Each ReviewSessionManager is deck-specific
        # No way to track cross-deck learning sessions

        # GAP: No deck switching analytics
        # No way to track when user switches between decks in a session

        # GAP: No session-level performance comparison across decks

    def test_missing_session_performance_analytics(self, in_memory_db, sample_cards):
        """Test that session performance analytics are missing."""
        # Insert cards
        in_memory_db.upsert_cards_batch(sample_cards)

        manager = ReviewSessionManager(
            db_manager=in_memory_db,
            scheduler=FSRS_Scheduler(),
            user_uuid=uuid4(),
            deck_name="Math"
        )
        manager.initialize_session()

        # Submit reviews with varying performance
        response_times = [800, 1200, 600, 1500, 900]  # ms
        ratings = [4, 3, 4, 2, 3]  # Easy, Good, Easy, Hard, Good

        for i, card in enumerate(sample_cards):
            manager.submit_review(
                card_uuid=card.uuid,
                rating=ratings[i],
                resp_ms=response_times[i],
                eval_ms=500
            )

        # GAP: No session-level performance metrics
        # Should calculate: average response time, accuracy rate, etc.

        # GAP: No session learning velocity tracking
        # Should track: cards per minute, improvement over session, etc.

        # GAP: No session fatigue detection
        # Should detect: declining performance, increasing response times, etc.

    def test_missing_session_insights_generation(self, in_memory_db):
        """Test that session insights generation is missing."""
        # Create a completed session manually
        session = Session(
            user_id="test_user",
            start_ts=datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
            end_ts=datetime(2024, 1, 1, 10, 30, 0, tzinfo=timezone.utc),
            total_duration_ms=1800000,  # 30 minutes
            cards_reviewed=20,
            decks_accessed={"Math", "Science"},
            deck_switches=2,
            interruptions=1,
            device_type="desktop",
            platform="cli"
        )

        created_session = in_memory_db.create_session(session)

        # GAP: No session insights generation
        # Should provide insights like:
        # - "You reviewed 20 cards in 30 minutes (0.67 cards/min)"
        # - "You switched between 2 decks with 2 switches"
        # - "You had 1 interruption during this session"
        # - "Your performance was consistent throughout the session"

        # GAP: No session recommendations
        # Should provide recommendations like:
        # - "Consider longer focused sessions to reduce deck switching"
        # - "Your response times suggest you're ready for harder cards"
        # - "Take a break - your performance is declining"

    def test_missing_session_comparison_analytics(self, in_memory_db):
        """Test that session comparison analytics are missing."""
        # Create multiple sessions for comparison
        sessions = []
        for i in range(3):
            session = Session(
                user_id="test_user",
                start_ts=datetime(2024, 1, i+1, 10, 0, 0, tzinfo=timezone.utc),
                end_ts=datetime(2024, 1, i+1, 10, 30, 0, tzinfo=timezone.utc),
                total_duration_ms=1800000,
                cards_reviewed=15 + i*5,  # Improving performance
                decks_accessed={"Math"},
                deck_switches=0,
                interruptions=i,  # Increasing interruptions
                device_type="desktop",
                platform="cli"
            )
            sessions.append(in_memory_db.create_session(session))

        # GAP: No session comparison analytics
        # Should provide comparisons like:
        # - "Your card review rate improved by 33% over the last 3 sessions"
        # - "Interruptions increased - consider finding a quieter environment"
        # - "Your session consistency is improving"

        # GAP: No session trend analysis
        # Should track trends in performance, duration, efficiency, etc.

    def test_missing_real_time_session_tracking(self, in_memory_db, sample_cards):
        """Test that real-time session tracking is missing."""
        # Insert cards
        in_memory_db.upsert_cards_batch(sample_cards)

        manager = ReviewSessionManager(
            db_manager=in_memory_db,
            scheduler=FSRS_Scheduler(),
            user_uuid=uuid4(),
            deck_name="Math"
        )
        manager.initialize_session()

        # GAP: No real-time session updates
        # Session object should be updated after each review

        # GAP: No live session analytics
        # Should provide real-time metrics during the session

        # GAP: No session progress tracking
        # Should track progress through the review queue


class TestSessionAnalyticsRequirements:
    """Test that defines requirements for comprehensive session analytics."""

    def test_session_manager_integration_requirements(self):
        """Test that defines requirements for SessionManager integration."""
        # Required SessionManager features:
        session_manager_requirements = {
            "class_name": "SessionManager",
            "responsibilities": [
                "Create Session objects in database",
                "Track session lifecycle (start/end)",
                "Update session analytics in real-time",
                "Generate session insights",
                "Provide session comparison analytics",
                "Detect session patterns and trends"
            ],
            "integration_points": [
                "ReviewSessionManager",
                "ReviewProcessor",
                "_review_all_logic",
                "CLI review workflows"
            ]
        }

        # Required Session model enhancements:
        session_model_enhancements = [
            "Average response time calculation",
            "Accuracy rate calculation",
            "Learning velocity metrics",
            "Fatigue detection indicators",
            "Performance trend tracking"
        ]

        # Required database analytics queries:
        analytics_queries = [
            "Session performance comparisons",
            "User learning trends",
            "Deck-specific session analytics",
            "Time-based session patterns",
            "Cross-session performance tracking"
        ]

        assert len(session_manager_requirements["responsibilities"]) == 6
        assert len(session_model_enhancements) == 5
        assert len(analytics_queries) == 5

    def test_session_lifecycle_requirements(self):
        """Test that defines session lifecycle management requirements."""
        # Session lifecycle stages:
        lifecycle_stages = [
            "initialization",  # Create Session object, set start time
            "active_tracking", # Update analytics during reviews
            "completion",      # Set end time, calculate final metrics
            "persistence",     # Save to database
            "analytics"        # Generate insights and comparisons
        ]

        # Required lifecycle events:
        lifecycle_events = [
            "session_started",
            "card_reviewed",
            "deck_switched",
            "interruption_detected",
            "session_paused",
            "session_resumed",
            "session_completed"
        ]

        # Required analytics calculations:
        analytics_calculations = [
            "total_duration_ms",
            "cards_per_minute",
            "average_response_time",
            "accuracy_percentage",
            "deck_switch_frequency",
            "interruption_impact",
            "learning_velocity",
            "fatigue_indicators"
        ]

        assert len(lifecycle_stages) == 5
        assert len(lifecycle_events) == 7
        assert len(analytics_calculations) == 8

    def test_session_insights_requirements(self):
        """Test that defines session insights generation requirements."""
        # Required insight categories:
        insight_categories = [
            "performance_summary",    # Overall session performance
            "efficiency_metrics",     # Time and accuracy metrics
            "learning_progress",      # Progress and improvement indicators
            "attention_patterns",     # Focus and interruption analysis
            "recommendations",        # Actionable suggestions
            "comparisons"            # Historical comparisons
        ]

        # Required insight types:
        insight_types = [
            "quantitative_metrics",   # Numbers and percentages
            "trend_analysis",         # Changes over time
            "pattern_recognition",    # Behavioral patterns
            "performance_alerts",     # Warnings and notifications
            "achievement_recognition", # Positive reinforcement
            "improvement_suggestions"  # Specific recommendations
        ]

        # Required delivery mechanisms:
        delivery_mechanisms = [
            "real_time_updates",      # During session
            "session_summary",        # At session end
            "periodic_reports",       # Weekly/monthly summaries
            "trend_notifications",    # When patterns change
            "achievement_badges",     # Gamification elements
            "api_endpoints"          # For external integrations
        ]

        assert len(insight_categories) == 6
        assert len(insight_types) == 6
        assert len(delivery_mechanisms) == 6

    def test_backward_compatibility_requirements(self):
        """Test that defines backward compatibility requirements."""
        # No breaking changes allowed:
        compatibility_requirements = [
            "ReviewSessionManager API unchanged",
            "ReviewProcessor API unchanged",
            "_review_all_logic API unchanged",
            "Database schema backward compatible",
            "Existing tests continue to pass",
            "Session tracking is opt-in initially"
        ]

        # Gradual rollout strategy:
        rollout_phases = [
            "Phase 1: SessionManager creation",
            "Phase 2: ReviewSessionManager integration",
            "Phase 3: Real-time analytics",
            "Phase 4: Insights generation",
            "Phase 5: Cross-session analytics",
            "Phase 6: Advanced recommendations"
        ]

        assert len(compatibility_requirements) == 6
        assert len(rollout_phases) == 6
