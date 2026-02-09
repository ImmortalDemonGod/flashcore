"""
Tests for the Session model in flashcore.
Comprehensive test coverage for session-level analytics functionality.
"""

import pytest
from datetime import datetime, timezone, timedelta
from uuid import UUID, uuid4

from flashcore.models import Session


class TestSessionModel:
    """Test the Session Pydantic model."""

    def test_session_creation_defaults(self):
        """Test creating a session with default values."""
        session = Session()

        assert session.session_id is None
        assert isinstance(session.session_uuid, UUID)
        assert session.user_id is None
        assert isinstance(session.start_ts, datetime)
        assert session.end_ts is None
        assert session.total_duration_ms is None
        assert session.cards_reviewed == 0
        assert session.decks_accessed == set()
        assert session.deck_switches == 0
        assert session.interruptions == 0
        assert session.device_type is None
        assert session.platform is None

    def test_session_creation_with_values(self):
        """Test creating a session with explicit values."""
        session_uuid = uuid4()
        start_time = datetime.now(timezone.utc)

        session = Session(
            session_uuid=session_uuid,
            user_id="test_user",
            start_ts=start_time,
            device_type="desktop",
            platform="cli",
        )

        assert session.session_uuid == session_uuid
        assert session.user_id == "test_user"
        assert session.start_ts == start_time
        assert session.device_type == "desktop"
        assert session.platform == "cli"

    def test_session_is_active_property(self):
        """Test the is_active property."""
        session = Session()

        # New session should be active
        assert session.is_active is True

        # Ended session should not be active
        session.end_session()
        assert session.is_active is False

    def test_calculate_duration(self):
        """Test duration calculation."""
        start_time = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        end_time = datetime(
            2023, 1, 1, 10, 5, 30, tzinfo=timezone.utc
        )  # 5.5 minutes

        session = Session(start_ts=start_time)

        # No duration for active session
        assert session.calculate_duration() is None

        # Set end time and calculate
        session.end_ts = end_time
        duration = session.calculate_duration()
        assert duration == 330000  # 5.5 minutes = 330,000 ms

    def test_end_session(self):
        """Test ending a session."""
        session = Session()

        assert session.is_active is True
        assert session.end_ts is None
        assert session.total_duration_ms is None

        # End the session
        session.end_session()

        assert session.is_active is False
        assert session.end_ts is not None
        assert session.total_duration_ms is not None
        assert session.total_duration_ms >= 0

    def test_end_session_idempotent(self):
        """Test that ending a session multiple times doesn't change the end time."""
        session = Session()

        # End session first time
        session.end_session()
        first_end_time = session.end_ts
        first_duration = session.total_duration_ms

        # End session second time (should not change)
        session.end_session()

        assert session.end_ts == first_end_time
        assert session.total_duration_ms == first_duration

    def test_add_card_review_single_deck(self):
        """Test adding card reviews from a single deck."""
        session = Session()

        # Add reviews from same deck
        session.add_card_review("Deck A")
        assert session.cards_reviewed == 1
        assert session.decks_accessed == {"Deck A"}
        assert session.deck_switches == 0

        session.add_card_review("Deck A")
        assert session.cards_reviewed == 2
        assert session.decks_accessed == {"Deck A"}
        assert session.deck_switches == 0

    def test_add_card_review_multiple_decks(self):
        """Test adding card reviews from multiple decks."""
        session = Session()

        # First deck
        session.add_card_review("Deck A")
        assert session.cards_reviewed == 1
        assert session.decks_accessed == {"Deck A"}
        assert session.deck_switches == 0

        # Switch to second deck
        session.add_card_review("Deck B")
        assert session.cards_reviewed == 2
        assert session.decks_accessed == {"Deck A", "Deck B"}
        assert session.deck_switches == 1

        # Back to first deck
        session.add_card_review("Deck A")
        assert session.cards_reviewed == 3
        assert session.decks_accessed == {"Deck A", "Deck B"}
        assert (
            session.deck_switches == 1
        )  # No additional switch (deck already accessed)

        # Third deck
        session.add_card_review("Deck C")
        assert session.cards_reviewed == 4
        assert session.decks_accessed == {"Deck A", "Deck B", "Deck C"}
        assert session.deck_switches == 2

    def test_record_interruption(self):
        """Test recording interruptions."""
        session = Session()

        assert session.interruptions == 0

        session.record_interruption()
        assert session.interruptions == 1

        session.record_interruption()
        assert session.interruptions == 2

    def test_cards_per_minute_property(self):
        """Test cards per minute calculation."""
        session = Session()

        # No rate for active session
        assert session.cards_per_minute is None

        # Set up completed session
        session.cards_reviewed = 10
        session.total_duration_ms = 300000  # 5 minutes

        rate = session.cards_per_minute
        assert rate == 2.0  # 10 cards / 5 minutes = 2 cards/minute

    def test_cards_per_minute_zero_duration(self):
        """Test cards per minute with zero duration."""
        session = Session()
        session.cards_reviewed = 5
        session.total_duration_ms = 0

        assert session.cards_per_minute is None

    def test_cards_per_minute_no_duration(self):
        """Test cards per minute with no duration set."""
        session = Session()
        session.cards_reviewed = 5
        # total_duration_ms remains None

        assert session.cards_per_minute is None

    def test_session_validation_negative_values(self):
        """Test that negative values are rejected."""
        with pytest.raises(ValueError):
            Session(total_duration_ms=-1)

        with pytest.raises(ValueError):
            Session(cards_reviewed=-1)

        with pytest.raises(ValueError):
            Session(deck_switches=-1)

        with pytest.raises(ValueError):
            Session(interruptions=-1)

    def test_session_model_config(self):
        """Test that the model configuration is correct."""
        session = Session()

        # Test that extra fields are forbidden
        with pytest.raises(ValueError):
            Session(invalid_field="should_fail")

    def test_session_uuid_uniqueness(self):
        """Test that each session gets a unique UUID."""
        session1 = Session()
        session2 = Session()

        assert session1.session_uuid != session2.session_uuid

    def test_complex_session_workflow(self):
        """Test a complex session workflow with multiple operations."""
        session = Session(
            user_id="test_user", device_type="desktop", platform="cli"
        )

        # Review cards from multiple decks
        session.add_card_review("Math")
        session.add_card_review("Math")
        session.add_card_review("Science")  # Switch
        session.record_interruption()
        session.add_card_review("History")  # Switch
        session.add_card_review("Math")  # No switch (already accessed)
        session.record_interruption()

        # Verify final state
        assert session.cards_reviewed == 5
        assert session.decks_accessed == {"Math", "Science", "History"}
        assert session.deck_switches == 2
        assert session.interruptions == 2
        assert session.is_active is True

        # End session
        session.end_session()

        assert session.is_active is False
        assert session.total_duration_ms is not None
        # Cards per minute might be None for very short sessions
        if session.total_duration_ms > 0:
            assert session.cards_per_minute is not None


