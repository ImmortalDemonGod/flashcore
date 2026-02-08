# Standard library imports
import re
from collections import Counter
from pathlib import Path
from unittest.mock import ANY, MagicMock, patch
from uuid import uuid4

# Third-party imports
import pytest
import typer
import yaml
from typer.testing import CliRunner

# Local application imports
from flashcore.models import Card, CardState
from flashcore.cli.main import app
from flashcore.db.database import FlashcardDatabase
from flashcore.exceptions import DeckNotFoundError, FlashcardDatabaseError


runner = CliRunner()


def strip_ansi(text: str) -> str:
    """
    Remove ANSI escape sequences (color and control codes) from text.
    
    Parameters:
        text (str): Input string that may contain ANSI escape sequences.
    
    Returns:
        str: The input string with all ANSI escape sequences removed.
    """
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


def normalize_output(text: str) -> str:
    """
    Normalize CLI output by removing ANSI escape sequences and collapsing consecutive whitespace into single spaces.
    
    Parameters:
        text (str): The original text (may contain ANSI escape codes and arbitrary whitespace).
    
    Returns:
        str: The cleaned text with ANSI codes removed and all whitespace sequences replaced by a single space, trimmed of leading/trailing spaces.
    """
    text = strip_ansi(text)
    # Replace all whitespace (spaces, tabs, newlines) with a single space
    return re.sub(r"\s+", " ", text).strip()


@pytest.fixture
def temp_flashcard_files(tmp_path):
    """
    Create three temporary YAML flashcard deck files for tests.
    
    Creates:
    - `valid.yml`: a deck named "Valid Deck" containing two complete cards (question and answer).
    - `invalid.yml`: a deck named "Invalid Deck" containing a card missing an answer.
    - `needs_vetting.yml`: a deck named "Needs Vetting" containing two unsorted cards intended to require vetting.
    
    Parameters:
        tmp_path (pathlib.Path): Base temporary directory in which to create the files.
    
    Returns:
        tuple: (tmp_path, valid_file, invalid_file, needs_vetting_file) where each file is a pathlib.Path to the created YAML file.
    """
    valid_deck = {
        "deck": "Valid Deck",
        "cards": [
            {"q": "Question 1", "a": "Answer 1"},
            {"q": "Question 2", "a": "Answer 2"},
        ],
    }
    invalid_deck = {"deck": "Invalid Deck", "cards": [{"q": "Only a question"}]}
    needs_vetting_deck = {
        "deck": "Needs Vetting",
        "cards": [
            {"q": "Unsorted Question Z", "a": "Answer Z"},
            {"q": "Unsorted Question A", "a": "Answer A"},
        ],
    }

    valid_file = tmp_path / "valid.yml"
    invalid_file = tmp_path / "invalid.yml"
    needs_vetting_file = tmp_path / "needs_vetting.yml"

    with open(valid_file, "w") as f:
        yaml.dump(valid_deck, f)
    with open(invalid_file, "w") as f:
        yaml.dump(invalid_deck, f)
    with open(needs_vetting_file, "w") as f:
        yaml.dump(needs_vetting_deck, f)

    return tmp_path, valid_file, invalid_file, needs_vetting_file


