"""
Comprehensive test suite for flashcore.database (FlashcardDatabase), covering connection, schema, CRUD, constraints, marshalling, and error handling.
"""

import pytest

import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Generator

import duckdb

from flashcore.models import Card, Review, CardState
from flashcore.db import FlashcardDatabase
from flashcore.exceptions import (
    CardOperationError,
    DatabaseConnectionError,
    ReviewOperationError,
    SchemaInitializationError,
)


# --- Fixtures ---
@pytest.fixture
def db_path_memory() -> str:
    return ":memory:"


@pytest.fixture
def db_path_file(tmp_path: Path) -> Path:
    return tmp_path / "test_flash.db"


@pytest.fixture(params=["memory", "file"])
def db_manager(
    request, db_path_memory: str, db_path_file: Path
) -> Generator[FlashcardDatabase, None, None]:
    if request.param == "memory":
        db_man = FlashcardDatabase(db_path_memory)
    else:
        db_man = FlashcardDatabase(db_path_file)
    try:
        yield db_man
    finally:
        db_man.close_connection()
        if request.param == "file" and db_path_file.exists():
            try:
                db_path_file.unlink()
            except Exception as e:
                print(
                    f"Error removing temporary DB file in test fixture teardown: {e}"
                )


@pytest.fixture
def initialized_db_manager(db_manager: FlashcardDatabase) -> FlashcardDatabase:
    db_manager.initialize_schema()
    return db_manager


@pytest.fixture
def sample_card1() -> Card:
    return Card(
        uuid=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        deck_name="Deck A::Sub1",
        front="Card 1 Front",
        back="Card 1 Back",
        tags={"tag1", "common-tag"},
        added_at=datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
        source_yaml_file=Path("source/deck_a.yaml"),
    )


@pytest.fixture
def sample_card2() -> Card:
    return Card(
        uuid=uuid.UUID("22222222-2222-2222-2222-222222222222"),
        deck_name="Deck A::Sub2",
        front="Card 2 Front",
        back="Card 2 Back",
        tags={"tag2", "common-tag"},
        added_at=datetime(2023, 1, 2, 10, 0, 0, tzinfo=timezone.utc),
        source_yaml_file=Path("source/deck_a.yaml"),
    )


@pytest.fixture
def sample_card3_deck_b() -> Card:
    return Card(
        uuid=uuid.UUID("33333333-3333-3333-3333-333333333333"),
        deck_name="Deck B",
        front="Card 3 DeckB Front",
        back="Card 3 DeckB Back",
        tags={"tag3"},
        added_at=datetime(2023, 1, 3, 10, 0, 0, tzinfo=timezone.utc),
        source_yaml_file=Path("source/deck_b.yaml"),
    )


