"""
Tests for session database operations in flashcore.
Comprehensive test coverage for session CRUD operations and analytics.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from cultivation.scripts.flashcore.database import FlashcardDatabase
from cultivation.scripts.flashcore.exceptions import DatabaseConnectionError, CardOperationError
from cultivation.scripts.flashcore.card import Session


@pytest.fixture
def in_memory_db():
    """Create an in-memory database for testing."""
    db = FlashcardDatabase(":memory:")
    db.initialize_schema()
    return db


@pytest.fixture
def sample_session():
    """Create a sample session for testing."""
    return Session(
        user_id="test_user",
        device_type="desktop",
        platform="cli"
    )


@pytest.fixture
def completed_session():
    """Create a completed session for testing."""
    start_time = datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    end_time = datetime(2023, 1, 1, 10, 30, 0, tzinfo=timezone.utc)

    session = Session(
        user_id="test_user",
        start_ts=start_time,
        end_ts=end_time,
        total_duration_ms=1800000,  # 30 minutes
        cards_reviewed=15,
        decks_accessed={"Math", "Science"},
        deck_switches=1,
        interruptions=2,
        device_type="desktop",
        platform="cli"
    )
    return session


class TestSessionDatabaseOperations:
    """Test session CRUD operations."""

    def test_create_session(self, in_memory_db, sample_session):
        """Test creating a new session."""
        # Create session
        created_session = in_memory_db.create_session(sample_session)

        # Verify session was created with ID
        assert created_session.session_id is not None
        assert created_session.session_uuid == sample_session.session_uuid
        assert created_session.user_id == sample_session.user_id
        assert created_session.device_type == sample_session.device_type
        assert created_session.platform == sample_session.platform

    def test_create_session_read_only_mode(self, sample_session, tmp_path):
        """Test that creating session fails in read-only mode."""
        # Create a temporary database file first
        db_file = tmp_path / "test.db"
        temp_db = FlashcardDatabase(str(db_file))
        temp_db.initialize_schema()
        # Don't need to explicitly close, just let it go out of scope

        # Now open in read-only mode
        db = FlashcardDatabase(str(db_file), read_only=True)

        with pytest.raises(DatabaseConnectionError):
            db.create_session(sample_session)

    def test_get_session_by_uuid(self, in_memory_db, sample_session):
        """Test retrieving a session by UUID."""
        # Create session
        created_session = in_memory_db.create_session(sample_session)

        # Retrieve session
        retrieved_session = in_memory_db.get_session_by_uuid(created_session.session_uuid)

        assert retrieved_session is not None
        assert retrieved_session.session_uuid == created_session.session_uuid
        assert retrieved_session.session_id == created_session.session_id
        assert retrieved_session.user_id == created_session.user_id

    def test_get_session_by_uuid_not_found(self, in_memory_db):
        """Test retrieving a non-existent session."""
        non_existent_uuid = uuid4()
        result = in_memory_db.get_session_by_uuid(non_existent_uuid)
        assert result is None

    def test_update_session(self, in_memory_db, sample_session):
        """Test updating an existing session."""
        # Create session
        created_session = in_memory_db.create_session(sample_session)

        # Modify session
        created_session.cards_reviewed = 10
        created_session.decks_accessed.add("New Deck")
        created_session.deck_switches = 2
        created_session.end_session()

        # Update session
        updated_session = in_memory_db.update_session(created_session)

        # Verify updates
        assert updated_session.cards_reviewed == 10
        assert "New Deck" in updated_session.decks_accessed
        assert updated_session.deck_switches == 2
        assert updated_session.end_ts is not None

    def test_update_session_read_only_mode(self, sample_session, tmp_path):
        """Test that updating a session fails when the database is in read-only mode."""
        db_file = tmp_path / "test_readonly.db"

        # 1. Create a DB and a session in writeable mode.
        db_write = FlashcardDatabase(db_file)
        db_write.initialize_schema()
        created_session = db_write.create_session(sample_session)
        created_session.cards_reviewed = 10  # Make a change to update
        db_write.close_connection()  # Close to release any locks

        # 2. Open the same DB in read-only mode.
        db_read = FlashcardDatabase(db_file, read_only=True)

        # 3. Attempt to update and assert that a DatabaseConnectionError is raised.
        with pytest.raises(DatabaseConnectionError, match="Cannot update session in read-only mode."):
            db_read.update_session(created_session)

    def test_update_session_without_uuid(self, in_memory_db):
        """Test that updating session without UUID fails."""
        # Create a session and then manually set session_uuid to None in the database check
        session = Session()

        # The validation should happen in the update_session method, not in Pydantic
        # Let's test by creating a session with a valid UUID first, then testing the database logic
        created_session = in_memory_db.create_session(session)

        # Now test the database validation by passing None directly to the method
        # We'll modify the session object's __dict__ to bypass Pydantic validation
        created_session.__dict__['session_uuid'] = None

        with pytest.raises(ValueError):
            in_memory_db.update_session(created_session)

    def test_get_active_sessions(self, in_memory_db):
        """Test retrieving active sessions."""
        # Create active session
        active_session = Session(user_id="user1")
        in_memory_db.create_session(active_session)

        # Create completed session
        completed_session = Session(user_id="user2")
        completed_session.end_session()
        in_memory_db.create_session(completed_session)

        # Get active sessions
        active_sessions = in_memory_db.get_active_sessions()

        assert len(active_sessions) == 1
        assert active_sessions[0].user_id == "user1"
        assert active_sessions[0].is_active is True

    def test_get_active_sessions_by_user(self, in_memory_db):
        """Test retrieving active sessions for specific user."""
        # Create sessions for different users
        user1_session = Session(user_id="user1")
        user2_session = Session(user_id="user2")

        in_memory_db.create_session(user1_session)
        in_memory_db.create_session(user2_session)

        # Get active sessions for user1
        user1_sessions = in_memory_db.get_active_sessions(user_id="user1")

        assert len(user1_sessions) == 1
        assert user1_sessions[0].user_id == "user1"

    def test_get_recent_sessions(self, in_memory_db):
        """Test retrieving recent sessions."""
        # Create sessions with different start times
        session1 = Session(
            user_id="user1",
            start_ts=datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        )
        session2 = Session(
            user_id="user2",
            start_ts=datetime(2023, 1, 1, 11, 0, 0, tzinfo=timezone.utc)
        )
        session3 = Session(
            user_id="user3",
            start_ts=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        )

        in_memory_db.create_session(session1)
        in_memory_db.create_session(session2)
        in_memory_db.create_session(session3)

        # Get recent sessions (should be ordered by start_ts DESC)
        recent_sessions = in_memory_db.get_recent_sessions(limit=2)

        assert len(recent_sessions) == 2
        assert recent_sessions[0].user_id == "user3"  # Most recent
        assert recent_sessions[1].user_id == "user2"  # Second most recent

    def test_get_recent_sessions_by_user(self, in_memory_db):
        """Test retrieving recent sessions for specific user."""
        # Create sessions for different users
        user1_session1 = Session(
            user_id="user1",
            start_ts=datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        )
        user1_session2 = Session(
            user_id="user1",
            start_ts=datetime(2023, 1, 1, 11, 0, 0, tzinfo=timezone.utc)
        )
        user2_session = Session(
            user_id="user2",
            start_ts=datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        )

        in_memory_db.create_session(user1_session1)
        in_memory_db.create_session(user1_session2)
        in_memory_db.create_session(user2_session)

        # Get recent sessions for user1
        user1_sessions = in_memory_db.get_recent_sessions(user_id="user1")

        assert len(user1_sessions) == 2
        assert all(s.user_id == "user1" for s in user1_sessions)
        assert user1_sessions[0].start_ts > user1_sessions[1].start_ts  # Ordered DESC

    def test_session_with_decks_accessed(self, in_memory_db):
        """Test session with multiple decks accessed."""
        session = Session(user_id="test_user")
        session.decks_accessed = {"Math", "Science", "History"}

        # Create and retrieve session
        created_session = in_memory_db.create_session(session)
        retrieved_session = in_memory_db.get_session_by_uuid(created_session.session_uuid)

        assert retrieved_session.decks_accessed == {"Math", "Science", "History"}

    def test_session_with_empty_decks_accessed(self, in_memory_db):
        """Test session with empty decks_accessed set."""
        session = Session(user_id="test_user")
        # decks_accessed defaults to empty set

        created_session = in_memory_db.create_session(session)
        retrieved_session = in_memory_db.get_session_by_uuid(created_session.session_uuid)

        assert retrieved_session.decks_accessed == set()

    def test_session_data_types_preservation(self, in_memory_db, completed_session):
        """Test that all data types are preserved correctly."""
        created_session = in_memory_db.create_session(completed_session)
        retrieved_session = in_memory_db.get_session_by_uuid(created_session.session_uuid)

        # Check all fields are preserved
        assert retrieved_session.user_id == completed_session.user_id
        assert retrieved_session.start_ts == completed_session.start_ts
        assert retrieved_session.end_ts == completed_session.end_ts
        assert retrieved_session.total_duration_ms == completed_session.total_duration_ms
        assert retrieved_session.cards_reviewed == completed_session.cards_reviewed
        assert retrieved_session.decks_accessed == completed_session.decks_accessed
        assert retrieved_session.deck_switches == completed_session.deck_switches
        assert retrieved_session.interruptions == completed_session.interruptions
        assert retrieved_session.device_type == completed_session.device_type
        assert retrieved_session.platform == completed_session.platform


class TestSessionDatabaseErrorHandling:
    """Test error handling in session database operations."""

    def test_create_session_database_error(self, in_memory_db, sample_session):
        """Test handling of database errors during session creation."""
        # Close the database connection to simulate error
        in_memory_db.close_connection()

        with pytest.raises(CardOperationError):
            in_memory_db.create_session(sample_session)

    def test_update_session_database_error(self, in_memory_db, sample_session):
        """Test handling of database errors during session update."""
        # Create session first
        created_session = in_memory_db.create_session(sample_session)

        # Close the database connection to simulate error
        in_memory_db.close_connection()

        with pytest.raises(CardOperationError):
            in_memory_db.update_session(created_session)

    def test_get_session_database_error(self, in_memory_db):
        """Test handling of database errors during session retrieval."""
        # Close the database connection to simulate error
        in_memory_db.close_connection()

        with pytest.raises(CardOperationError):
            in_memory_db.get_session_by_uuid(uuid4())

    def test_get_active_sessions_database_error(self, in_memory_db):
        """Test handling of database errors during active sessions retrieval."""
        # Close the database connection to simulate error
        in_memory_db.close_connection()

        with pytest.raises(CardOperationError):
            in_memory_db.get_active_sessions()

    def test_get_recent_sessions_database_error(self, in_memory_db):
        """Test handling of database errors during recent sessions retrieval."""
        # Close the database connection to simulate error
        in_memory_db.close_connection()

        with pytest.raises(CardOperationError):
            in_memory_db.get_recent_sessions()


class TestSessionReviewIntegration:
    """Test integration between sessions and reviews."""

    def test_get_reviews_for_session_empty(self, in_memory_db, sample_session):
        """Test getting reviews for session with no reviews."""
        created_session = in_memory_db.create_session(sample_session)
        reviews = in_memory_db.get_reviews_for_session(created_session.session_uuid)

        assert reviews == []

    def test_get_reviews_for_session_database_error(self, in_memory_db):
        """Test handling of database errors when getting reviews for session."""
        # Close the database connection to simulate error
        in_memory_db.close_connection()

        with pytest.raises(Exception):  # Could be ReviewOperationError or CardOperationError
            in_memory_db.get_reviews_for_session(uuid4())


class TestSessionDatabaseEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_session_with_null_values(self, in_memory_db):
        """Test session with null/None values."""
        session = Session()
        # Most fields should be None or default values

        created_session = in_memory_db.create_session(session)
        retrieved_session = in_memory_db.get_session_by_uuid(created_session.session_uuid)

        assert retrieved_session.user_id is None
        assert retrieved_session.device_type is None
        assert retrieved_session.platform is None
        assert retrieved_session.end_ts is None

    def test_session_with_very_long_duration(self, in_memory_db):
        """Test session with extremely long duration."""
        session = Session()
        session.total_duration_ms = 86400000  # 24 hours in milliseconds

        created_session = in_memory_db.create_session(session)
        retrieved_session = in_memory_db.get_session_by_uuid(created_session.session_uuid)

        assert retrieved_session.total_duration_ms == 86400000

    def test_session_with_unicode_user_id(self, in_memory_db):
        """Test session with unicode user ID."""
        session = Session(user_id="用户123")  # Chinese characters

        created_session = in_memory_db.create_session(session)
        retrieved_session = in_memory_db.get_session_by_uuid(created_session.session_uuid)

        assert retrieved_session.user_id == "用户123"

    def test_session_with_large_deck_list(self, in_memory_db):
        """Test session with many decks accessed."""
        session = Session(user_id="test_user")
        # Add many decks
        session.decks_accessed = {f"Deck_{i}" for i in range(100)}

        created_session = in_memory_db.create_session(session)
        retrieved_session = in_memory_db.get_session_by_uuid(created_session.session_uuid)

        assert len(retrieved_session.decks_accessed) == 100
        assert "Deck_50" in retrieved_session.decks_accessed

    def test_get_recent_sessions_zero_limit(self, in_memory_db, sample_session):
        """Test getting recent sessions with zero limit."""
        in_memory_db.create_session(sample_session)

        # Zero limit should return all sessions
        sessions = in_memory_db.get_recent_sessions(limit=0)
        assert len(sessions) == 1

    def test_get_recent_sessions_negative_limit(self, in_memory_db, sample_session):
        """Test getting recent sessions with negative limit."""
        in_memory_db.create_session(sample_session)

        # Negative limit should return all sessions
        sessions = in_memory_db.get_recent_sessions(limit=-1)
        assert len(sessions) == 1
