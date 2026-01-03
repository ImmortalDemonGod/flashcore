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
    """
    Temporarily change the process working directory to the test's tmpdir and prepend that tmpdir to sys.path.
    
    Parameters:
        request: The pytest `request` fixture used to obtain the per-test `tmpdir` fixture. The working directory is changed for the duration of the test; `sys.path` is modified to insert the tmpdir at the front.
    """
    tmpdir = request.getfixturevalue("tmpdir")
    # ensure local test created packages can be imported
    sys.path.insert(0, str(tmpdir))
    # Chdir only for the duration of the test.
    with tmpdir.as_cwd():
        yield


# --- Database Fixtures ---
@pytest.fixture
def db_path_memory() -> str:
    """
    Provide the SQLite in-memory database path identifier.
    
    Returns:
        db_path (str): The SQLite path string ":memory:" which opens a transient in-memory database.
    """
    return ":memory:"


@pytest.fixture
def db_path_file(tmp_path: Path) -> Path:
    """
    Provide the filesystem path for a temporary test SQLite database file.
    
    Parameters:
        tmp_path (Path): pytest temporary directory for the current test.
    
    Returns:
        Path: Path to the file named "test_flash.db" inside `tmp_path`.
    """
    return tmp_path / "test_flash.db"


@pytest.fixture(params=["memory", "file"])
def db_manager(
    request, db_path_memory: str, db_path_file: Path
) -> Generator[FlashcardDatabase, None, None]:
    """
    Provide a FlashcardDatabase instance for tests, either in-memory or file-backed, and ensure proper teardown.
    
    Parameters:
        request: pytest `FixtureRequest` providing `param` which must be either `"memory"` or `"file"` to select the database backend.
        db_path_memory (str): Path identifier used to create an in-memory database (e.g., ":memory:").
        db_path_file (Path): Filesystem path for a temporary file-backed database.
    
    Returns:
        FlashcardDatabase: A database instance configured according to `request.param`. The fixture closes the database connection on teardown and, if using the file-backed backend, attempts to delete the temporary DB file (logging a warning if deletion fails).
    """
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
    """
    Ensure the provided FlashcardDatabase has its schema created and return it.
    
    Parameters:
        db_manager (FlashcardDatabase): Database instance whose schema will be initialized.
    
    Returns:
        FlashcardDatabase: The same `db_manager` instance with its schema initialized.
    """
    db_manager.initialize_schema()
    return db_manager


@pytest.fixture
def sample_card1() -> Card:
    """
    Create a sample Card for tests representing an entry in the "Deck A::Sub1" deck.
    
    Returns:
        Card: A Card pre-populated with uuid "11111111-1111-1111-1111-111111111111", deck name "Deck A::Sub1", front "Sample Front", back "Sample Back", tags {"tag1", "tag2"}, and UTC added/modified timestamps of 2023-01-01 10:00:00.
    """
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
    """
    Create a sample Card for tests representing "Another Front/Back" in the "Deck A::Sub1" deck.
    
    Returns:
        Card: A Card with uuid "22222222-2222-2222-2222-222222222222", deck_name "Deck A::Sub1", front "Another Front", back "Another Back", tags {"tag1"}, and both added_at and modified_at set to 2023-01-02 10:00 UTC.
    """
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
    """
    Create a sample Card belonging to "Deck B" for use in tests.
    
    The card has UUID "33333333-3333-3333-333333333333", front text "Deck B Card Front",
    back text "Deck B Card Back", tags {"tag3"}, and UTC timestamps set to 2023-01-03T10:00:00.
    
    Returns:
        Card: A Card instance populated with the above test data.
    """
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
    """
    Create a sample Review for the given card populated with deterministic test values.
    
    Parameters:
        sample_card1 (Card): Card whose UUID will be used as the review's card_uuid.
    
    Returns:
        Review: Review linked to the provided card with rating 3, stab_after 5.0, diff 3.0, next_due equal to today plus 5 days, elapsed_days_at_review 0, and scheduled_days_interval 5.
    """
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
    """
    Create a Review for the provided card using fixed sample values and a next_due date 10 days from today.
    
    Parameters:
        sample_card1 (Card): Card to associate the generated Review with.
    
    Returns:
        Review: A Review instance for the given card with rating 4, stab_after 10.0, diff 2.5, next_due set to today plus 10 days, elapsed_days_at_review 5, and scheduled_days_interval 10.
    """
    return Review(
        card_uuid=sample_card1.uuid,
        rating=4,
        stab_after=10.0,
        diff=2.5,
        next_due=date.today() + timedelta(days=10),
        elapsed_days_at_review=5,
        scheduled_days_interval=10,
    )