@pytest.fixture
def sample_review1(sample_card1: Card) -> Review:
    return Review(
        card_uuid=sample_card1.uuid,
        ts=datetime(2023, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        rating=3,
        stab_before=1.0,
        stab_after=2.5,
        diff=5.0,
        next_due=date(2023, 1, 8),
        elapsed_days_at_review=0,
        scheduled_days_interval=3,
    )


@pytest.fixture
def sample_review2_for_card1(sample_card1: Card) -> Review:
    return Review(
        card_uuid=sample_card1.uuid,
        ts=datetime(2023, 1, 8, 13, 0, 0, tzinfo=timezone.utc),
        rating=2,
        stab_before=2.5,
        stab_after=6.0,
        diff=4.8,
        next_due=date(2023, 1, 14),
        elapsed_days_at_review=3,
        scheduled_days_interval=6,
    )


# --- Sample Data Generators ---


def create_sample_card(**overrides) -> Card:
    data = dict(
        uuid=uuid.uuid4(),
        deck_name="Deck A::Sub1",
        front="Sample Front",
        back="Sample Back",
        tags={"tag1", "tag2"},
        added_at=datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
        source_yaml_file=Path("source/deck_a.yaml"),
        origin_task="test-task",
        media=[Path("media1.png"), Path("media2.mp3")],
        internal_note="test note",
    )
    data.update(overrides)
    return Card(**data)


def create_sample_review(
    card_uuid, bypass_validation: bool = False, **overrides
) -> Review:
    data = dict(
        card_uuid=card_uuid,
        ts=datetime(2023, 1, 2, 11, 0, 0, tzinfo=timezone.utc),
        rating=2,
        stab_before=1.0,
        stab_after=2.0,
        diff=4.0,
        next_due=date(2023, 1, 5),
        elapsed_days_at_review=0,
        scheduled_days_interval=3,
        resp_ms=1234,
        review_type="learn",
    )
    data.update(overrides)
    if bypass_validation:
        return Review.model_construct(**data)
    return Review(**data)


# --- Test Classes ---


class TestFlashcardDatabaseConnection:
    def test_instantiation_requires_db_path(self):
        # This test verifies that FlashcardDatabase() requires db_path parameter
        with pytest.raises(
            TypeError,
            match="missing 1 required positional argument: 'db_path'",
        ):
            FlashcardDatabase()  # No path provided - should raise TypeError

    def test_instantiation_custom_file_path(self, tmp_path: Path):
        custom_path = tmp_path / "custom_dir" / "my_flash.db"
        db_man = FlashcardDatabase(custom_path)
        assert db_man.db_path_resolved == custom_path.resolve()
        conn = None
        try:
            conn = db_man.get_connection()
            assert custom_path.parent.exists()
        finally:
            if conn:
                conn.close()

    def test_instantiation_in_memory(self, db_path_memory: str):
        db_man = FlashcardDatabase(db_path_memory)
        assert str(db_man.db_path_resolved) == ":memory:"
        with db_man as db:
            conn = db.get_connection()
            assert conn is not None
            conn.execute("SELECT 42;").fetchone()
        # The connection object obtained within the context should now be closed.
        with pytest.raises(duckdb.Error, match="Connection already closed"):
            conn.execute("SELECT 1")

    def test_get_connection_success(self, db_manager: FlashcardDatabase):
        conn = db_manager.get_connection()
        assert conn is not None

    def test_get_connection_idempotent(self, db_manager: FlashcardDatabase):
        conn1 = db_manager.get_connection()
        conn2 = db_manager.get_connection()
        assert conn1 is conn2
        db_manager.close_connection()
        # The original connection object should be closed and raise an error on use.
        with pytest.raises(duckdb.Error, match="Connection already closed"):
            conn1.execute("SELECT 1")
        conn3 = db_manager.get_connection()
        assert conn3 is not None
        # Further check: new connection is usable
        conn3.execute("SELECT 1")
        assert conn1 is not conn3

    def test_close_connection(self, db_manager: FlashcardDatabase):
        conn1 = db_manager.get_connection()  # Ensure connection is established
        db_manager.close_connection()
        # The connection object should be closed and raise an error on use.
        with pytest.raises(duckdb.Error, match="Connection already closed"):
            conn1.execute("SELECT 1")
        # Should be able to reconnect
        conn2 = db_manager.get_connection()
        assert conn2 is not None
        assert conn1 is not conn2

    def test_context_manager_usage(self, db_path_file: Path):
        db = FlashcardDatabase(db_path_file)
        with db as open_db:
            conn = open_db.get_connection()
            assert conn is not None
        # The connection obtained within the context should now be closed.
        with pytest.raises(duckdb.Error, match="Connection already closed"):
            conn.execute("SELECT 1")

    def test_read_only_mode_connection(self, db_path_file: Path):
        db_man = FlashcardDatabase(db_path_file)
        db_man.initialize_schema()
        db_man.close_connection()
        db_readonly = FlashcardDatabase(db_path_file, read_only=True)
        conn = db_readonly.get_connection()
        assert conn is not None
        # Attempt write
        with pytest.raises(
            CardOperationError, match=r"Batch card upsert failed:.*read-only"
        ):
            db_readonly.upsert_cards_batch([create_sample_card()])


class TestSchemaInitialization:
    def test_initialize_schema_creates_tables_and_sequence(
        self, db_manager: FlashcardDatabase
    ):
        db_manager.initialize_schema()
        conn = db_manager.get_connection()
        tables = conn.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_name IN ('cards', 'reviews');"
        ).fetchall()
        table_names = {name[0] for name in tables}
        assert "cards" in table_names
        assert "reviews" in table_names
        seq = conn.execute(
            "SELECT sequence_name FROM duckdb_sequences() WHERE sequence_name='review_seq';"
        ).fetchone()
        assert seq is not None

    def test_initialize_schema_idempotent(
        self, db_manager: FlashcardDatabase, sample_card1: Card
    ):
        with db_manager:
            db_manager.initialize_schema()
            db_manager.upsert_cards_batch([sample_card1])
            db_manager.initialize_schema()
            retrieved_card = db_manager.get_card_by_uuid(sample_card1.uuid)
        assert retrieved_card is not None
        assert retrieved_card.added_at == sample_card1.added_at
        assert retrieved_card.modified_at >= sample_card1.modified_at

    def test_initialize_schema_force_recreate(
        self, db_path_file: Path, sample_card1: Card
    ):
        from cultivation.scripts.flashcore import config

        original_settings = config.settings
        # Directly instantiate settings with testing_mode=True to bypass caching issues.
        config.settings = config.Settings(testing_mode=True)

        db_manager = FlashcardDatabase(db_path_file)

        try:
            with db_manager:
                db_manager.initialize_schema()
                db_manager.upsert_cards_batch([sample_card1])
                assert (
                    db_manager.get_card_by_uuid(sample_card1.uuid) is not None
                )
                db_manager.initialize_schema(force_recreate_tables=True)
                assert db_manager.get_card_by_uuid(sample_card1.uuid) is None
        finally:
            # Restore original settings to avoid side-effects
            config.settings = original_settings

    def test_initialize_schema_on_readonly_db_fails_for_force_recreate(
        self, db_path_file: Path
    ):
        db_man = FlashcardDatabase(db_path_file)
        db_man.initialize_schema()
        db_man.close_connection()
        db_readonly = FlashcardDatabase(db_path_file, read_only=True)
        with pytest.raises(DatabaseConnectionError):
            db_readonly.initialize_schema(force_recreate_tables=True)

    def test_schema_constraints_rating(
        self, initialized_db_manager: FlashcardDatabase, sample_card1: Card
    ):
        db = initialized_db_manager
        db.upsert_cards_batch([sample_card1])

        # Bypass Pydantic validation to test the database CHECK constraint directly.
        conn = db.get_connection()
        with pytest.raises(duckdb.ConstraintException) as excinfo:
            # Manually construct and execute a raw SQL INSERT
            ts = datetime(2023, 1, 2, 11, 0, 0, tzinfo=timezone.utc)
            conn.execute(
                "INSERT INTO reviews (card_uuid, ts, rating, stab_before, stab_after, diff, next_due, elapsed_days_at_review, scheduled_days_interval, resp_ms, review_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    str(sample_card1.uuid),
                    ts,
                    5,  # Invalid rating
                    1.0,
                    2.0,
                    4.0,
                    date(2023, 1, 5),
                    0,
                    3,
                    1234,
                    "learn",
                ),
            )
        assert "CHECK constraint failed" in str(excinfo.value)
        # The failed transaction should be rolled back, so no reviews should exist.
        assert len(db.get_reviews_for_card(sample_card1.uuid)) == 0


