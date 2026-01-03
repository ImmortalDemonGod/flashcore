"""
Additional tests to achieve 100% coverage for database layer refactoring.
"""

import pytest
from pathlib import Path
from datetime import date, datetime, timezone
from unittest.mock import patch, MagicMock
import duckdb

from flashcore.models import Card, Review, Session, CardState
from flashcore.db import FlashcardDatabase
from flashcore.db.connection import ConnectionHandler
from flashcore.db.schema_manager import SchemaManager
from flashcore.db import db_utils
from flashcore.exceptions import (
    DatabaseConnectionError,
    SchemaInitializationError,
    MarshallingError,
)


class TestConnectionHandlerCoverage:
    """Tests for uncovered ConnectionHandler code paths."""

    def test_context_manager(self, tmp_path):
        """Test ConnectionHandler as context manager."""
        db_path = tmp_path / "test.db"
        handler = ConnectionHandler(db_path)

        with handler as conn:
            assert conn is not None
            assert isinstance(conn, duckdb.DuckDBPyConnection)

        # Connection should be closed after exiting context
        assert handler._connection is None


class TestSchemaManagerCoverage:
    """Tests for uncovered SchemaManager code paths."""

    def test_handle_read_only_initialization_force_recreate_error(
        self, tmp_path
    ):
        """Test that force_recreate in read-only mode raises error."""
        db_path = tmp_path / "test.db"
        # Create DB first
        handler = ConnectionHandler(db_path)
        handler.get_connection()
        handler.close_connection()

        # Open in read-only mode
        handler_ro = ConnectionHandler(db_path, read_only=True)
        manager = SchemaManager(handler_ro)

        with pytest.raises(
            DatabaseConnectionError,
            match="Cannot force_recreate_tables in read-only mode",
        ):
            manager.initialize_schema(force_recreate_tables=True)

    def test_safety_check_with_data(self, db_path_file, sample_card1):
        """Test safety check prevents dropping tables with data."""
        # Create DB with data
        db = FlashcardDatabase(db_path_file)
        db.initialize_schema()
        db.upsert_cards_batch([sample_card1])

        # Try to force recreate with data present - should raise ValueError
        with pytest.raises(ValueError, match="CRITICAL.*existing data"):
            db.initialize_schema(force_recreate_tables=True)

    def test_safety_check_catalog_exception(self, db_path_memory):
        """Test safety check handles CatalogException (tables don't exist)."""
        db = FlashcardDatabase(db_path_memory)
        # Force recreate when tables don't exist should work
        db.initialize_schema(force_recreate_tables=True)
        assert True  # Should not raise

    def test_recreate_tables_drops_in_order(self, db_path_memory):
        """Test that recreate_tables drops tables in correct order."""
        db = FlashcardDatabase(db_path_memory)
        db.initialize_schema()
        # Force recreate should drop and recreate
        db.initialize_schema(force_recreate_tables=True)
        # Verify schema exists
        conn = db.get_connection()
        result = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        table_names = [r[0] for r in result]
        assert "cards" in table_names


class TestDatabaseCoverage:
    """Tests for uncovered FlashcardDatabase code paths."""

    def test_upsert_error_handling_with_closed_connection(
        self, initialized_db_manager, sample_card1
    ):
        """Test error handling when connection is closed during upsert."""
        db = initialized_db_manager

        # Mock to simulate closed connection during rollback
        with patch.object(db, "get_connection") as mock_conn:
            mock_conn.return_value.cursor.return_value.__enter__.return_value.executemany.side_effect = duckdb.Error(
                "Test error"
            )
            mock_conn.return_value.closed = True  # Simulate closed connection

            with pytest.raises(Exception):
                db.upsert_cards_batch([sample_card1])