class TestSessionEdgeCases:
    """Test edge cases and error conditions for Session model."""

    def test_session_with_future_start_time(self):
        """Test session with future start time."""
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)
        session = Session(start_ts=future_time)

        # Should be allowed (might be useful for scheduled sessions)
        assert session.start_ts == future_time

    def test_session_with_end_before_start(self):
        """Test session where end time is before start time."""
        start_time = datetime.now(timezone.utc)
        end_time = start_time - timedelta(minutes=5)

        session = Session(start_ts=start_time, end_ts=end_time)

        # Duration calculation should handle this gracefully
        duration = session.calculate_duration()
        assert duration < 0  # Negative duration indicates error condition

    def test_session_with_very_long_duration(self):
        """Test session with extremely long duration."""
        start_time = datetime(2023, 1, 1, tzinfo=timezone.utc)
        end_time = datetime(2023, 1, 2, tzinfo=timezone.utc)  # 24 hours

        session = Session(start_ts=start_time, end_ts=end_time)
        duration = session.calculate_duration()

        assert duration == 24 * 60 * 60 * 1000  # 24 hours in milliseconds

    def test_session_with_empty_deck_name(self):
        """Test adding review with empty deck name."""
        session = Session()

        session.add_card_review("")
        assert session.cards_reviewed == 1
        assert "" in session.decks_accessed

    def test_session_with_unicode_deck_names(self):
        """Test session with unicode deck names."""
        session = Session()

        session.add_card_review("数学")  # Chinese
        session.add_card_review("Français")  # French
        session.add_card_review("العربية")  # Arabic

        assert session.cards_reviewed == 3
        assert session.decks_accessed == {"数学", "Français", "العربية"}
        assert session.deck_switches == 2
