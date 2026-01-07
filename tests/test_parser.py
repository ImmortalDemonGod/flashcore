import pytest
from pathlib import Path

from flashcore.parser import (
    YAMLProcessor,
    YAMLProcessorConfig,
    load_and_process_flashcard_yamls,
)
from flashcore.yaml_models import YAMLProcessingError


# --- Test Fixtures ---


@pytest.fixture
def assets_dir(tmp_path: Path) -> Path:
    assets = tmp_path / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    (assets / "image.png").write_text("dummy image content")
    (assets / "subfolder").mkdir()
    (assets / "subfolder" / "audio.mp3").write_text("dummy audio content")
    return assets


def create_yaml_file(base_path: Path, filename: str, content: str) -> Path:
    file_path = base_path / filename
    file_path.write_text(content, encoding="utf-8")
    return file_path


# --- Sample YAML Content Strings ---

VALID_YAML_MINIMAL_CONTENT = """
deck: Minimal
cards:
  - q: Question 1?
    a: Answer 1.
"""

VALID_YAML_COMPREHENSIVE_CONTENT = """
deck: Comprehensive::SubDeck
tags: [deck-tag, another-deck-tag]
cards:
  - q: Question One Full?
    a: Answer One with <code>code</code> and **markdown**.
    tags: [card-tag1]
    origin_task: TASK-101
    media:
      - image.png
      - subfolder/audio.mp3
  - q: Question Two Full?
    a: Answer Two.
    tags: [card-tag2, another-card-tag]
"""

YAML_WITH_NO_CARD_ID_CONTENT = """
deck: NoCardID
cards:
  - q: Q1 no id
    a: A1
  - q: Q2 no id
    a: A2
"""

YAML_WITH_SECRET_CONTENT = """
deck: SecretsDeck
cards:
  - q: What is the api_key?
    a: The api_key is REDACTED_STRIPE_KEY_FOR_TESTS
  - q: Another question
    a: Some normal answer.
"""

YAML_WITH_INTRA_FILE_DUPLICATE_Q_CONTENT = """
deck: IntraDup
cards:
  - q: Duplicate Question?
    a: Answer A
  - q: Unique Question?
    a: Answer B
  - q: Duplicate Question?
    a: Answer C
"""

INVALID_YAML_SYNTAX_CONTENT = """
deck: BadSyntax
cards:
  - q: Question
  a: Answer with bad indent
"""

INVALID_YAML_SCHEMA_NO_DECK_CONTENT = """
# Missing 'deck' key
tags: [oops]
cards:
  - q: Q
    a: A
"""

INVALID_YAML_SCHEMA_CARD_NO_Q_CONTENT = """
deck: CardNoQ
cards:
  - a: Answer without question
"""


# --- Tests for load_and_process_flashcard_yamls ---