class TestCardOperations:
    def test_upsert_cards_batch_insert_new(
        self,
        initialized_db_manager: FlashcardDatabase,
        sample_card1: Card,
        sample_card2: Card,
    ):
        db = initialized_db_manager
        cards_to_insert = [sample_card1, sample_card2]
        affected_rows = db.upsert_cards_batch(cards_to_insert)
        assert affected_rows == 2
        assert db.get_card_by_uuid(sample_card1.uuid) is not None
        assert db.get_card_by_uuid(sample_card2.uuid) is not None
        retrieved_c1 = db.get_card_by_uuid(sample_card1.uuid)
        assert retrieved_c1.added_at == sample_card1.added_at

    def test_upsert_cards_batch_update_existing(
        self, initialized_db_manager: FlashcardDatabase, sample_card1: Card
    ):
        db = initialized_db_manager
        db.upsert_cards_batch([sample_card1])
        retrieved_card = db.get_card_by_uuid(sample_card1.uuid)
        assert retrieved_card is not None
        original_added_at = retrieved_card.added_at
        updated_card1 = sample_card1.model_copy(
            update={"front": "Updated Card 1 Front", "tags": {"new-tag"}}
        )
        affected_rows = db.upsert_cards_batch([updated_card1])
        assert affected_rows == 1
        retrieved_updated_card = db.get_card_by_uuid(sample_card1.uuid)
        assert retrieved_updated_card is not None
        assert retrieved_updated_card.front == "Updated Card 1 Front"
        assert retrieved_updated_card.tags == {"new-tag"}
        assert retrieved_updated_card.added_at == original_added_at

    def test_upsert_cards_batch_mixed_insert_update(
        self,
        initialized_db_manager: FlashcardDatabase,
        sample_card1: Card,
        sample_card2: Card,
    ):
        db = initialized_db_manager
        db.upsert_cards_batch([sample_card1])  # Re-indenting this line
        updated_card1 = sample_card1.model_copy(
            update={"front": "Mixed Updated", "tags": {"mixed"}}
        )
        new_card = create_sample_card()
        affected = db.upsert_cards_batch(
            [updated_card1, new_card, sample_card2]
        )
        assert affected == 3
        retrieved_updated_card1 = db.get_card_by_uuid(updated_card1.uuid)
        assert retrieved_updated_card1 is not None
        assert retrieved_updated_card1.front == "Mixed Updated"
        assert db.get_card_by_uuid(new_card.uuid) is not None
        assert db.get_card_by_uuid(sample_card2.uuid) is not None

    def test_upsert_cards_batch_empty_list(
        self, initialized_db_manager: FlashcardDatabase
    ):
        affected_count = initialized_db_manager.upsert_cards_batch([])
        assert affected_count == 0

    def test_upsert_cards_batch_data_marshalling(
        self, initialized_db_manager: FlashcardDatabase
    ):
        db = initialized_db_manager
        card = create_sample_card(
            tags={"tag-x"},
            media=[Path("foo.png")],
            source_yaml_file=Path("foo.yaml"),
        )
        affected_rows = db.upsert_cards_batch([card])
        assert affected_rows == 1
        retrieved = db.get_card_by_uuid(card.uuid)
        assert retrieved is not None
        assert isinstance(retrieved.tags, set) and "tag-x" in retrieved.tags
        assert (
            isinstance(retrieved.media, list)
            and Path("foo.png") in retrieved.media
        )
        assert (
            isinstance(retrieved.source_yaml_file, Path)
            and retrieved.source_yaml_file.name == "foo.yaml"
        )

    def test_upsert_cards_batch_transaction_rollback(
        self, db_manager: FlashcardDatabase
    ):
        db = db_manager
        db.initialize_schema()
        valid_card = create_sample_card()
        # Create a card with an invalid deck_name by bypassing Pydantic validation.
        # This allows us to test the database-level NOT NULL constraint.
        broken_card_data = create_sample_card().model_dump()
        broken_card_data["deck_name"] = None
        broken_card_data["uuid"] = uuid.uuid4()  # Ensure it has a unique UUID
        broken_card = Card.model_construct(**broken_card_data)
        with pytest.raises(CardOperationError):
            db.upsert_cards_batch([valid_card, broken_card])
        assert db.get_card_by_uuid(valid_card.uuid) is None

    def test_get_card_by_uuid_exists(
        self, initialized_db_manager: FlashcardDatabase, sample_card1: Card
    ):
        db = initialized_db_manager
        db.upsert_cards_batch([sample_card1])
        card = db.get_card_by_uuid(sample_card1.uuid)
        assert card is not None
        assert card.uuid == sample_card1.uuid

    def test_get_card_by_uuid_not_exists(
        self, initialized_db_manager: FlashcardDatabase
    ):
        assert initialized_db_manager.get_card_by_uuid(uuid.uuid4()) is None

    def test_get_card_by_uuid_not_exists_when_other_cards_present(
        self, initialized_db_manager: FlashcardDatabase, sample_card1: Card
    ):
        """Ensures get_card_by_uuid returns None for a non-existent UUID even when the DB is not empty."""
        db = initialized_db_manager
        db.upsert_cards_batch([sample_card1])

        non_existent_uuid = uuid.UUID("00000000-0000-0000-0000-000000000000")
        assert non_existent_uuid != sample_card1.uuid

        retrieved_card = db.get_card_by_uuid(non_existent_uuid)
        assert retrieved_card is None

    def test_get_all_cards_empty_db(
        self, initialized_db_manager: FlashcardDatabase
    ):
        assert initialized_db_manager.get_all_cards() == []

    def test_get_all_cards_multiple_cards(
        self,
        initialized_db_manager: FlashcardDatabase,
        sample_card1: Card,
        sample_card2: Card,
    ):
        db = initialized_db_manager
        db.upsert_cards_batch([sample_card1, sample_card2])
        cards = db.get_all_cards()
        assert len(cards) == 2
        uuids = {c.uuid for c in cards}
        assert sample_card1.uuid in uuids
        assert sample_card2.uuid in uuids

    def test_get_all_cards_with_deck_filter(
        self,
        initialized_db_manager: FlashcardDatabase,
        sample_card1: Card,
        sample_card2: Card,
        sample_card3_deck_b: Card,
    ):
        db = initialized_db_manager
        db.upsert_cards_batch(
            [sample_card1, sample_card2, sample_card3_deck_b]
        )
        deck_a_cards = db.get_all_cards(deck_name_filter="Deck A::%")
        assert len(deck_a_cards) == 2
        uuids = {c.uuid for c in deck_a_cards}
        assert sample_card1.uuid in uuids
        assert sample_card2.uuid in uuids
        deck_b_cards = db.get_all_cards(deck_name_filter="Deck B")
        assert len(deck_b_cards) == 1
        assert sample_card3_deck_b.uuid == deck_b_cards[0].uuid

    def test_get_due_cards_logic(
        self,
        initialized_db_manager: FlashcardDatabase,
        sample_card1: Card,
        sample_card2: Card,
    ):
        db = initialized_db_manager
        now = datetime.now(timezone.utc)
        # Card 1: Due yesterday, should be fetched
        review1 = create_sample_review(
            card_uuid=sample_card1.uuid,
            ts=now - timedelta(days=10),
            next_due=(now - timedelta(days=1)).date(),
        )
        # Card 2: Due tomorrow, should NOT be fetched
        review2 = create_sample_review(
            card_uuid=sample_card2.uuid,
            ts=now,
            next_due=(now + timedelta(days=1)).date(),
        )
        db.upsert_cards_batch([sample_card1, sample_card2])
        db.add_review_and_update_card(review1, CardState.Review)
        db.add_review_and_update_card(review2, CardState.Review)
        due_cards = db.get_due_cards(
            deck_name=sample_card1.deck_name, on_date=now.date()
        )
        assert len(due_cards) == 1
        assert due_cards[0].uuid == sample_card1.uuid
        # Test with limit
        due_cards_limit = db.get_due_cards(
            deck_name=sample_card1.deck_name, on_date=now.date(), limit=0
        )
        assert len(due_cards_limit) == 0
        assert db.get_card_by_uuid(sample_card1.uuid) is not None
        assert len(db.get_reviews_for_card(sample_card1.uuid)) == 1

    def test_delete_cards_by_uuids_batch_non_existent(
        self, initialized_db_manager: FlashcardDatabase
    ):
        affected = initialized_db_manager.delete_cards_by_uuids_batch(
            [uuid.uuid4()]
        )
        assert affected == 0

    def test_get_all_card_fronts_and_uuids(
        self, initialized_db_manager: FlashcardDatabase, sample_card1: Card
    ):
        db = initialized_db_manager
        # Card with different case and whitespace
        card_variant = create_sample_card(front="  Card 1 FRONT  ")
        db.upsert_cards_batch([sample_card1, card_variant])
        front_map = db.get_all_card_fronts_and_uuids()
        # The function should normalize and deduplicate, returning the UUID of the first-inserted card.
        assert len(front_map) == 1
        normalized_front = " ".join(sample_card1.front.lower().split())
        assert normalized_front in front_map
        assert front_map[normalized_front] == sample_card1.uuid