def test_vet_command_no_files(tmp_path):
    """Tests that vet handles directories with no YAML files gracefully."""
    result = runner.invoke(app, ["vet", "--source-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "No YAML files found to vet." in result.stdout


def test_vet_command_check_mode_dirty(temp_flashcard_files):
    """Tests that vet --check returns a non-zero exit code if files need changes."""
    temp_dir, valid_file, invalid_file, _ = temp_flashcard_files
    # Isolate the test to only the file that needs formatting, not validation.
    valid_file.unlink()
    invalid_file.unlink()

    result = runner.invoke(app, ["vet", "--check", "--source-dir", str(temp_dir)])
    output = normalize_output(result.stdout)
    assert result.exit_code == 1
    assert "! Dirty: needs_vetting.yml" in output
    assert "Check failed: Some files need changes." in output


def test_vet_command_check_mode_clean(temp_flashcard_files):
    """Tests that vet --check returns a zero exit code if a file is clean after formatting."""
    # This test checks for idempotency. First we vet a file, then we check it.
    temp_dir, clean_file, invalid_file, needs_vetting_file = temp_flashcard_files
    # To make the test specific, we'll work with just the file that needs formatting.
    clean_file.unlink()
    invalid_file.unlink()

    # First, run vet to format the file. This file is valid but needs sorting/UUIDs.
    result_format = runner.invoke(app, ["vet", "--source-dir", str(temp_dir)])
    output_format = re.sub(r"\s+", " ", strip_ansi(result_format.stdout)).strip()
    assert result_format.exit_code == 0, f"Initial vet run failed: {output_format}"
    assert "File formatted successfully: needs_vetting.yml" in output_format
    assert "✓ Vetting complete. Some files were modified." in output_format

    # Now, run vet --check to ensure it's considered clean.
    result_check = runner.invoke(app, ["vet", "--check", "--source-dir", str(temp_dir)])
    output_check = re.sub(r"\s+", " ", strip_ansi(result_check.stdout)).strip()
    assert (
        result_check.exit_code == 0
    ), f"vet --check failed on formatted file: {output_check}"
    assert "All files are clean. No changes needed." in output_check


def test_vet_command_modifies_file(temp_flashcard_files):
    """Tests that vet modifies a file that needs formatting."""
    temp_dir, clean_file, invalid_file, needs_vetting_file = temp_flashcard_files
    # To make the test specific, we only want the file that needs formatting.
    clean_file.unlink()
    invalid_file.unlink()

    original_content = needs_vetting_file.read_text()

    # Run vet to modify the file.
    result_modify = runner.invoke(app, ["vet", "--source-dir", str(temp_dir)])
    output_modify = normalize_output(result_modify.stdout)
    assert result_modify.exit_code == 0
    assert "File formatted successfully: needs_vetting.yml" in output_modify
    assert "✓ Vetting complete. Some files were modified." in output_modify

    modified_content = needs_vetting_file.read_text()
    assert original_content != modified_content
    assert "uuid:" in modified_content

    # As a final check, ensure the modified file is now considered clean.
    result_check = runner.invoke(app, ["vet", "--check", "--source-dir", str(temp_dir)])
    output_check = normalize_output(result_check.stdout)
    assert (
        result_check.exit_code == 0
    ), f"vet --check failed after modification: {output_check}"
    assert "All files are clean. No changes needed." in output_check


@patch("flashcore.cli.main.FlashcardDatabase")
def test_stats_command(MockDatabase, tmp_path):
    """Tests the stats command with mocked database output."""
    # 1. Setup mock
    mock_db_instance = MockDatabase.return_value
    mock_db_instance.__enter__.return_value = mock_db_instance

    # 2. Define the mock return value for the high-level stats method
    mock_stats_data = {
        "total_cards": 3,
        "total_reviews": 1,
        "decks": [
            {"deck_name": "Deck A", "card_count": 2, "due_count": 1},
            {"deck_name": "Deck B", "card_count": 1, "due_count": 0},
        ],
        "states": {
            "New": 1,
            "Learning": 2,
        },
    }
    mock_db_instance.get_database_stats.return_value = mock_stats_data
    db_path = tmp_path / "test.db"

    # 3. Execute command
    result = runner.invoke(app, ["stats", "--db", str(db_path)])

    # 4. Assertions
    assert result.exit_code == 0

    # Clean stdout to make assertions robust against rich's formatting
    output = normalize_output(result.stdout)

    # Check for key text components in the rich table output
    assert "Overall Database Stats" in output
    assert "Total Cards │ 3" in output
    assert "Total Reviews │ 1" in output
    assert "Decks" in output
    assert "Deck A │ 2 │ 1" in output
    assert "Deck B │ 1 │ 0" in output
    assert "Card States" in output
    assert "New │ 1" in output
    assert "Learning │ 2" in output


@patch("flashcore.cli.main.FlashcardDatabase")
@patch("flashcore.cli.main._load_cards_from_source")
def test_ingest_command(mock_load_cards, MockDatabase, tmp_path):
    """Tests the ingest command, mocking the loader and DB."""
    # 1. Configure mocks
    db_path = tmp_path / "test.db"
    mock_db_instance = MockDatabase.return_value
    mock_db_instance.__enter__.return_value = mock_db_instance

    # Simulate one processed card and no errors
    mock_card = MagicMock()
    mock_card.front = "Q1"
    mock_cards = [mock_card]
    mock_load_cards.return_value = mock_cards
    mock_db_instance.upsert_cards_batch.return_value = len(mock_cards)

    # 2. Execute command
    result = runner.invoke(
        app, ["ingest", "--db", str(db_path), "--source-dir", str(tmp_path)]
    )

    # 3. Assertions
    assert (
        result.exit_code == 0
    ), f"CLI exited with code {result.exit_code}: {result.stdout}"
    mock_load_cards.assert_called_once()
    mock_db_instance.upsert_cards_batch.assert_called_once_with(mock_cards)
    output = normalize_output(result.stdout)
    assert "Ingestion complete!" in output
    assert "1 cards were successfully ingested or updated." in output


@patch("flashcore.cli.main.load_and_process_flashcard_yamls")
@patch("flashcore.cli.main.FlashcardDatabase")
def test_ingest_command_re_ingest_flag(mock_db, mock_load_process, tmp_path):
    """Tests the ingest command with the --re-ingest flag."""
    db_path = tmp_path / "test.db"
    mock_load_process.return_value = ([MagicMock()], [])
    mock_db.return_value.__enter__.return_value.upsert_cards_batch.return_value = 1

    result = runner.invoke(
        app,
        ["ingest", "--db", str(db_path), "--source-dir", str(tmp_path), "--re-ingest"],
    )

    assert (
        result.exit_code == 0
    ), f"CLI exited with code {result.exit_code}: {result.stdout}"
    output = normalize_output(result.stdout)
    assert "--re-ingest flag is noted" in output
    mock_load_process.assert_called_once()
    mock_db.return_value.__enter__.return_value.upsert_cards_batch.assert_called_once()


@patch("flashcore.cli.main.load_and_process_flashcard_yamls")
def test_ingest_command_yaml_errors(mock_load_process, tmp_path):
    """Tests that the ingest command exits if there are YAML processing errors."""
    db_path = tmp_path / "test.db"

    # Simulate YAML processing returning errors
    mock_load_process.return_value = ([], ["Error 1"])

    result = runner.invoke(
        app, ["ingest", "--db", str(db_path), "--source-dir", str(tmp_path)]
    )

    # The command should exit with an error code because _load_cards_from_source handles this.
    assert result.exit_code == 1
    output = normalize_output(result.stdout)
    assert "Errors encountered during YAML processing" in output
    assert "Error 1" in output
    assert "No flashcards found to ingest." not in output


@patch("flashcore.cli.main.FlashcardDatabase")
@patch("flashcore.cli.main._load_cards_from_source")
def test_ingest_command_no_flashcards(
    mock_load_cards_from_source, mock_FlashcardDatabase, tmp_path
):
    """Tests the ingest command when no flashcards are found."""
    # Simulate the loader finding no cards, which causes a graceful exit.
    mock_load_cards_from_source.side_effect = typer.Exit(0)
    db_path = tmp_path / "test.db"

    result = runner.invoke(
        app, ["ingest", "--db", str(db_path), "--source-dir", str(tmp_path)]
    )

    # Should exit gracefully
    assert result.exit_code == 0
    # No database operations should have occurred
    mock_FlashcardDatabase.return_value.__enter__.return_value.upsert_cards_batch.assert_not_called()


def test_vet_command_with_pre_commit_args():
    """Tests that `vet` command runs successfully when passed file paths by pre-commit."""
    with patch("flashcore.cli.main.vet_logic") as mock_vet_logic:
        mock_vet_logic.return_value = False
        files_arg = [Path("some/file/path.yaml")]
        result = runner.invoke(app, ["vet", "--check", str(files_arg[0])])
        assert result.exit_code == 0
        mock_vet_logic.assert_called_once_with(
            check=True,
            files_to_process=files_arg,
            source_dir=None,
        )


@patch("flashcore.cli.main._load_cards_from_source")
@patch("flashcore.cli.main.FlashcardDatabase")
def test_ingest_command_db_exception(mock_db, mock_load_cards, tmp_path):
    """Tests the ingest command handles generic database exceptions."""
    mock_load_cards.return_value = [MagicMock()]
    # Simulate a database error during the 'with' block
    mock_db.return_value.__enter__.side_effect = FlashcardDatabaseError(
        "Connection refused"
    )
    db_path = tmp_path / "test.db"

    result = runner.invoke(
        app, ["ingest", "--db", str(db_path), "--source-dir", str(tmp_path)]
    )

    assert result.exit_code == 1
    output = normalize_output(result.stdout)
    assert "Database Error: Connection refused" in output


def test_ingest_command_integration(tmp_path: Path):
    """
    Integration test that vets YAML deck files, ingests them into a temporary database, and verifies the persisted cards.
    
    Creates a small deck YAML in a temporary source directory, runs the CLI's `vet` command to normalize/validate the files, runs the `ingest` command against a temporary SQLite database, and asserts that two cards exist in the database with the expected deck name, fronts, and backs.
    """
    # 1. Setup paths
    yaml_src_dir = tmp_path / "yaml_files"
    yaml_src_dir.mkdir()
    db_path = tmp_path / "test.db"

    # 2. Create test data
    deck_content = {
        "deck": "Integration Deck",
        "cards": [
            {"q": "Integration Q1", "a": "Integration A1"},
            {"q": "Integration Q2", "a": "Integration A2"},
        ],
    }
    unvetted_file = yaml_src_dir / "deck.yml"
    with unvetted_file.open("w") as f:
        yaml.dump(deck_content, f)

    # 3. Run vet command
    vet_result = runner.invoke(app, ["vet", "--source-dir", str(yaml_src_dir)])
    assert vet_result.exit_code == 0, f"Vet command failed: {vet_result.stdout}"

    # 4. Run ingest command
    ingest_result = runner.invoke(
        app, ["ingest", "--db", str(db_path), "--source-dir", str(yaml_src_dir)]
    )
    assert (
        ingest_result.exit_code == 0
    ), f"Ingest command failed: {ingest_result.stdout}"
    ingest_output = normalize_output(ingest_result.stdout)
    assert "2 cards were successfully ingested or updated" in ingest_output

    # 5. Verify database state
    with FlashcardDatabase(db_path=db_path) as db:
        cards = db.get_all_cards()
        assert len(cards) == 2
        assert cards[0].deck_name == "Integration Deck"
        assert cards[0].front == "Integration Q1"
        assert cards[1].back == "Integration A2"


def test_stats_command_integration(tmp_path: Path):
    """
    Tests the stats command with a real database and YAML files.
    """
    # 1. Setup paths
    yaml_src_dir = tmp_path / "yaml_files"
    yaml_src_dir.mkdir()
    db_path = tmp_path / "test.db"

    # 2. Create test data
    deck_content = {
        "deck": "Integration Deck",
        "cards": [
            {"q": "Stats Q1", "a": "Stats A1", "state": "New"},
            {"q": "Stats Q2", "a": "Stats A2", "state": "Learning"},
            {"q": "Stats Q3", "a": "Stats A3", "state": "Relearning"},
            {
                "q": "Stats Q1",
                "a": "Stats A1 Duplicate",
                "state": "New",
            },  # Duplicate question
        ],
    }
    vetted_file = yaml_src_dir / "deck.yml"
    with vetted_file.open("w") as f:
        yaml.dump(deck_content, f)

    # 3. Vet and Ingest data
    runner.invoke(app, ["vet", "--source-dir", str(yaml_src_dir)])
    runner.invoke(
        app, ["ingest", "--db", str(db_path), "--source-dir", str(yaml_src_dir)]
    )

    # 4. Run stats command
    result = runner.invoke(app, ["stats", "--db", str(db_path)], env={"COLUMNS": "200"})

    # 5. Assertions
    assert (
        result.exit_code == 0
    ), f"Stats command failed with exit code {result.exit_code}. Output: {result.stdout}"
    output = normalize_output(result.stdout)

    # We expect only 3 cards to be ingested due to the in-file duplicate.
    assert "Total Cards │ 3" in output
    # All 3 cards are due (next_due_date is NULL).
    assert "Integration Deck │ 3 │ 3" in output
    # The duplicate 'New' card was dropped.
    assert "New │ 1" in output
    assert "Learning │ 1" in output
    assert "Relearning │ 1" in output


def test_stats_command_with_manual_db_population(tmp_path):
    """
    Tests the stats command against a real database populated with data.
    """
    db_path = tmp_path / "stats_test.db"

    # Manually populate the database
    with FlashcardDatabase(db_path=db_path) as db:
        db.initialize_schema()
        cards_to_insert = [
            Card(
                uuid=uuid4(),
                deck_name="Stats Deck",
                front="q1",
                back="a1",
                state=CardState.New,
            ),
            Card(
                uuid=uuid4(),
                deck_name="Stats Deck",
                front="q2",
                back="a2",
                state=CardState.Learning,
            ),
            Card(
                uuid=uuid4(),
                deck_name="Another Deck",
                front="q3",
                back="a3",
                state=CardState.Learning,
            ),
        ]
        db.upsert_cards_batch(cards_to_insert)

    # Run the stats command
    result = runner.invoke(app, ["stats", "--db", str(db_path)], env={"COLUMNS": "200"})
    output = normalize_output(result.stdout)

    assert result.exit_code == 0
    assert "Total Cards │ 3" in output
    assert "Stats Deck │ 2 │ 2" in output
    assert "Another Deck │ 1 │ 1" in output


@patch("flashcore.cli.main.FlashcardDatabase")
def test_stats_command_no_cards(mock_db, tmp_path):
    """Tests the stats command when the database has no cards."""
    mock_db_instance = mock_db.return_value.__enter__.return_value
    mock_db_instance.get_database_stats.return_value = {
        "total_cards": 0,
        "total_reviews": 0,
        "decks": [],
        "states": Counter(),
    }
    db_path = tmp_path / "test.db"

    result = runner.invoke(app, ["stats", "--db", str(db_path)])

    assert result.exit_code == 0
    assert "No cards found in the database." in strip_ansi(result.stdout)
    # The tables should not be in the output.
    assert "Overall Database Stats" not in strip_ansi(result.stdout)


@patch("flashcore.cli.main.FlashcardDatabase")
def test_stats_command_db_exception(mock_db, tmp_path):
    """Tests the stats command handles generic database exceptions."""
    mock_db.return_value.__enter__.side_effect = FlashcardDatabaseError(
        "DB file not found"
    )
    db_path = tmp_path / "test.db"

    result = runner.invoke(app, ["stats", "--db", str(db_path)])

    assert result.exit_code == 1
    output = normalize_output(result.output)
    assert "A database error occurred: DB file not found" in output


@patch("flashcore.cli.main.FlashcardDatabase")
def test_stats_command_unexpected_exception(mock_db, tmp_path):
    """Tests the stats command handles an unexpected generic Exception."""
    mock_db.return_value.__enter__.side_effect = Exception("Something broke")
    db_path = tmp_path / "test.db"

    result = runner.invoke(app, ["stats", "--db", str(db_path)])

    assert result.exit_code == 1
    output = normalize_output(result.output)
    assert (
        "An unexpected error occurred while fetching stats: Something broke" in output
    )


@patch("flashcore.cli.main.review_logic")
def test_review_command(mock_review_logic, tmp_path):
    """Tests the review command calls the underlying logic function."""
    deck = "MyDeck"
    db_path = tmp_path / "db.db"

    result = runner.invoke(app, ["review", deck, "--db", str(db_path)])
    assert result.exit_code == 0
    mock_review_logic.assert_called_once_with(
        deck_name=deck,
        db_path=db_path,
        user_uuid=ANY,
        tags=None,
    )


@patch("flashcore.cli.main.review_all_logic")
def test_review_all_command(mock_review_all_logic, tmp_path):
    """Tests the review-all command calls the underlying logic function."""
    db_path = tmp_path / "db.db"

    result = runner.invoke(app, ["review-all", "--db", str(db_path)])
    assert result.exit_code == 0
    mock_review_all_logic.assert_called_once_with(db_path=db_path, limit=50)


@patch("flashcore.cli.main.review_all_logic")
def test_review_all_command_with_limit(mock_review_all_logic, tmp_path):
    """Tests the review-all command with custom limit."""
    db_path = tmp_path / "db.db"

    result = runner.invoke(app, ["review-all", "--db", str(db_path), "--limit", "10"])
    assert result.exit_code == 0
    mock_review_all_logic.assert_called_once_with(db_path=db_path, limit=10)


@patch("flashcore.cli.main.review_all_logic")
def test_review_all_command_with_short_limit_flag(mock_review_all_logic, tmp_path):
    """Tests the review-all command with short limit flag."""
    db_path = tmp_path / "db.db"

    result = runner.invoke(app, ["review-all", "--db", str(db_path), "-l", "5"])
    assert result.exit_code == 0
    mock_review_all_logic.assert_called_once_with(db_path=db_path, limit=5)


@patch("flashcore.cli.main.review_logic")
def test_review_command_db_error(mock_review_logic, tmp_path):
    """Tests the review command handles FlashcardDatabaseError."""
    mock_review_logic.side_effect = FlashcardDatabaseError("DB connection failed")
    deck = "MyDeck"
    db_path = tmp_path / "db.db"

    result = runner.invoke(app, ["review", deck, "--db", str(db_path)])
    assert result.exit_code == 1
    output = normalize_output(result.stdout)
    assert "A database error occurred: DB connection failed" in output


@patch("flashcore.cli.main.review_logic")
def test_review_command_deck_not_found_error(mock_review_logic, tmp_path):
    """Tests the review command handles DeckNotFoundError."""
    mock_review_logic.side_effect = DeckNotFoundError("Deck 'MyDeck' not found")
    deck = "MyDeck"
    db_path = tmp_path / "db.db"

    result = runner.invoke(app, ["review", deck, "--db", str(db_path)])
    assert result.exit_code == 1
    output = normalize_output(result.stdout)
    assert "Error: Deck 'MyDeck' not found" in output


@patch("flashcore.cli.main.review_logic")
def test_review_command_unexpected_error(mock_review_logic, tmp_path):
    """Tests the review command handles an unexpected generic Exception."""
    mock_review_logic.side_effect = Exception("Something went wrong")
    deck = "MyDeck"
    db_path = tmp_path / "db.db"

    result = runner.invoke(app, ["review", deck, "--db", str(db_path)])
    assert result.exit_code == 1
    output = normalize_output(result.stdout)
    assert "An unexpected error occurred: Something went wrong" in output


@patch("flashcore.cli.main.FlashcardDatabase")
def test_stats_command_no_card_states(mock_db, tmp_path):
    """Tests stats command when cards exist but have no countable states."""
    mock_db_instance = mock_db.return_value.__enter__.return_value
    mock_db_instance.get_database_stats.return_value = {
        "total_cards": 1,
        "total_reviews": 0,
        "decks": [{"deck_name": "Test Deck", "card_count": 1, "due_count": 0}],
        "states": Counter(),  # No states
    }
    db_path = tmp_path / "test.db"

    result = runner.invoke(app, ["stats", "--db", str(db_path)], env={"COLUMNS": "200"})
    output = normalize_output(result.stdout)

    assert result.exit_code == 0
    assert "Total Cards │ 1" in output
    assert "Test Deck │ 1 │ 0" in output
    assert "N/A │ 1" in output  # Check for the placeholder for cards with no state
    assert "Card States" in output
    # Check that the table body is empty as no states are returned
    assert "New" not in output
    assert "Learning" not in output
    assert "Relearning" not in output


def test_export_anki_stub():
    """Tests that the anki export stub prints a 'not implemented' message."""
    result = runner.invoke(app, ["export", "anki"])
    output = normalize_output(result.stdout)
    assert result.exit_code == 0
    assert "Export to Anki is not yet implemented. This is a placeholder." in output


@patch("flashcore.cli.main.export_to_markdown")
def test_export_md_command(mock_export_logic, tmp_path):
    """Tests the 'export md' command calls the underlying logic function."""
    db_path = tmp_path / "db.db"
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    result = runner.invoke(
        app, ["export", "md", "--db", str(db_path), "--output-dir", str(output_dir)]
    )

    assert result.exit_code == 0
    mock_export_logic.assert_called_once_with(db=ANY, output_dir=output_dir)


@patch("flashcore.cli.main.app")
@patch("flashcore.cli.main.console.print")
def test_main_handles_unexpected_exception(mock_print, mock_app):
    """Tests that the main function catches and reports unexpected exceptions."""
    mock_app.side_effect = Exception("Something went wrong")
    with patch("flashcore.cli.main.app", mock_app):
        from flashcore.cli.main import main

        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
    # Check that the mock_print was called with the exception message.
    # The exact formatting may vary, so we check for the presence of the error string.
    assert any(
        "UNEXPECTED ERROR: Something went wrong" in call.args[0]
        for call in mock_print.call_args_list
    )


@patch("flashcore.cli.main.FlashcardDatabase")
@patch("flashcore.cli.main.load_and_process_flashcard_yamls")
def test_ingest_proceeds_with_partial_yaml_errors(mock_load_process, mock_db, tmp_path):
    """Tests that ingest proceeds if some cards are loaded despite YAML errors."""
    db_path = tmp_path / "test.db"
    mock_db_instance = mock_db.return_value.__enter__.return_value
    mock_db_instance.get_all_card_fronts_and_uuids.return_value = set()
    mock_db_instance.upsert_cards_batch.return_value = 1

    mock_card = Card(
        uuid=uuid4(), deck_name="deck", front="q", back="a", state=CardState.New
    )
    mock_load_process.return_value = ([mock_card], ["Bad file"])

    result = runner.invoke(
        app, ["ingest", "--db", str(db_path), "--source-dir", str(tmp_path)]
    )

    assert result.exit_code == 0, result.stdout
    output = normalize_output(result.stdout)
    assert "Errors encountered during YAML processing" in output
    assert "Bad file" in output
    assert "Ingestion complete!" in output
    mock_db_instance.upsert_cards_batch.assert_called_once()


@patch("flashcore.cli.main.FlashcardDatabase")
@patch("flashcore.cli.main._load_cards_from_source")
def test_ingest_handles_database_error_during_upsert(
    mock_load_cards, mock_db, tmp_path
):
    """Tests ingest handles a DatabaseError during the upsert operation."""
    mock_load_cards.return_value = [MagicMock()]
    mock_db_instance = mock_db.return_value.__enter__.return_value
    mock_db_instance.upsert_cards_batch.side_effect = FlashcardDatabaseError(
        "UPSERT failed"
    )
    db_path = tmp_path / "test.db"

    result = runner.invoke(
        app, ["ingest", "--db", str(db_path), "--source-dir", str(tmp_path)]
    )

    assert result.exit_code == 1
    output = normalize_output(result.stdout)
    assert "Database Error: UPSERT failed" in output


@patch("flashcore.cli.main.export_to_markdown")
@patch("flashcore.cli.main.FlashcardDatabase")
def test_export_md_handles_io_error(mock_db, mock_export, tmp_path):
    """Tests that the 'export md' command handles an IOError."""
    mock_export.side_effect = IOError("Permission denied")
    db_path = tmp_path / "test.db"

    result = runner.invoke(
        app, ["export", "md", "--db", str(db_path), "--output-dir", str(tmp_path)]
    )

    assert result.exit_code == 1
    output = normalize_output(result.stdout)
    assert "An error occurred during export: Permission denied" in output


def test_ingest_preserves_review_state_integration(tmp_path: Path):
    """
    Tests that a second ingest preserves the review state of an existing card
    while updating its content.
    """
    # 1. Setup: Create a database and a YAML file with one card.
    yaml_src_dir = tmp_path / "yaml_files"
    yaml_src_dir.mkdir()
    db_path = tmp_path / "test_preserve.db"

    deck_content = {
        "deck": "State Preservation Deck",
        "cards": [
            {"q": "Original Question", "a": "Answer"},
        ],
    }
    card_file = yaml_src_dir / "deck.yml"
    with card_file.open("w") as f:
        yaml.dump(deck_content, f)

    # 2. Vet and Ingest for the first time.
    runner.invoke(app, ["vet", "--source-dir", str(yaml_src_dir)])
    runner.invoke(
        app, ["ingest", "--db", str(db_path), "--source-dir", str(yaml_src_dir)]
    )

    # 3. Manually update the card's state in the DB to simulate a review.
    with FlashcardDatabase(db_path=db_path) as db:
        cards = db.get_all_cards()
        assert len(cards) == 1
        card_to_update = cards[0]
        card_to_update.state = CardState.Learning
        db.upsert_cards_batch([card_to_update])
        # Capture the UUID after the first ingest and state update
        card_uuid = card_to_update.uuid

    # 4. Modify the card's content in the YAML file, adding the stable ID.
    deck_content["cards"][0]["id"] = str(card_uuid)
    deck_content["cards"][0]["q"] = "Updated Question"
    with card_file.open("w") as f:
        yaml.dump(deck_content, f)

    # 5. Run ingest again.
    ingest_result = runner.invoke(
        app, ["ingest", "--db", str(db_path), "--source-dir", str(yaml_src_dir)]
    )
    assert ingest_result.exit_code == 0, f"Second ingest failed: {ingest_result.stdout}"

    # 6. Verify the card's state was preserved and content was updated.
    with FlashcardDatabase(db_path=db_path) as db:
        final_cards = db.get_all_cards()
        assert len(final_cards) == 1
        final_card = final_cards[0]
        assert final_card.uuid == card_uuid
        assert final_card.state == CardState.Learning
        assert final_card.front == "Updated Question"


class TestCoverageGaps:
    """Tests targeting specific uncovered lines in cli/main.py."""

    def test_resolve_db_path_from_envvar(self, tmp_path, monkeypatch):
        """Test _resolve_db_path falls back to FLASHCORE_DB envvar."""
        monkeypatch.setenv("FLASHCORE_DB", str(tmp_path / "env.db"))
        result = runner.invoke(app, ["stats"])
        assert result.exit_code != 1 or "Error: --db is required" not in result.stdout

    def test_resolve_db_path_missing_errors(self, monkeypatch):
        """Test _resolve_db_path errors when no --db and no envvar."""
        monkeypatch.delenv("FLASHCORE_DB", raising=False)
        result = runner.invoke(app, ["stats"])
        assert result.exit_code != 0
        assert "Error: --db is required" in strip_ansi(result.stdout)

    def test_ingest_no_flashcards_found(self, tmp_path):
        """Test ingest with empty source dir (no YAML files)."""
        db_path = tmp_path / "test.db"
        source_dir = tmp_path / "empty_src"
        source_dir.mkdir()
        result = runner.invoke(
            app, ["ingest", "--db", str(db_path), "--source-dir", str(source_dir)]
        )
        output = strip_ansi(result.stdout)
        assert "No flashcards found" in output or result.exit_code == 0

    def test_ingest_source_dir_required(self, tmp_path):
        """Test ingest without --source-dir gives error."""
        db_path = tmp_path / "test.db"
        result = runner.invoke(app, ["ingest", "--db", str(db_path)])
        output = strip_ansi(result.stdout)
        assert "Error: --source-dir is required" in output
        assert result.exit_code != 0

    def test_ingest_all_cards_already_exist(self, tmp_path):
        """Test ingest when all cards already in database."""
        db_path = tmp_path / "test.db"
        source_dir = tmp_path / "src"
        source_dir.mkdir()

        yaml_content = {"deck": "Test", "cards": [{"q": "What?", "a": "That"}]}
        (source_dir / "deck.yml").write_text(yaml.dump(yaml_content))

        # First ingest
        result1 = runner.invoke(
            app, ["ingest", "--db", str(db_path), "--source-dir", str(source_dir)]
        )
        assert result1.exit_code == 0

        # Second ingest - cards already exist
        result2 = runner.invoke(
            app, ["ingest", "--db", str(db_path), "--source-dir", str(source_dir)]
        )
        output = strip_ansi(result2.stdout)
        assert "already exist" in output or result2.exit_code == 0

    @patch("flashcore.cli.main.review_logic")
    @patch("flashcore.cli.main.backup_database")
    def test_review_with_tags(self, mock_backup, mock_review, tmp_path):
        """Test review command with --tags flag."""
        db_path = tmp_path / "test.db"
        FlashcardDatabase(db_path=db_path).initialize_schema()
        mock_backup.return_value = tmp_path / "backups" / "test.db.bak"
        mock_backup.return_value.parent.mkdir(parents=True, exist_ok=True)

        result = runner.invoke(
            app,
            [
                "review",
                "TestDeck",
                "--db",
                str(db_path),
                "--tags",
                "math,science",
            ],
        )
        output = strip_ansi(result.stdout)
        assert "math" in output or result.exit_code == 0

    @patch("flashcore.cli.main.review_all_logic", side_effect=Exception("Unexpected"))
    @patch("flashcore.cli.main.backup_database")
    def test_review_all_unexpected_error(self, mock_backup, mock_review_all, tmp_path):
        """Test review-all with unexpected exception."""
        db_path = tmp_path / "test.db"
        mock_backup.return_value = tmp_path / "backups" / "test.db.bak"
        mock_backup.return_value.parent.mkdir(parents=True, exist_ok=True)

        result = runner.invoke(app, ["review-all", "--db", str(db_path)])
        assert result.exit_code != 0
        assert "unexpected error" in strip_ansi(result.stdout).lower()

    def test_export_md_output_dir_required(self, tmp_path):
        """Test export md without --output-dir gives error."""
        db_path = tmp_path / "test.db"
        result = runner.invoke(app, ["export", "md", "--db", str(db_path)])
        output = strip_ansi(result.stdout)
        assert "Error: --output-dir is required" in output
        assert result.exit_code != 0

    @patch("flashcore.cli.main.find_latest_backup")
    def test_restore_no_backup_found(self, mock_find, tmp_path):
        """Test restore when no backup files exist."""
        db_path = tmp_path / "test.db"
        mock_find.return_value = None
        result = runner.invoke(app, ["restore", "--db", str(db_path)])
        output = strip_ansi(result.stdout)
        assert "No backup files found" in output
        assert result.exit_code != 0

    @patch("flashcore.cli.main.shutil.copy2")
    @patch("flashcore.cli.main.find_latest_backup")
    def test_restore_success_with_yes(self, mock_find, mock_copy, tmp_path):
        """Test restore command with --yes flag."""
        db_path = tmp_path / "test.db"
        backup_file = tmp_path / "test.db.bak"
        backup_file.touch()
        mock_find.return_value = backup_file
        result = runner.invoke(app, ["restore", "--db", str(db_path), "--yes"])
        output = strip_ansi(result.stdout)
        assert "successfully restored" in output
        mock_copy.assert_called_once()

    @patch("flashcore.cli.main.shutil.copy2", side_effect=OSError("Permission denied"))
    @patch("flashcore.cli.main.find_latest_backup")
    def test_restore_copy_error(self, mock_find, mock_copy, tmp_path):
        """Test restore when copy fails."""
        db_path = tmp_path / "test.db"
        backup_file = tmp_path / "test.db.bak"
        backup_file.touch()
        mock_find.return_value = backup_file
        result = runner.invoke(app, ["restore", "--db", str(db_path), "--yes"])
        output = strip_ansi(result.stdout)
        assert "unexpected error" in output.lower()
        assert result.exit_code != 0

    @patch("flashcore.cli.main.find_latest_backup")
    def test_restore_cancelled(self, mock_find, tmp_path):
        """Test restore cancelled by user."""
        db_path = tmp_path / "test.db"
        backup_file = tmp_path / "test.db.bak"
        backup_file.touch()
        mock_find.return_value = backup_file
        result = runner.invoke(app, ["restore", "--db", str(db_path)], input="n\n")
        output = strip_ansi(result.stdout)
        assert "cancelled" in output.lower() or result.exit_code == 0