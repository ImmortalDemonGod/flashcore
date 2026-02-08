"""
Tests for the flashcard export logic.
"""

import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from flashcore.models import Card
from flashcore.cli._export_logic import export_to_markdown
from flashcore.db.database import FlashcardDatabase


@pytest.fixture
def mock_db():
    """Fixture for a mocked FlashcardDatabase."""
    return MagicMock(spec=FlashcardDatabase)


@pytest.fixture
def sample_cards():
    """Fixture for a list of sample Card objects."""
    return [
        Card(front="Q1", back="A1", deck_name="Deck 1", tags={"tag1", "tag2"}),
        Card(front="Q3", back="A3", deck_name="Deck 2"),
        Card(front="Q2", back="A2", deck_name="Deck 1", tags={"tag3"}),
    ]


def test_export_to_markdown_success(mock_db, sample_cards, tmp_path):
    """Test successful export of multiple cards to Markdown files."""
    mock_db.get_all_cards.return_value = sample_cards
    output_dir = tmp_path / "export"

    export_to_markdown(mock_db, output_dir)

    deck1_file = output_dir / "Deck 1.md"
    deck2_file = output_dir / "Deck 2.md"

    assert output_dir.exists()
    assert deck1_file.exists()
    assert deck2_file.exists()

    deck1_content = deck1_file.read_text(encoding="utf-8")
    assert "# Deck: Deck 1" in deck1_content
    assert "**Front:** Q1" in deck1_content
    assert "**Tags:** `tag1, tag2`" in deck1_content
    assert "**Front:** Q2" in deck1_content
    assert "**Tags:** `tag3`" in deck1_content
    # Check sorting
    assert deck1_content.find("Q1") < deck1_content.find("Q2")

    deck2_content = deck2_file.read_text(encoding="utf-8")
    assert "# Deck: Deck 2" in deck2_content
    assert "**Front:** Q3" in deck2_content
    assert "**Tags:**" not in deck2_content


def test_export_to_markdown_no_cards(mock_db, tmp_path, caplog):
    """Test export when there are no cards in the database."""
    mock_db.get_all_cards.return_value = []
    output_dir = tmp_path / "export"

    with caplog.at_level(logging.WARNING):
        export_to_markdown(mock_db, output_dir)

    assert not any(output_dir.iterdir())
    assert "No cards found in the database to export." in caplog.text


def test_export_to_markdown_deck_name_sanitization(mock_db, tmp_path):
    """Test that deck names are sanitized for filenames."""
    cards = [Card(front="Q", back="A", deck_name="Deck / With: Chars?")]
    mock_db.get_all_cards.return_value = cards
    output_dir = tmp_path / "export"

    export_to_markdown(mock_db, output_dir)

    expected_file = output_dir / "Deck  With Chars.md"
    assert expected_file.exists()


def test_export_to_markdown_dir_creation_error(mock_db, tmp_path, mocker):
    """Test that an IOError is raised if the output directory cannot be created."""
    output_dir = tmp_path / "export"
    mocker.patch.object(Path, "mkdir", side_effect=OSError("Permission denied"))

    with pytest.raises(IOError, match="Failed to create output directory"):
        export_to_markdown(mock_db, output_dir)


def test_export_to_markdown_file_write_error(mock_db, sample_cards, tmp_path, caplog):
    """Test that the export continues if one file fails to write."""
    mock_db.get_all_cards.return_value = sample_cards
    output_dir = tmp_path / "export"

    # Let Deck 1 write, but fail on Deck 2
    original_open = open

    def mock_open(file, *args, **kwargs):
        if "Deck 2" in str(file):
            raise IOError("Disk full")
        return original_open(file, *args, **kwargs)

    with caplog.at_level(logging.ERROR):
        with patch("builtins.open", mock_open):
            export_to_markdown(mock_db, output_dir)

    assert (output_dir / "Deck 1.md").exists()
    assert not (output_dir / "Deck 2.md").exists()
    assert "Could not write to file" in caplog.text
    assert "Disk full" in caplog.text


def test_export_to_markdown_unnamed_deck_fallback(mock_db, tmp_path):
    """Test that deck names with only special chars get 'unnamed_deck' filename."""
    cards = [Card(front="Q", back="A", deck_name="@#$%^&*")]
    mock_db.get_all_cards.return_value = cards
    output_dir = tmp_path / "export"

    export_to_markdown(mock_db, output_dir)

    expected_file = output_dir / "unnamed_deck.md"
    assert expected_file.exists()