class TestReviewOperations:
    def test_add_review_success(
        self, initialized_db_manager: FlashcardDatabase, sample_card1: Card
    ):
        db = initialized_db_manager
        db.upsert_cards_batch([sample_card1])
        review = create_sample_review(card_uuid=sample_card1.uuid)
        db.add_review_and_update_card(review, CardState.Review)
        retrieved_reviews = db.get_reviews_for_card(sample_card1.uuid)
        assert len(retrieved_reviews) == 1
        assert retrieved_reviews[0].rating == review.rating

    def test_add_review_fk_violation(
        self, initialized_db_manager: FlashcardDatabase
    ):
        db = initialized_db_manager
        # Create a review for a card UUID that does not exist in the DB
        bad_review = create_sample_review(card_uuid=uuid.uuid4())

        # The operation should fail because the card does not exist.
        # This is no longer a DB constraint violation but an application logic error.
        with pytest.raises(ReviewOperationError) as excinfo:
            db.add_review_and_update_card(bad_review, CardState.Review)

        # Check that the error indicates a data consistency issue.
        assert "Failed to retrieve card" in str(excinfo.value)
        assert excinfo.value.original_exception is None

    def test_add_review_check_constraint_violation(
        self, initialized_db_manager: FlashcardDatabase, sample_card1: Card
    ):
        db = initialized_db_manager
        db.upsert_cards_batch([sample_card1])
        bad_review = create_sample_review(
            card_uuid=sample_card1.uuid, rating=99, bypass_validation=True
        )
        with pytest.raises(ReviewOperationError) as excinfo:
            db.add_review_and_update_card(bad_review, CardState.Review)
        assert isinstance(
            excinfo.value.original_exception, duckdb.ConstraintException
        )

    def test_add_reviews_individually(
        self,
        initialized_db_manager: FlashcardDatabase,
        sample_card1: Card,
        sample_card2: Card,
    ):
        db = initialized_db_manager
        db.upsert_cards_batch([sample_card1, sample_card2])
        r1 = create_sample_review(card_uuid=sample_card1.uuid)
        r2 = create_sample_review(card_uuid=sample_card2.uuid)
        db.add_review_and_update_card(r1, CardState.Review)
        db.add_review_and_update_card(r2, CardState.Review)
        reviews1 = db.get_reviews_for_card(sample_card1.uuid)
        reviews2 = db.get_reviews_for_card(sample_card2.uuid)
        assert len(reviews1) == 1
        assert len(reviews2) == 1

    def test_add_review_transactionality(self, db_manager: FlashcardDatabase):
        db = db_manager
        db.initialize_schema()
        card = create_sample_card()
        db.upsert_cards_batch([card])
        bad_review = create_sample_review(
            card_uuid=card.uuid, rating=999, bypass_validation=True
        )
        with pytest.raises(ReviewOperationError):
            # This should fail and roll back, leaving no review.
            db.add_review_and_update_card(bad_review, CardState.Review)
        assert db.get_reviews_for_card(card.uuid) == []

    def test_get_reviews_for_card(
        self, initialized_db_manager: FlashcardDatabase, sample_card1: Card
    ):
        db = initialized_db_manager
        db.upsert_cards_batch([sample_card1])
        r1 = create_sample_review(
            card_uuid=sample_card1.uuid,
            ts=datetime(2023, 1, 2, 11, 0, 0, tzinfo=timezone.utc),
        )
        r2 = create_sample_review(
            card_uuid=sample_card1.uuid,
            ts=datetime(2023, 1, 3, 12, 0, 0, tzinfo=timezone.utc),
        )
        db.add_review_and_update_card(r1, CardState.Review)
        db.add_review_and_update_card(r2, CardState.Review)
        reviews_asc = db.get_reviews_for_card(
            sample_card1.uuid, order_by_ts_desc=False
        )
        reviews_desc = db.get_reviews_for_card(
            sample_card1.uuid, order_by_ts_desc=True
        )
        assert reviews_asc[0].ts < reviews_asc[1].ts
        assert reviews_desc[0].ts > reviews_desc[1].ts

    def test_get_reviews_for_card_no_reviews(
        self, initialized_db_manager: FlashcardDatabase, sample_card1: Card
    ):
        db = initialized_db_manager
        db.upsert_cards_batch([sample_card1])
        assert db.get_reviews_for_card(sample_card1.uuid) == []

    def test_get_latest_review_for_card(
        self, initialized_db_manager: FlashcardDatabase, sample_card1: Card
    ):
        db = initialized_db_manager
        db.upsert_cards_batch([sample_card1])
        r1 = create_sample_review(
            card_uuid=sample_card1.uuid,
            ts=datetime(2023, 1, 2, 11, 0, 0, tzinfo=timezone.utc),
        )
        r2 = create_sample_review(
            card_uuid=sample_card1.uuid,
            ts=datetime(2023, 1, 3, 12, 0, 0, tzinfo=timezone.utc),
        )
        db.add_review_and_update_card(r1, CardState.Review)
        db.add_review_and_update_card(r2, CardState.Review)
        latest = db.get_latest_review_for_card(sample_card1.uuid)
        assert latest.ts == r2.ts

    def test_get_latest_review_for_card_no_reviews(
        self, initialized_db_manager: FlashcardDatabase, sample_card1: Card
    ):
        db = initialized_db_manager
        db.upsert_cards_batch([sample_card1])
        assert db.get_latest_review_for_card(sample_card1.uuid) is None

    def test_get_all_reviews_empty(
        self, initialized_db_manager: FlashcardDatabase
    ):
        assert initialized_db_manager.get_all_reviews() == []

    def test_get_all_reviews_with_data_and_filtering(
        self, initialized_db_manager: FlashcardDatabase, sample_card1: Card
    ):
        db = initialized_db_manager
        db.upsert_cards_batch([sample_card1])
        r1 = create_sample_review(
            card_uuid=sample_card1.uuid,
            ts=datetime(2023, 1, 2, 11, 0, 0, tzinfo=timezone.utc),
        )
        r2 = create_sample_review(
            card_uuid=sample_card1.uuid,
            ts=datetime(2023, 1, 3, 12, 0, 0, tzinfo=timezone.utc),
        )
        db.add_review_and_update_card(r1, CardState.Review)
        db.add_review_and_update_card(r2, CardState.Review)
        all_reviews = db.get_all_reviews()
        assert len(all_reviews) >= 2
        filtered = db.get_all_reviews(
            start_ts=datetime(2023, 1, 3, 0, 0, 0, tzinfo=timezone.utc)
        )
        assert all(
            r.ts >= datetime(2023, 1, 3, 0, 0, 0, tzinfo=timezone.utc)
            for r in filtered
        )


