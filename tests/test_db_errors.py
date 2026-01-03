import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from datetime import date, datetime, timezone
import duckdb

from flashcore.db import FlashcardDatabase
from flashcore.exceptions import (
    DatabaseConnectionError,
    DatabaseError,
    SchemaInitializationError,
    CardOperationError,
    ReviewOperationError,
    MarshallingError,
)
from flashcore.models import Card, CardState, Review
import uuid
from pydantic import ValidationError


@patch('duckdb.connect')
def test_get_connection_raises_custom_error_on_duckdb_error(mock_connect):
    """Tests that get_connection raises DatabaseConnectionError on duckdb.Error."""
    mock_connect.side_effect = duckdb.Error("Connection failed")
    db = FlashcardDatabase(db_path=':memory:')

    with pytest.raises(DatabaseConnectionError, match="Failed to connect to database"):
        db.get_connection()


@patch('flashcore.db.database.duckdb.connect')
def test_initialize_schema_raises_custom_error_on_duckdb_error(mock_duckdb_connect):
    """Tests that initialize_schema raises SchemaInitializationError on duckdb.Error."""
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = duckdb.Error("Schema creation failed")

    mock_connection = MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mock_duckdb_connect.return_value = mock_connection

    db = FlashcardDatabase(db_path=':memory:')

    with pytest.raises(SchemaInitializationError, match="Failed to initialize schema"):
        db.initialize_schema()


@patch('flashcore.db.schema_manager.logger.error')
@patch('flashcore.db.connection.duckdb.connect')
def test_initialize_schema_handles_rollback_error(mock_duckdb_connect, mock_logger_error):
    """
    Tests that initialize_schema logs an error if rollback fails after an initial
    schema creation error.
    """
    # 1. Setup mocks to simulate the double-fault scenario
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = duckdb.Error("Initial schema error")

    mock_connection = MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connection.rollback.side_effect = duckdb.Error("Rollback failed!")
    # Ensure the connection is not seen as 'closed'
    type(mock_connection).closed = PropertyMock(return_value=False)

    mock_duckdb_connect.return_value = mock_connection

    db = FlashcardDatabase(db_path=':memory:')

    # 2. Execute the method and assert the expected exception is raised
    with pytest.raises(SchemaInitializationError, match="Failed to initialize schema: Initial schema error"):
        db.initialize_schema()

    # 3. Verify that the rollback failure was logged
    assert mock_logger_error.call_count == 2
    final_log_call = str(mock_logger_error.call_args_list[1])
    assert "Failed to rollback transaction: Rollback failed!" in final_log_call


def _create_sample_card():
    """Helper function to create a sample card for testing."""
    return Card(
        uuid=uuid.uuid4(),
        deck_name="test_deck",
        front="front",
        back="back",
        added_at=datetime.now(timezone.utc),
        modified_at=datetime.now(timezone.utc),
        state=CardState.New,
    )


@patch('flashcore.db.database.duckdb.connect')
def test_upsert_cards_batch_handles_db_error(mock_duckdb_connect):
    """Tests that upsert_cards_batch handles a database error correctly."""
    mock_cursor = MagicMock()
    mock_cursor.executemany.side_effect = duckdb.Error("Upsert failed")

    mock_connection = MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    type(mock_connection).closed = PropertyMock(return_value=False)  # Ensure rollback is attempted

    mock_duckdb_connect.return_value = mock_connection

    db = FlashcardDatabase(db_path=':memory:')
    card = _create_sample_card()

    with pytest.raises(CardOperationError, match=r"Batch card upsert failed:.*Upsert failed"):
        db.upsert_cards_batch([card])

    mock_connection.rollback.assert_called_once()


@patch('flashcore.db.db_utils.db_row_to_card')
def test_get_card_by_uuid_handles_validation_error(mock_db_row_to_card, in_memory_db_with_data):
    """
    Tests that a CardOperationError is raised if a MarshallingError occurs
    when converting a database row to a Card object.
    """
    db = in_memory_db_with_data
    # Get a valid UUID from the fixture to ensure the DB query runs
    conn = db.get_connection()
    card_uuid_to_fetch = conn.execute("SELECT uuid FROM cards LIMIT 1").fetchone()[0]

    # Configure the mock to simulate a marshalling failure by raising the error
    # that db_row_to_card is expected to raise.
    validation_error = ValidationError.from_exception_data(title="Validation Error", line_errors=[])
    marshalling_error = MarshallingError("Marshalling failed", original_exception=validation_error)
    mock_db_row_to_card.side_effect = marshalling_error

    with pytest.raises(CardOperationError) as excinfo:
        db.get_card_by_uuid(card_uuid_to_fetch)

    # Check that the database method correctly wraps the MarshallingError
    assert f"Failed to parse card with UUID {card_uuid_to_fetch} from database" in str(excinfo.value)
    assert excinfo.value.original_exception is marshalling_error
    mock_db_row_to_card.assert_called_once()


