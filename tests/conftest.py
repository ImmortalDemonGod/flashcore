import sys
import pytest
from pathlib import Path
from typing import Generator
from datetime import date, datetime, timezone

from flashcore.models import Card, Review, CardState
from flashcore.db import FlashcardDatabase


# each test runs on cwd to its temp dir
@pytest.fixture(autouse=True)
def go_to_tmpdir(request):
    # Get the fixture dynamically by its name.
    tmpdir = request.getfixturevalue("tmpdir")
    # ensure local test created packages can be imported
    sys.path.insert(0, str(tmpdir))
    # Chdir only for the duration of the test.
    with tmpdir.as_cwd():
        yield


# --- Database Fixtures ---
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
            except OSError as e:
                import logging

                logging.warning(
                    f"Error removing temporary DB file in test fixture teardown: {e}"
                )


@pytest.fixture
def initialized_db_manager(db_manager: FlashcardDatabase) -> FlashcardDatabase:
    db_manager.initialize_schema()
    return db_manager


@pytest.fixture
def sample_card1() -> Card:
    return Card(
        uuid="11111111-1111-1111-1111-111111111111",
        deck_name="Deck A::Sub1",
        front="Sample Front",
        back="Sample Back",
        tags={"tag1", "tag2"},
        added_at=datetime(2023, 1, 1, 10, 0, tzinfo=timezone.utc),
        modified_at=datetime(2023, 1, 1, 10, 0, tzinfo=timezone.utc),
    )


@pytest.fixture
def sample_card2() -> Card:
    return Card(
        uuid="22222222-2222-2222-2222-222222222222",
        deck_name="Deck A::Sub1",
        front="Another Front",
        back="Another Back",
        tags={"tag1"},
        added_at=datetime(2023, 1, 2, 10, 0, tzinfo=timezone.utc),
        modified_at=datetime(2023, 1, 2, 10, 0, tzinfo=timezone.utc),
    )


@pytest.fixture
def sample_card3_deck_b() -> Card:
    return Card(
        uuid="33333333-3333-3333-3333-333333333333",
        deck_name="Deck B",
        front="Deck B Card Front",
        back="Deck B Card Back",
        tags={"tag3"},
        added_at=datetime(2023, 1, 3, 10, 0, tzinfo=timezone.utc),
        modified_at=datetime(2023, 1, 3, 10, 0, tzinfo=timezone.utc),
    )


@pytest.fixture
def sample_review1(sample_card1: Card) -> Review:
    return Review(
        card_uuid=sample_card1.uuid,
        rating=3,
        stab_after=5.0,
        diff=3.0,
        next_due=date.today() + timedelta(days=5),
        elapsed_days_at_review=0,
        scheduled_days_interval=5,
    )


@pytest.fixture
def sample_review2_for_card1(sample_card1: Card) -> Review:
    return Review(
        card_uuid=sample_card1.uuid,
        rating=4,
        stab_after=10.0,
        diff=2.5,
        next_due=date.today() + timedelta(days=10),
        elapsed_days_at_review=5,
        scheduled_days_interval=10,
    )