class TestDatabaseErrorHandling:
    def test_handle_schema_initialization_error_rollback_fails(
        self, db_manager: FlashcardDatabase, mocker
    ):
        """Tests that a failure during rollback in schema init is logged."""
        mocker.patch(
            "cultivation.scripts.flashcore.schema_manager.SchemaManager._create_schema_from_sql",
            side_effect=duckdb.Error("Schema creation failed!"),
        )
        mock_conn = mocker.patch.object(
            db_manager, "get_connection"
        ).return_value
        mock_conn.rollback.side_effect = duckdb.Error("Rollback failed!")

        with pytest.raises(
            SchemaInitializationError,
            match=r"Failed to initialize schema:.*Schema creation failed!",
        ):
            db_manager.initialize_schema()

    def test_get_deck_names_db_error(
        self, initialized_db_manager: FlashcardDatabase, mocker
    ):
        """Tests that a duckdb.Error on fetching deck names is handled."""
        mock_conn = mocker.patch.object(
            initialized_db_manager, "get_connection"
        ).return_value
        mock_conn.execute.side_effect = duckdb.Error(
            "DB error on get_deck_names"
        )

        with pytest.raises(
            CardOperationError, match="Could not fetch deck names."
        ):
            initialized_db_manager.get_deck_names()

    def test_get_all_reviews_db_error(
        self, initialized_db_manager: FlashcardDatabase, mocker
    ):
        """Tests that a duckdb.Error on fetching all reviews is handled."""
        mock_conn = mocker.patch.object(
            initialized_db_manager, "get_connection"
        ).return_value
        mock_conn.execute.side_effect = duckdb.Error(
            "DB error on get_all_reviews"
        )

        with pytest.raises(
            ReviewOperationError,
            match=r"Failed to get all reviews:.*DB error on get_all_reviews",
        ):
            initialized_db_manager.get_all_reviews()

    def test_add_review_and_update_card_consistency_error(
        self,
        initialized_db_manager: FlashcardDatabase,
        sample_review1: Review,
        mocker,
    ):
        """Tests the critical data consistency check in add_review_and_update_card."""
        db = initialized_db_manager
        mocker.patch.object(
            db, "_execute_review_transaction"
        )  # Mock out the actual DB transaction
        mocker.patch.object(
            db, "get_card_by_uuid", return_value=None
        )  # Simulate card not being found after update

        with pytest.raises(
            ReviewOperationError,
            match=r"Failed to retrieve card.*critical data consistency issue",
        ):
            db.add_review_and_update_card(sample_review1, CardState.Review)

    def test_handle_upsert_error_rollback_fails(
        self, db_manager: FlashcardDatabase, mocker
    ):
        """Tests that a failure during rollback in upsert is logged."""
        db_manager.initialize_schema()
        mock_conn = mocker.patch.object(
            db_manager, "get_connection"
        ).return_value
        mocker.patch.object(
            db_manager,
            "_execute_upsert_transaction",
            side_effect=duckdb.Error("Upsert failed!"),
        )
        mock_conn.rollback.side_effect = duckdb.Error("Rollback failed!")

        with pytest.raises(
            CardOperationError,
            match=r"Batch card upsert failed:.*Upsert failed!",
        ):
            db_manager.upsert_cards_batch([create_sample_card()])