@patch('flashcore.db.database.duckdb.connect')
def test_get_all_cards_handles_db_error(mock_duckdb_connect):
    """Tests that get_all_cards raises CardOperationError on a database error."""
    # 1. Setup mocks to raise an error on execute
    mock_connection = MagicMock()
    mock_connection.execute.side_effect = duckdb.Error("DB query failed")
    mock_duckdb_connect.return_value = mock_connection

    db = FlashcardDatabase(db_path=':memory:')

    # 2. Execute and assert
    with pytest.raises(CardOperationError, match="Failed to get all cards: DB query failed"):
        db.get_all_cards()


@patch('flashcore.db.database.duckdb.connect')
def test_get_due_card_count_handles_db_error(mock_duckdb_connect):
    """Tests that get_due_card_count raises CardOperationError on a database error."""
    # 1. Setup mocks to raise an error on execute
    mock_connection = MagicMock()
    mock_connection.execute.side_effect = duckdb.Error("DB count failed")
    mock_duckdb_connect.return_value = mock_connection

    db = FlashcardDatabase(db_path=':memory:')

    # 2. Execute and assert
    with pytest.raises(CardOperationError, match="Failed to count due cards: DB count failed"):
        db.get_due_card_count(deck_name="any_deck", on_date=datetime.now(timezone.utc).date())


@patch('flashcore.db.database.duckdb.connect')
def test_delete_cards_by_uuids_batch_handles_db_error(mock_duckdb_connect):
    """Tests that delete_cards_by_uuids_batch handles a database error and rolls back."""
    # 1. Setup mocks
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = duckdb.Error("Delete failed")

    mock_connection = MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    type(mock_connection).closed = PropertyMock(return_value=False)  # Ensure rollback is attempted

    mock_duckdb_connect.return_value = mock_connection

    db = FlashcardDatabase(db_path=':memory:')
    test_uuid = uuid.uuid4()

    # 2. Execute and assert
    with pytest.raises(CardOperationError, match="Batch card delete failed: Delete failed"):
        db.delete_cards_by_uuids_batch([test_uuid])

    # 3. Verify rollback was called
    mock_connection.rollback.assert_called_once()


@patch('flashcore.db.database.duckdb.connect')
def test_upsert_cards_batch_handles_rollback_error(mock_duckdb_connect, caplog):
    """Tests that a rollback failure after an upsert error is handled and logged."""
    # 1. Setup mocks to fail on both executemany and rollback
    mock_cursor = MagicMock()
    mock_cursor.executemany.side_effect = duckdb.Error("Upsert failed")

    mock_connection = MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connection.rollback.side_effect = duckdb.Error("Rollback failed")
    # Set 'closed' to False to ensure the `if conn and not conn.closed:` check passes
    mock_connection.closed = False

    mock_duckdb_connect.return_value = mock_connection

    db = FlashcardDatabase(db_path=':memory:')
    sample_card = _create_sample_card()

    # 2. Execute and assert the final exception is still raised
    with pytest.raises(CardOperationError, match="Batch card upsert failed"):
        db.upsert_cards_batch([sample_card])

    # 3. Verify the fatal rollback error was logged
    assert "Failed to rollback transaction during upsert error" in caplog.text





@patch('flashcore.db.database.duckdb.connect')
def test_get_card_by_uuid_handles_db_error(mock_duckdb_connect):
    """Tests that get_card_by_uuid handles a database error."""
    # 1. Setup mock to raise an error on execute
    mock_connection = MagicMock()
    mock_connection.execute.side_effect = duckdb.Error("DB query failed")
    mock_duckdb_connect.return_value = mock_connection

    db = FlashcardDatabase(db_path=':memory:')
    sample_uuid = uuid.uuid4()

    # 2. Execute and assert that the error is caught and re-raised correctly
    with pytest.raises(CardOperationError, match="Failed to fetch card by UUID"):
        db.get_card_by_uuid(sample_uuid)


@patch('flashcore.db.database.duckdb.connect')
def test_get_due_cards_handles_db_error(mock_duckdb_connect):
    """Tests that get_due_cards handles a database error."""
    # 1. Setup mock to raise an error on execute
    mock_connection = MagicMock()
    mock_connection.execute.side_effect = duckdb.Error("DB query failed for due cards")
    mock_duckdb_connect.return_value = mock_connection

    db = FlashcardDatabase(db_path=':memory:')

    # 2. Execute and assert that the error is caught and re-raised correctly
    with pytest.raises(CardOperationError, match="Failed to fetch due cards"):
        db.get_due_cards(deck_name="some_deck", on_date=date.today())