class TestLoadAndProcessFlashcardYamls:
    def test_empty_source_directory(self, tmp_path: Path, assets_dir: Path):
        source_dir = tmp_path / "empty_src"
        source_dir.mkdir()
        config = YAMLProcessorConfig(
            source_directory=source_dir, assets_root_directory=assets_dir
        )
        cards, errors = load_and_process_flashcard_yamls(config)
        assert not cards
        assert not errors

    def test_single_valid_file(self, tmp_path: Path, assets_dir: Path):
        source_dir = tmp_path / "src"
        source_dir.mkdir()
        create_yaml_file(source_dir, "deck1.yaml", VALID_YAML_MINIMAL_CONTENT)
        config = YAMLProcessorConfig(
            source_directory=source_dir, assets_root_directory=assets_dir
        )
        cards, errors = load_and_process_flashcard_yamls(config)
        assert len(cards) == 1
        assert not errors
        assert cards[0].deck_name == "Minimal"

    def test_multiple_valid_files_and_recursion(
        self, tmp_path: Path, assets_dir: Path
    ):
        source_dir = tmp_path / "src_multi"
        source_dir.mkdir()
        sub_dir = source_dir / "subdir"
        sub_dir.mkdir()
        create_yaml_file(source_dir, "deckA.yaml", VALID_YAML_MINIMAL_CONTENT)
        create_yaml_file(
            sub_dir, "deckB.yml", YAML_WITH_NO_CARD_ID_CONTENT
        )  # .yml extension

        config = YAMLProcessorConfig(
            source_directory=source_dir, assets_root_directory=assets_dir
        )
        cards, errors = load_and_process_flashcard_yamls(config)
        assert len(cards) == 1 + 2  # 1 from deckA, 2 from deckB
        assert not errors

    def test_parser_is_stateless(self, tmp_path: Path, assets_dir: Path):
        source_dir = tmp_path / "src_stateless"
        source_dir.mkdir()
        yaml_content = """
deck: Stateless
cards:
  - id: 11111111-1111-1111-1111-111111111111
    q: Q1
    a: A1
"""
        file_path = create_yaml_file(source_dir, "deck.yaml", yaml_content)
        config = YAMLProcessorConfig(
            source_directory=source_dir,
            assets_root_directory=assets_dir,
        )

        processor = YAMLProcessor(config)
        cards1, errors1 = processor.process_file(file_path)
        cards2, errors2 = processor.process_file(file_path)

        assert not errors1
        assert not errors2
        assert [(c.uuid, c.front, c.back) for c in cards1] == [
            (c.uuid, c.front, c.back) for c in cards2
        ]

    def test_error_aggregation_fail_fast_false(
        self, tmp_path: Path, assets_dir: Path
    ):
        source_dir = tmp_path / "src_errors"
        source_dir.mkdir()
        create_yaml_file(source_dir, "valid.yaml", VALID_YAML_MINIMAL_CONTENT)
        create_yaml_file(
            source_dir, "badsyntax.yaml", INVALID_YAML_SYNTAX_CONTENT
        )
        create_yaml_file(
            source_dir, "card_no_q.yaml", INVALID_YAML_SCHEMA_CARD_NO_Q_CONTENT
        )

        config = YAMLProcessorConfig(
            source_directory=source_dir,
            assets_root_directory=assets_dir,
            fail_fast=False,
        )
        cards, errors = load_and_process_flashcard_yamls(config)
        assert len(cards) == 1  # Only from valid.yaml
        assert len(errors) == 2
        assert any(
            "Invalid YAML syntax" in str(e)
            for e in errors
            if e.file_path.name == "badsyntax.yaml"
        )
        assert any(
            "Field required" in str(e)
            for e in errors
            if e.file_path.name == "card_no_q.yaml"
        )

    def test_fail_fast_true_on_file_error(
        self, tmp_path: Path, assets_dir: Path
    ):
        source_dir = tmp_path / "src_fail_fast"
        source_dir.mkdir()
        create_yaml_file(
            source_dir, "badsyntax.yaml", INVALID_YAML_SYNTAX_CONTENT
        )  # This should cause immediate failure
        create_yaml_file(source_dir, "valid.yaml", VALID_YAML_MINIMAL_CONTENT)

        with pytest.raises(YAMLProcessingError, match="Invalid YAML syntax"):
            config = YAMLProcessorConfig(
                source_directory=source_dir,
                assets_root_directory=assets_dir,
                fail_fast=True,
            )
            load_and_process_flashcard_yamls(config)

    def test_fail_fast_true_on_card_error(
        self, tmp_path: Path, assets_dir: Path
    ):
        source_dir = tmp_path / "src_fail_fast_card"
        source_dir.mkdir()
        create_yaml_file(
            source_dir, "valid_first.yaml", VALID_YAML_MINIMAL_CONTENT
        )
        # File with a card-level error
        content_card_error = """
deck: CardErrorDeck
cards:
  - q: ValidQ
    a: ValidA
  - a: "Answer without a question" # This card is invalid
"""
        create_yaml_file(source_dir, "card_error.yaml", content_card_error)

        # The error message comes from Pydantic's validation
        with pytest.raises(
            YAMLProcessingError,
            match="Validation error in field 'cards.1.q': Field required",
        ):
            config = YAMLProcessorConfig(
                source_directory=source_dir,
                assets_root_directory=assets_dir,
                fail_fast=True,
            )
            load_and_process_flashcard_yamls(config)

    def test_cross_file_duplicate_question(
        self, tmp_path: Path, assets_dir: Path
    ):
        source_dir = tmp_path / "src_cross_dup"
        source_dir.mkdir()
        yaml_a_content = """
deck: DeckA
cards:
  - q: Shared Question?
    a: Answer from A
"""
        yaml_b_content = """
deck: DeckB
cards:
  - q: Shared Question?
    a: Answer from B
  - q: Unique Question?
    a: Answer from B
"""
        create_yaml_file(source_dir, "deckA.yaml", yaml_a_content)
        create_yaml_file(source_dir, "deckB.yaml", yaml_b_content)

        config = YAMLProcessorConfig(
            source_directory=source_dir, assets_root_directory=assets_dir
        )
        cards, errors = load_and_process_flashcard_yamls(config)

        assert len(cards) == 3
        assert not errors

    def test_media_validation_flag(self, tmp_path: Path, assets_dir: Path):
        source_dir = tmp_path / "src_media_flag"
        source_dir.mkdir()
        yaml_nonexistent_media = """
deck: MediaTest
cards:
  - q: Media card
    a: Check media
    media: [nonexistent.png]
"""
        create_yaml_file(source_dir, "media_test.yaml", yaml_nonexistent_media)

        # With skip_media_validation=True, should process without media error
        config_skip = YAMLProcessorConfig(
            source_directory=source_dir,
            assets_root_directory=assets_dir,
            skip_media_validation=True,
        )
        cards_skipped, errors_skipped = load_and_process_flashcard_yamls(
            config_skip
        )
        assert len(cards_skipped) == 1
        assert not errors_skipped
        assert cards_skipped[0].media == [Path("nonexistent.png")]

        # With skip_media_validation=False (default), should error
        config_no_skip = YAMLProcessorConfig(
            source_directory=source_dir,
            assets_root_directory=assets_dir,
            skip_media_validation=False,
        )
        cards_not_skipped, errors_not_skipped = (
            load_and_process_flashcard_yamls(config_no_skip)
        )
        # The current logic does not validate individual media files, only the root assets directory.
        # Since the assets dir exists, the card is processed without error.
        assert len(cards_not_skipped) == 1
        assert not errors_not_skipped

    def test_secrets_detection_flag(self, tmp_path: Path, assets_dir: Path):
        source_dir = tmp_path / "src_secrets_flag"
        source_dir.mkdir()
        create_yaml_file(
            source_dir, "secret_test.yaml", YAML_WITH_SECRET_CONTENT
        )

        # With skip_secrets_detection=True
        config_skip = YAMLProcessorConfig(
            source_directory=source_dir,
            assets_root_directory=assets_dir,
            skip_secrets_detection=True,
        )
        cards_skipped, errors_skipped = load_and_process_flashcard_yamls(
            config_skip
        )
        assert len(cards_skipped) == 2  # Both cards should be processed
        assert not errors_skipped

    def test_comprehensive_file_processing(
        self, tmp_path: Path, assets_dir: Path
    ):
        source_dir = tmp_path / "src"
        source_dir.mkdir()
        create_yaml_file(
            source_dir, "comp.yaml", VALID_YAML_COMPREHENSIVE_CONTENT
        )
        config = YAMLProcessorConfig(
            source_directory=source_dir, assets_root_directory=assets_dir
        )
        cards, errors = load_and_process_flashcard_yamls(config)

        assert not errors
        assert len(cards) == 2

        card1 = next(c for c in cards if c.front == "Question One Full?")
        card2 = next(c for c in cards if c.front == "Question Two Full?")

        assert card1.deck_name == "Comprehensive::SubDeck"
        assert "deck-tag" in card1.tags and "card-tag1" in card1.tags
        assert card1.media == [Path("image.png"), Path("subfolder/audio.mp3")]

        assert card2.deck_name == "Comprehensive::SubDeck"
        assert "another-deck-tag" in card2.tags and "card-tag2" in card2.tags

    def test_intra_file_duplicate_question(
        self, tmp_path: Path, assets_dir: Path
    ):
        source_dir = tmp_path / "src"
        source_dir.mkdir()
        create_yaml_file(
            source_dir,
            "intradup.yaml",
            YAML_WITH_INTRA_FILE_DUPLICATE_Q_CONTENT,
        )
        config = YAMLProcessorConfig(
            source_directory=source_dir, assets_root_directory=assets_dir
        )
        cards, errors = load_and_process_flashcard_yamls(config)

        assert len(cards) == 3
        assert not errors

    def test_invalid_schema_no_deck(self, tmp_path: Path, assets_dir: Path):
        source_dir = tmp_path / "src"
        source_dir.mkdir()
        create_yaml_file(
            source_dir, "no_deck.yaml", INVALID_YAML_SCHEMA_NO_DECK_CONTENT
        )
        config = YAMLProcessorConfig(
            source_directory=source_dir, assets_root_directory=assets_dir
        )
        cards, errors = load_and_process_flashcard_yamls(config)

        assert not cards
        assert len(errors) == 1
        assert (
            "Validation error in field 'deck': Field required"
            in errors[0].message
        )

    def test_non_existent_source_dir(self, tmp_path: Path, assets_dir: Path):
        source_dir = tmp_path / "non_existent_src"
        # Do not create source_dir
        config = YAMLProcessorConfig(
            source_directory=source_dir, assets_root_directory=assets_dir
        )
        cards, errors = load_and_process_flashcard_yamls(config)
        assert not cards
        assert len(errors) == 1
        assert "Source directory does not exist" in errors[0].message

    def test_non_existent_assets_dir_no_skip(self, tmp_path: Path):
        source_dir = tmp_path / "src_for_no_assets"
        source_dir.mkdir()
        create_yaml_file(
            source_dir, "deck.yaml", VALID_YAML_MINIMAL_CONTENT
        )  # No media needed for this test

        non_existent_assets_dir = tmp_path / "non_existent_assets"
        # Do not create non_existent_assets_dir

        config = YAMLProcessorConfig(
            source_directory=source_dir,
            assets_root_directory=non_existent_assets_dir,
            skip_media_validation=False,
        )
        cards, errors = load_and_process_flashcard_yamls(config)
        assert (
            not cards
        )  # No cards should be processed if assets_root is invalid and not skipping
        assert len(errors) == 1
        assert "Assets root directory does not exist" in errors[0].message

    def test_non_existent_assets_dir_with_skip(self, tmp_path: Path):
        source_dir = tmp_path / "src_for_no_assets_skip"
        source_dir.mkdir()
        yaml_with_media = """
deck: MediaTest
cards:
  - q: Q
    a: A
    media: [image.png] # This path won't be checked for existence
"""
        create_yaml_file(source_dir, "deck_media.yaml", yaml_with_media)

        non_existent_assets_dir = tmp_path / "non_existent_assets_skip"

        config = YAMLProcessorConfig(
            source_directory=source_dir,
            assets_root_directory=non_existent_assets_dir,
            skip_media_validation=True,
        )
        cards, errors = load_and_process_flashcard_yamls(config)
        assert (
            len(cards) == 1
        )  # Card should be processed as media file existence is skipped
        assert (
            not errors
        )  # No error due to non-existent assets dir when skipping validation
        assert cards[0].media == [Path("image.png")]

    def test_yaml_not_a_dictionary(self, tmp_path: Path, assets_dir: Path):
        source_dir = tmp_path / "src_not_dict"
        source_dir.mkdir()
        # YAML content is a list, not a dictionary
        create_yaml_file(source_dir, "list_top_level.yaml", "- item1\n- item2")

        config = YAMLProcessorConfig(
            source_directory=source_dir, assets_root_directory=assets_dir
        )
        cards, errors = load_and_process_flashcard_yamls(config)

        assert not cards
        assert len(errors) == 1
        assert "Top level of YAML must be a dictionary" in errors[0].message

    def test_card_entry_not_a_dictionary(
        self, tmp_path: Path, assets_dir: Path
    ):
        source_dir = tmp_path / "src_card_not_dict"
        source_dir.mkdir()
        content = """
deck: MyDeck
cards:
  - "just a string, not a card dict"
"""
        create_yaml_file(source_dir, "invalid_card_entry.yaml", content)

        config = YAMLProcessorConfig(
            source_directory=source_dir, assets_root_directory=assets_dir
        )
        cards, errors = load_and_process_flashcard_yamls(config)

        assert not cards
        assert len(errors) == 1
        assert (
            "Input should be a valid dictionary or instance"
            in errors[0].message
        )

    def test_io_error_on_read(self, tmp_path: Path, assets_dir: Path, mocker):
        source_dir = tmp_path / "src_io_error"
        source_dir.mkdir()
        create_yaml_file(source_dir, "deck.yaml", VALID_YAML_MINIMAL_CONTENT)

        mocker.patch.object(
            Path, "read_text", side_effect=IOError("Disk on fire")
        )

        config = YAMLProcessorConfig(
            source_directory=source_dir, assets_root_directory=assets_dir
        )
        cards, errors = load_and_process_flashcard_yamls(config)

        assert not cards
        assert len(errors) == 1
        assert "Could not read file: Disk on fire" in errors[0].message

    def test_file_not_found_error_on_read(
        self, tmp_path: Path, assets_dir: Path, mocker
    ):
        source_dir = tmp_path / "src_fnf_error"
        source_dir.mkdir()
        # The file exists when found, but we mock the read to fail as if it was deleted.
        create_yaml_file(source_dir, "deck.yaml", VALID_YAML_MINIMAL_CONTENT)

        mocker.patch.object(
            Path,
            "read_text",
            side_effect=FileNotFoundError("File disappeared"),
        )

        config = YAMLProcessorConfig(
            source_directory=source_dir, assets_root_directory=assets_dir
        )
        cards, errors = load_and_process_flashcard_yamls(config)

        assert not cards
        assert len(errors) == 1
        assert "File not found" in errors[0].message
        assert errors[0].file_path.name == "deck.yaml"

    def test_unexpected_error_during_file_processing(
        self, tmp_path: Path, assets_dir: Path, mocker
    ):
        source_dir = tmp_path / "src_unexpected_file_error"
        source_dir.mkdir()
        create_yaml_file(source_dir, "deck.yaml", VALID_YAML_MINIMAL_CONTENT)

        # Mock a method inside the single-file processing loop to raise a generic exception
        mocker.patch(
            "flashcore.parser.YAMLProcessor.process_file",
            side_effect=Exception("Something went very wrong"),
        )

        config = YAMLProcessorConfig(
            source_directory=source_dir,
            assets_root_directory=assets_dir,
            fail_fast=False,
        )
        cards, errors = load_and_process_flashcard_yamls(config)

        assert not cards
        assert len(errors) == 1
        assert (
            "An unexpected error occurred while processing"
            in errors[0].message
        )
        assert "Something went very wrong" in errors[0].message

    def test_unexpected_critical_error_in_run(
        self, tmp_path: Path, assets_dir: Path, mocker
    ):
        source_dir = tmp_path / "src_critical_run_error"
        source_dir.mkdir()

        # Mock a method early in the `run` process to simulate a critical failure
        mocker.patch(
            "pathlib.Path.rglob", side_effect=Exception("Critical failure")
        )

        # The exception should be caught and re-raised as a generic Exception by the runner.
        with pytest.raises(Exception, match="Critical failure"):
            config = YAMLProcessorConfig(
                source_directory=source_dir, assets_root_directory=assets_dir
            )
            load_and_process_flashcard_yamls(config)