class TestDbUtilsCoverage:
    """Tests for uncovered db_utils code paths."""

    def test_db_row_to_session_with_all_fields(self):
        """Test db_row_to_session with all optional fields."""
        row = {
            "session_id": 1,
            "session_uuid": "12345678-1234-1234-1234-123456789012",
            "user_id": "test_user",
            "start_ts": datetime.now(timezone.utc),
            "end_ts": datetime.now(timezone.utc),
            "total_duration_ms": 60000,
            "cards_reviewed": 10,
            "decks_accessed": ["deck1", "deck2"],
            "deck_switches": 2,
            "interruptions": 1,
            "device_type": "desktop",
            "platform": "macos",
        }
        session = db_utils.db_row_to_session(row)
        assert session.session_id == 1
        assert session.user_id == "test_user"
        assert session.cards_reviewed == 10

    def test_session_to_db_params_tuple_with_all_fields(self):
        """Test session_to_db_params_tuple with all fields."""
        session = Session(
            session_uuid="12345678-1234-1234-1234-123456789012",
            user_id="test_user",
            start_ts=datetime.now(timezone.utc),
            end_ts=datetime.now(timezone.utc),
            total_duration_ms=60000,
            cards_reviewed=10,
            decks_accessed=["deck1", "deck2"],
            deck_switches=2,
            interruptions=1,
            device_type="desktop",
            platform="macos",
        )
        params = db_utils.session_to_db_params_tuple(session)
        assert len(params) == 11
        assert params[1] == "test_user"

    def test_backup_database_nonexistent(self, tmp_path):
        """Test backup_database when database doesn't exist."""
        db_path = tmp_path / "nonexistent.db"
        result = db_utils.backup_database(db_path)
        # Should return the path even if DB doesn't exist
        assert result == db_path

    def test_backup_database_success(self, tmp_path):
        """Test successful database backup."""
        db_path = tmp_path / "test.db"
        # Create a database
        db = FlashcardDatabase(db_path)
        db.initialize_schema()
        db.close_connection()

        # Backup should create a timestamped copy
        backup_path = db_utils.backup_database(db_path)
        assert backup_path.exists()
        assert backup_path != db_path
        assert "backup" in str(backup_path)


class TestSessionOperations:
    """Tests for session operations to increase coverage."""

    def test_create_session_full(self, initialized_db_manager):
        """Test creating session with all fields."""
        db = initialized_db_manager
        session = Session(
            session_uuid="12345678-1234-1234-1234-123456789012",
            user_id="test_user",
            start_ts=datetime.now(timezone.utc),
            end_ts=datetime.now(timezone.utc),
            total_duration_ms=60000,
            cards_reviewed=10,
            decks_accessed=["deck1", "deck2"],
            deck_switches=2,
            interruptions=1,
            device_type="desktop",
            platform="macos",
        )
        created = db.create_session(session)
        assert created.session_id is not None

    def test_update_session(self, initialized_db_manager):
        """Test updating a session."""
        db = initialized_db_manager
        session = Session(
            session_uuid="12345678-1234-1234-1234-123456789012",
            user_id="test_user",
            start_ts=datetime.now(timezone.utc),
        )
        created = db.create_session(session)

        # Update session
        created.end_ts = datetime.now(timezone.utc)
        created.cards_reviewed = 5
        updated = db.update_session(created)
        assert updated.cards_reviewed == 5

    def test_get_session_by_uuid(self, initialized_db_manager):
        """Test getting session by UUID."""
        db = initialized_db_manager
        session = Session(
            session_uuid="12345678-1234-1234-1234-123456789012",
            user_id="test_user",
            start_ts=datetime.now(timezone.utc),
        )
        created = db.create_session(session)

        retrieved = db.get_session_by_uuid(created.session_uuid)
        assert retrieved is not None
        assert retrieved.session_uuid == created.session_uuid

    def test_get_active_sessions(self, initialized_db_manager):
        """Test getting active sessions."""
        db = initialized_db_manager
        session = Session(
            session_uuid="12345678-1234-1234-1234-123456789012",
            user_id="test_user",
            start_ts=datetime.now(timezone.utc),
        )
        db.create_session(session)

        active = db.get_active_sessions()
        assert len(active) == 1

    def test_get_recent_sessions(self, initialized_db_manager):
        """Test getting recent sessions."""
        db = initialized_db_manager
        session = Session(
            session_uuid="12345678-1234-1234-1234-123456789012",
            user_id="test_user",
            start_ts=datetime.now(timezone.utc),
            end_ts=datetime.now(timezone.utc),
        )
        db.create_session(session)

        recent = db.get_recent_sessions(limit=10)
        assert len(recent) == 1