@patch('flashcore.db.database.duckdb.connect')
def test_add_review_and_update_card_handles_db_error(mock_duckdb_connect):
    """Tests that add_review_and_update_card handles a database error during a transaction."""
    # 1. Setup mock cursor to raise an error, simulating a transaction failure
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = duckdb.Error("DB query failed during transaction")

    mock_connection = MagicMock()
    # This setup mocks the 'with conn.cursor() as cursor:' context manager
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mock_duckdb_connect.return_value = mock_connection

    db = FlashcardDatabase(db_path=':memory:')

    # 2. Create sample data
    card_uuid = uuid.uuid4()
    sample_review = Review(
        card_uuid=card_uuid,
        ts=datetime.now(timezone.utc),
        rating=3,
        stab_after=1.0,
        diff=1.0,
        next_due=date.today(),
        elapsed_days_at_review=0,
        scheduled_days_interval=1,
    )
    sample_card = Card(
        uuid=card_uuid,
        deck_name="test_deck",
        front="front",
        back="back",
        added_at=datetime.now(timezone.utc),
        modified_at=datetime.now(timezone.utc),
        state=CardState.New,
    )

    # 3. Execute and assert that the error is caught and re-raised correctly
    with pytest.raises(DatabaseError, match="Failed to add review and update card"):
        db.add_review_and_update_card(sample_review, sample_card)


@patch('flashcore.db.database.duckdb.connect')
def test_get_reviews_for_card_handles_db_error(mock_duckdb_connect):
    """Tests that get_reviews_for_card handles a database error."""
    # 1. Setup mock to raise an error on execute
    mock_connection = MagicMock()
    mock_connection.execute.side_effect = duckdb.Error("DB query failed for reviews")
    mock_duckdb_connect.return_value = mock_connection

    db = FlashcardDatabase(db_path=':memory:')
    sample_uuid = uuid.uuid4()

    # 2. Execute and assert that the error is caught and re-raised correctly
    with pytest.raises(ReviewOperationError, match="Failed to get reviews for card"):
        db.get_reviews_for_card(sample_uuid)


@patch('flashcore.db.database.duckdb.connect')
def test_add_review_and_update_card_handles_missing_return_id(mock_duckdb_connect):
    """Tests that add_review_and_update_card handles failure to retrieve review_id."""
    # 1. Setup mock to simulate INSERT not returning an ID
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_connection = MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connection.closed = False  # Simulate an open connection so rollback is attempted
    mock_duckdb_connect.return_value = mock_connection

    db = FlashcardDatabase(db_path=':memory:')
    sample_review = Review(
        card_uuid=uuid.uuid4(),
        ts=datetime.now(timezone.utc),
        rating=3, stab_after=10.0, diff=5.0, next_due=date.today(),
        elapsed_days_at_review=0, scheduled_days_interval=10
    )

    # 2. Execute and assert the correct error is raised
    with pytest.raises(ReviewOperationError, match="Failed to retrieve review_id after insertion."):
        db.add_review_and_update_card(sample_review, CardState.Review)

    # 3. Verify transaction was rolled back
    mock_cursor.begin.assert_called_once()
    mock_connection.rollback.assert_called_once()
    mock_cursor.commit.assert_not_called()


def test_delete_cards_by_uuids_batch_with_empty_list():
    """Tests that calling delete with an empty list returns 0 immediately."""
    db = FlashcardDatabase(db_path=':memory:')
    # Mock get_connection to ensure it's not called
    with patch.object(db, 'get_connection') as mock_get_conn:
        result = db.delete_cards_by_uuids_batch([])
        assert result == 0
        mock_get_conn.assert_not_called()


def test_add_review_and_update_card_read_only_mode_raises_error():
    """
    Tests that calling add_review_and_update_card in read-only mode raises an error.
    """
    db = FlashcardDatabase(db_path='test.db', read_only=True)

    # Create a valid review object with all required fields
    card_uuid = uuid.uuid4()
    review = Review(
        card_uuid=card_uuid,
        rating=1,
        stab_after=2.5,
        diff=0.5,
        next_due=date.today(),
        elapsed_days_at_review=0,
        scheduled_days_interval=4
    )
    # The method expects a CardState enum for the new state
    new_card_state = CardState.Learning

    with pytest.raises(DatabaseConnectionError, match="Cannot add review in read-only mode"):
        db.add_review_and_update_card(review, new_card_state)