class TestGeneralErrorHandling:
    def test_operations_on_uninitialized_db(
        self, db_manager: FlashcardDatabase, sample_card1: Card
    ):
        # Ensure connection is open but schema not initialized
        db_manager.get_connection()
        # Attempt to add a card, which should fail if schema is not initialized
        with pytest.raises(CardOperationError):
            db_manager.upsert_cards_batch([sample_card1])

    def test_operations_on_closed_connection(
        self, initialized_db_manager: FlashcardDatabase, sample_card1: Card
    ):
        db = initialized_db_manager
        db.close_connection()
        # Should reconnect or raise
        try:
            db.upsert_cards_batch([sample_card1])
        except Exception:
            pass

    def test_read_only_db_write_attempt(self, db_path_file: Path):
        db_man = FlashcardDatabase(db_path_file)
        db_man.initialize_schema()
        db_man.close_connection()
        db_readonly = FlashcardDatabase(db_path_file, read_only=True)
        db_readonly.initialize_schema()
        with pytest.raises(CardOperationError):
            db_readonly.upsert_cards_batch([create_sample_card()])


class TestIngestionBugReproduction:
    """Tests for the critical bug where ingestion destroys review history."""

    def test_upsert_preserves_review_history_on_content_update(
        self, initialized_db_manager: FlashcardDatabase
    ):
        """
        Test that demonstrates and verifies the fix for the critical bug where
        tm-fc ingest destroys review history when updating card content.

        Bug: When a card with review history is re-ingested (e.g., after YAML content changes),
        the UPSERT operation overwrites review history fields with None/default values.

        Expected behavior: Content fields should update, review history should be preserved.
        """
        db = initialized_db_manager

        # Step 1: Create a card and establish review history
        original_card = create_sample_card(
            uuid=uuid.UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"),
            front="Original Question",
            back="Original Answer",
            tags={"original-tag"},
        )

        # Insert the card initially
        db.upsert_cards_batch([original_card])

        # Add review history to simulate user learning progress
        review1 = create_sample_review(
            card_uuid=original_card.uuid,
            ts=datetime(2023, 6, 1, 10, 0, 0, tzinfo=timezone.utc),
            rating=2,  # Hard
            stab_before=None,
            stab_after=1.5,
            diff=6.0,
            next_due=date(2023, 6, 3),
        )

        review2 = create_sample_review(
            card_uuid=original_card.uuid,
            ts=datetime(2023, 6, 3, 14, 0, 0, tzinfo=timezone.utc),
            rating=3,  # Good
            stab_before=1.5,
            stab_after=4.2,
            diff=5.8,
            next_due=date(2023, 6, 8),
        )

        # Add reviews and update card state
        db.add_review_and_update_card(review1, CardState.Learning)
        db.add_review_and_update_card(review2, CardState.Review)

        # Verify the card has review history
        card_with_history = db.get_card_by_uuid(original_card.uuid)
        assert card_with_history is not None
        assert card_with_history.state == CardState.Review
        assert card_with_history.next_due_date == date(2023, 6, 8)
        assert card_with_history.stability == 4.2
        assert card_with_history.difficulty == 5.8
        assert card_with_history.last_review_id is not None

        # Verify we have 2 reviews
        reviews = db.get_reviews_for_card(original_card.uuid)
        assert len(reviews) == 2

        # Step 2: Simulate ingestion of updated card content (like from modified YAML)
        # This simulates what happens when user edits YAML and runs tm-fc ingest
        updated_card_content = create_sample_card(
            uuid=original_card.uuid,  # Same UUID
            front="Updated Question",  # Changed content
            back="Updated Answer",  # Changed content
            tags={"updated-tag"},  # Changed tags
            # Note: These fields come as None/defaults from YAML processing:
            state=CardState.New,  # Default state from YAML
            next_due_date=None,  # No due date in YAML
            stability=None,  # No FSRS data in YAML
            difficulty=None,  # No FSRS data in YAML
            last_review_id=None,  # No review ID in YAML
        )

        # Step 3: Re-ingest the card (this is where the bug occurs)
        db.upsert_cards_batch([updated_card_content])

        # Step 4: Verify the bug - review history should be preserved, content should be updated
        card_after_reingest = db.get_card_by_uuid(original_card.uuid)
        assert card_after_reingest is not None

        # Content should be updated
        assert card_after_reingest.front == "Updated Question"
        assert card_after_reingest.back == "Updated Answer"
        assert card_after_reingest.tags == {"updated-tag"}

        # CRITICAL: Review history should be preserved (this is what currently fails)
        assert (
            card_after_reingest.state == CardState.Review
        ), f"Expected Review state, got {card_after_reingest.state}"
        assert card_after_reingest.next_due_date == date(
            2023, 6, 8
        ), f"Expected due date 2023-06-08, got {card_after_reingest.next_due_date}"
        assert (
            card_after_reingest.stability == 4.2
        ), f"Expected stability 4.2, got {card_after_reingest.stability}"
        assert (
            card_after_reingest.difficulty == 5.8
        ), f"Expected difficulty 5.8, got {card_after_reingest.difficulty}"
        assert (
            card_after_reingest.last_review_id is not None
        ), "Expected last_review_id to be preserved"

        # Reviews should still exist
        reviews_after_reingest = db.get_reviews_for_card(original_card.uuid)
        assert (
            len(reviews_after_reingest) == 2
        ), f"Expected 2 reviews, got {len(reviews_after_reingest)}"

        # Verify review data integrity
        assert reviews_after_reingest[0].rating in [2, 3]
        assert reviews_after_reingest[1].rating in [2, 3]