@patch('flashcore.db.database.FlashcardDatabase._insert_review_and_get_id', side_effect=ValueError("Internal processing error"))
def test_add_review_and_update_card_handles_generic_exception(mock_insert_review):
    """
    Tests that a generic exception during the transaction is caught, rolled back,
    and wrapped in a ReviewOperationError. This covers the general exception handling
    path in add_review_and_update_card.
    """
    db = FlashcardDatabase(db_path=':memory:')
    db.initialize_schema()
    
    card_uuid = uuid.uuid4()
    # Create a dummy card and review to pass to the method
    card = Card(uuid=card_uuid, deck_name="test", front="f", back="b")
    db.upsert_cards_batch([card])
    review = Review(
        card_uuid=card.uuid,
        ts=datetime.now(timezone.utc),
        rating=3,
        stab_after=2.5,
        diff=0.5,
        next_due=date.today(),
        elapsed_days_at_review=0,
        scheduled_days_interval=4
    )
    new_card_state = Card(uuid=card.uuid, deck_name="test", front="f", back="b", state=CardState.Learning)

    with pytest.raises(ReviewOperationError) as excinfo:
        db.add_review_and_update_card(review, new_card_state)

    assert "Failed to add review and update card" in str(excinfo.value)
    assert isinstance(excinfo.value.original_exception, ValueError)
    assert "Internal processing error" in str(excinfo.value.original_exception)
    mock_insert_review.assert_called_once()


@patch('flashcore.db.database.FlashcardDatabase._insert_review_and_get_id', side_effect=CardOperationError("Underlying DB issue"))
def test_add_review_and_update_card_reraises_database_error(mock_insert_review):
    """
    Tests that if a DatabaseError subclass is raised during the transaction,
    it is caught, rolled back, and re-raised without being wrapped. This covers
    the `if isinstance(e, DatabaseError)` path.
    """
    db = FlashcardDatabase(db_path=':memory:')
    db.initialize_schema()
    
    card_uuid = uuid.uuid4()
    card = Card(uuid=card_uuid, deck_name="test", front="f", back="b")
    db.upsert_cards_batch([card])
    review = Review(
        card_uuid=card.uuid,
        ts=datetime.now(timezone.utc),
        rating=3,
        stab_after=2.5,
        diff=0.5,
        next_due=date.today(),
        elapsed_days_at_review=0,
        scheduled_days_interval=4
    )
    new_card_state = Card(uuid=card.uuid, deck_name="test", front="f", back="b", state=CardState.Learning)

    with pytest.raises(CardOperationError, match="Underlying DB issue"):
        db.add_review_and_update_card(review, new_card_state)

    mock_insert_review.assert_called_once()


def test_delete_cards_by_uuids_batch_in_read_only_mode(tmp_path):
    """Tests that deleting in read-only mode raises a CardOperationError."""
    db_path = tmp_path / "test.db"

    # Create the database file by connecting in write mode to initialize it.
    with FlashcardDatabase(db_path=db_path) as db_write:
        db_write.initialize_schema()

    # Now, connect to the existing database in read-only mode.
    db_read = FlashcardDatabase(db_path=db_path, read_only=True)
    with pytest.raises(CardOperationError, match="Cannot delete cards in read-only mode."):
        db_read.delete_cards_by_uuids_batch([uuid.uuid4()])
    db_read.close_connection()


@patch('flashcore.db.database.duckdb.connect')
def test_get_all_card_fronts_and_uuids_handles_db_error(mock_duckdb_connect):
    """Tests that get_all_card_fronts_and_uuids handles a database error."""
    # 1. Setup mocks to raise an error on cursor.execute(), based on the actual source code.
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = duckdb.Error("DB execute failed")

    mock_connection = MagicMock()
    # This correctly mocks the 'with conn.cursor() as cursor:' pattern
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mock_duckdb_connect.return_value = mock_connection

    db = FlashcardDatabase(db_path=':memory:')

    # 2. Execute and assert that the error is caught and re-raised correctly
    with pytest.raises(CardOperationError, match="Could not fetch card fronts and UUIDs."):
        db.get_all_card_fronts_and_uuids()


@patch('flashcore.db.db_utils.db_row_to_card')
def test_get_all_cards_handles_validation_error(mock_db_row_to_card, in_memory_db_with_data):
    """
    Tests that a CardOperationError is raised when card data from the database
    fails Pydantic validation, checking for the new exception chaining.
    """
    db = in_memory_db_with_data

    # Configure the mock to simulate a marshalling failure
    validation_error = ValidationError.from_exception_data(title="Validation Error", line_errors=[])
    marshalling_error = MarshallingError("Marshalling failed", original_exception=validation_error)
    mock_db_row_to_card.side_effect = marshalling_error

    with pytest.raises(CardOperationError) as excinfo:
        db.get_all_cards()

    # Verify the exception chain is CardOperationError -> MarshallingError -> ValidationError
    assert "Failed to parse cards from database." in str(excinfo.value)
    assert isinstance(excinfo.value.original_exception, MarshallingError)
    assert isinstance(excinfo.value.original_exception.original_exception, ValidationError)
    mock_db_row_to_card.assert_called()


@patch('flashcore.db.db_utils.db_row_to_card')
def test_get_due_cards_handles_validation_error(mock_db_row_to_card, in_memory_db_with_data):
    """
    Tests that a CardOperationError is raised when due card data from the database
    fails Pydantic validation, checking for the new exception chaining.
    """
    db = in_memory_db_with_data

    # Configure the mock to simulate a marshalling failure by raising the error
    # that db_row_to_card is expected to raise.
    validation_error = ValidationError.from_exception_data(title="Validation Error", line_errors=[])
    marshalling_error = MarshallingError("Marshalling failed", original_exception=validation_error)
    mock_db_row_to_card.side_effect = marshalling_error

    with pytest.raises(CardOperationError) as excinfo:
        db.get_due_cards(deck_name="test-deck", on_date=date.today())

    # Verify the exception chain is CardOperationError -> MarshallingError -> ValidationError
    assert "Failed to parse due cards for deck 'test-deck' from database." in str(excinfo.value)
    assert isinstance(excinfo.value.original_exception, MarshallingError)
    assert isinstance(excinfo.value.original_exception.original_exception, ValidationError)
    mock_db_row_to_card.assert_called_once()


def test_get_card_with_invalid_tag_data_raises_error():
    """
    Tests that a CardOperationError is raised when retrieving a card with data
    that fails Pydantic validation (e.g., an invalid tag format).
    This test uses a real in-memory database to ensure the data-to-model pipeline.
    """
    db = FlashcardDatabase(db_path=':memory:')
    db.initialize_schema()
    conn = db.get_connection()

    card_uuid = uuid.uuid4()
    invalid_tag = 'Invalid_Tag'  # This violates the kebab-case validator

    # Manually insert a row with data that will fail Pydantic validation
    conn.execute(
        """INSERT INTO cards (uuid, deck_name, front, back, tags, added_at, modified_at, state)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            card_uuid,
            'test-deck',
            'front',
            'back',
            [invalid_tag],
            datetime.now(timezone.utc),
            datetime.now(timezone.utc),
            'New',
        ]
    )

    with pytest.raises(CardOperationError) as excinfo:
        db.get_card_by_uuid(card_uuid)

    # Verify the exception chain is CardOperationError -> MarshallingError -> ValidationError
    assert f"Failed to parse card with UUID {card_uuid} from database" in str(excinfo.value)
    assert isinstance(excinfo.value.original_exception, MarshallingError)
    assert isinstance(excinfo.value.original_exception.original_exception, ValidationError)

    # Verify the root cause is the Pydantic validation error
    root_cause = excinfo.value.original_exception.original_exception
    assert isinstance(root_cause, ValidationError)
    assert f"Tag '{invalid_tag}' is not in kebab-case" in str(root_cause)


@patch('flashcore.db.database.duckdb.connect')
def test_add_review_and_update_card_handles_rollback_error(mock_duckdb_connect, caplog):
    """Tests that a rollback failure after a review/update error is logged."""
    # 1. Setup mocks to fail on both the main operation and the rollback
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = duckdb.Error("Review insert failed")

    mock_connection = MagicMock()
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connection.rollback.side_effect = duckdb.Error("Rollback failed miserably")
    mock_connection.closed = False  # Ensure rollback is attempted

    mock_duckdb_connect.return_value = mock_connection

    db = FlashcardDatabase(db_path=':memory:')
    sample_review = Review(
        card_uuid=uuid.uuid4(),
        ts=datetime.now(timezone.utc),
        rating=3, stab_after=10.0, diff=5.0, next_due=date.today(),
        elapsed_days_at_review=0, scheduled_days_interval=10
    )

    # 2. Execute and assert the original error is raised
    with pytest.raises(ReviewOperationError, match="Failed to add review and update card: Review insert failed"):
        db.add_review_and_update_card(sample_review, CardState.Review)

    # 3. Verify the fatal rollback error was logged
    assert "Failed to rollback transaction: Rollback failed miserably" in caplog.text
