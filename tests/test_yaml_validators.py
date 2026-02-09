import pytest
import uuid
from pathlib import Path

from flashcore.yaml_validators import (
    validate_card_uuid,
    check_for_secrets,
    validate_media_paths,
    validate_single_media_path,
    validate_directories,
    extract_cards_list,
    validate_raw_card_structure,
    _handle_skipped_media_validation,
    extract_deck_name,
    extract_deck_tags,
    run_card_validation_pipeline,
    sanitize_card_text,
    compile_card_tags,
    validate_deck_and_extract_metadata,
)
from flashcore.yaml_models import (
    _RawYAMLCardEntry,
    _CardProcessingContext,
    YAMLProcessingError,
)


@pytest.fixture
def mock_context(tmp_path):
    """
    Create a mock _CardProcessingContext preconfigured for unit tests.

    Parameters:
        tmp_path (Path): Temporary directory to use as the assets_root_directory.

    Returns:
        _CardProcessingContext: Context with source_file_path set to "/fake/deck.yaml", card_index 0,
        card_q_preview "A test question...", assets_root_directory set to `tmp_path`,
        skip_media_validation False, and skip_secrets_detection False.
    """
    return _CardProcessingContext(
        source_file_path=Path("/fake/deck.yaml"),
        card_index=0,
        card_q_preview="A test question...",
        assets_root_directory=tmp_path,  # Use tmp_path for assets
        skip_media_validation=False,
        skip_secrets_detection=False,
    )


def test_validate_card_uuid_invalid_format(mock_context):
    """Tests that validate_card_uuid returns an error for an invalid UUID string."""
    raw_card = _RawYAMLCardEntry(q="q", a="a", id="not-a-uuid")
    result = validate_card_uuid(raw_card, mock_context)
    assert isinstance(result, YAMLProcessingError)
    assert "Invalid UUID format" in result.message


def test_check_for_secrets_found_in_question(mock_context):
    """Tests that a secret is detected in the question field."""
    mock_context.skip_secrets_detection = False
    # Use a string that matches the length and format of the regex
    secret_string = (
        "api_key: 'this_is_a_super_long_secret_key_that_is_over_20_chars'"
    )
    result = check_for_secrets(secret_string, "answer", mock_context)
    assert isinstance(result, YAMLProcessingError)
    assert "detected in card question" in result.message


def test_check_for_secrets_found_in_answer(mock_context):
    """Tests that a secret is detected in the answer field."""
    mock_context.skip_secrets_detection = False
    # Use a string that matches a specific token format (e.g., GitHub)
    secret_string = (
        "here is a github token ghp_abcdefghijklmnopqrstuvwxyz1234567890abcd"
    )
    result = check_for_secrets("question", secret_string, mock_context)
    assert isinstance(result, YAMLProcessingError)
    assert "detected in card answer" in result.message


def test_validate_single_media_path_nonexistent(mock_context):
    """Tests error when media path does not exist."""
    result = validate_single_media_path("nonexistent.jpg", mock_context)
    assert isinstance(result, YAMLProcessingError)
    assert "Media file not found" in result.message


def test_validate_single_media_path_is_directory(mock_context):
    """Tests error when media path is a directory."""
    (mock_context.assets_root_directory / "a_directory").mkdir()
    result = validate_single_media_path("a_directory", mock_context)
    assert isinstance(result, YAMLProcessingError)
    assert "is a directory, not a file" in result.message


def test_validate_single_media_path_traversal_attack(mock_context):
    """Tests error for directory traversal attempts."""
    result = validate_single_media_path("../outside_assets.jpg", mock_context)
    assert isinstance(result, YAMLProcessingError)
    assert "resolves outside the assets root directory" in result.message


def test_validate_media_paths_with_invalid_item(mock_context):
    """Tests that validate_media_paths returns an error if one item is invalid."""
    (mock_context.assets_root_directory / "good.jpg").touch()
    raw_media = ["good.jpg", "nonexistent.jpg"]
    result = validate_media_paths(raw_media, mock_context)
    assert isinstance(result, YAMLProcessingError)
    assert "nonexistent.jpg" in result.message
    assert "Media file not found" in result.message


def test_validate_directories_source_does_not_exist(tmp_path):
    """Tests error when source directory does not exist."""
    result = validate_directories(Path("/nonexistent/source"), tmp_path, False)
    assert isinstance(result, YAMLProcessingError)
    assert "Source directory does not exist" in result.message


def test_validate_directories_assets_do_not_exist(tmp_path):
    """Tests error when asset directory does not exist and media validation is not skipped."""
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    result = validate_directories(
        source_dir, Path("/nonexistent/assets"), False
    )
    assert isinstance(result, YAMLProcessingError)
    assert "Assets root directory does not exist" in result.message


def test_extract_cards_list_missing():
    """Tests error when 'cards' key is missing."""
    with pytest.raises(
        YAMLProcessingError, match="Missing or invalid 'cards' list"
    ):
        extract_cards_list({}, Path("test.yaml"))


def test_extract_cards_list_empty():
    """Tests error when 'cards' list is empty."""
    with pytest.raises(
        YAMLProcessingError, match="No cards found in 'cards' list"
    ):
        extract_cards_list({"cards": []}, Path("test.yaml"))


def test_validate_raw_card_structure_invalid(tmp_path):
    """Tests that a pydantic validation error is caught and wrapped."""
    invalid_card_dict = {"q": "question"}  # 'a' is missing
    result = validate_raw_card_structure(
        invalid_card_dict, 0, tmp_path / "test.yaml"
    )
    assert isinstance(result, YAMLProcessingError)
    assert "Card validation failed" in result.message


def test_validate_raw_card_structure_not_a_dict(tmp_path):
    """Tests that an error is returned if a card entry is not a dictionary."""
    invalid_card = "just a string"
    result = validate_raw_card_structure(
        invalid_card, 0, tmp_path / "test.yaml"
    )
    assert isinstance(result, YAMLProcessingError)
    assert "Card entry is not a valid dictionary" in result.message


def test_validate_media_paths_not_a_list(mock_context):
    """Tests error when 'media' field is not a list."""
    raw_media = "not_a_list"
    result = validate_media_paths(raw_media, mock_context)
    assert isinstance(result, YAMLProcessingError)
    assert "must be a list of strings" in result.message


def test_handle_skipped_media_validation_not_a_list():
    """Tests that _handle_skipped_media_validation returns an empty list if input is not a list."""
    result = _handle_skipped_media_validation("not_a_list")
    assert result == []


def test_validate_single_media_path_absolute_path(mock_context):
    """Tests error for absolute media paths."""
    result = validate_single_media_path("/abs/path/image.jpg", mock_context)
    assert isinstance(result, YAMLProcessingError)
    assert "Media path must be relative" in result.message


def test_validate_single_media_path_generic_exception(mock_context, mocker):
    """Tests that a generic exception during validation is caught and wrapped."""
    mocker.patch.object(
        Path, "resolve", side_effect=Exception("Unexpected error")
    )
    result = validate_single_media_path("some_file.jpg", mock_context)
    assert isinstance(result, YAMLProcessingError)
    assert "Error validating media path" in result.message


def test_validate_single_media_path_success(mock_context):
    """Tests that a valid media path is validated successfully."""
    # Arrange
    media_file = mock_context.assets_root_directory / "good.jpg"
    media_file.touch()
    media_path = "good.jpg"

    # Act
    result = validate_single_media_path(media_path, mock_context)

    # Assert
    expected_path = (mock_context.assets_root_directory / media_path).resolve()
    assert result == expected_path
    assert not isinstance(result, YAMLProcessingError)


def test_validate_single_media_path_skipped(mock_context):
    """Tests that validation is skipped and a Path object is returned."""
    # Arrange
    mock_context.skip_media_validation = True
    media_path = "nonexistent/and/invalid.jpg"

    # Act
    result = validate_single_media_path(media_path, mock_context)

    # Assert
    assert result == Path(media_path)
    assert not isinstance(result, YAMLProcessingError)


def test_run_card_validation_pipeline_propagates_uuid_error(mock_context):
    """Tests that an error from a child validator is correctly propagated."""
    raw_card = _RawYAMLCardEntry(q="q", a="a", id="not-a-uuid")
    result = run_card_validation_pipeline(raw_card, mock_context, set())
    assert isinstance(result, YAMLProcessingError)
    assert "Invalid UUID format" in result.message


class TestDeckMetadataValidation:
    def test_extract_deck_name_success(self):
        assert (
            extract_deck_name({"deck": " My Deck "}, Path("test.yaml"))
            == "My Deck"
        )

    def test_extract_deck_name_missing(self):
        with pytest.raises(YAMLProcessingError, match="Missing 'deck' field"):
            extract_deck_name({}, Path("test.yaml"))

    def test_extract_deck_name_not_a_string(self):
        with pytest.raises(
            YAMLProcessingError, match="'deck' field must be a string"
        ):
            extract_deck_name({"deck": 123}, Path("test.yaml"))

    def test_extract_deck_name_empty_string(self):
        with pytest.raises(
            YAMLProcessingError, match="'deck' field cannot be empty"
        ):
            extract_deck_name({"deck": "   "}, Path("test.yaml"))

    def test_extract_deck_tags_success(self):
        tags = extract_deck_tags(
            {"tags": [" Tag1 ", "tag2"]}, Path("test.yaml")
        )
        assert tags == {"tag1", "tag2"}

    def test_extract_deck_tags_missing(self):
        assert extract_deck_tags({}, Path("test.yaml")) == set()

    def test_extract_deck_tags_not_a_list(self):
        with pytest.raises(
            YAMLProcessingError, match="'tags' field must be a list"
        ):
            extract_deck_tags({"tags": "not-a-list"}, Path("test.yaml"))


def test_sanitize_card_text():
    """Tests that text is stripped and sanitized."""
    raw_card = _RawYAMLCardEntry(
        q="  <p>Question</p> <script>alert('xss')</script>  ",
        a=" <b>Answer</b>  ",
    )
    front, back = sanitize_card_text(raw_card)
    assert front == "<p>Question</p> alert('xss')"
    assert back == "<b>Answer</b>"


def test_check_for_secrets_skipped(mock_context):
    """Tests that secret scanning is skipped when the flag is set."""
    mock_context.skip_secrets_detection = True
    secret = "ghp_abcdefghijklmnopqrstuvwxyz1234567890abcd"
    result = check_for_secrets(secret, secret, mock_context)
    assert result is None


def test_check_for_secrets_no_secret(mock_context):
    """Tests that no error is returned when no secret is present."""
    result = check_for_secrets(
        "Normal question", "Normal answer", mock_context
    )
    assert result is None


def test_run_card_validation_pipeline_secret_error(mock_context):
    """Tests that a secret error is propagated by the pipeline."""
    secret = "ghp_abcdefghijklmnopqrstuvwxyz1234567890abcd"
    raw_card = _RawYAMLCardEntry(q=secret, a="a")
    result = run_card_validation_pipeline(raw_card, mock_context, set())
    assert isinstance(result, YAMLProcessingError)
    assert "Potential secret detected" in result.message


def test_run_card_validation_pipeline_media_error(mock_context):
    """Tests that a media validation error is propagated by the pipeline."""
    raw_card = _RawYAMLCardEntry(q="q", a="a", media=["nonexistent.jpg"])
    result = run_card_validation_pipeline(raw_card, mock_context, set())
    assert isinstance(result, YAMLProcessingError)
    assert "Media file not found" in result.message


def test_validate_raw_card_structure_maps_front_back(tmp_path):
    """Tests that 'front'/'back' are correctly mapped to 'q'/'a'."""
    card_dict = {"front": "question", "back": "answer"}
    result = validate_raw_card_structure(card_dict, 0, tmp_path / "test.yaml")
    assert isinstance(result, _RawYAMLCardEntry)
    assert result.q == "question"
    assert result.a == "answer"


def test_validate_directories_assets_skipped(tmp_path):
    """Tests that a missing assets dir is ignored if validation is skipped."""
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    result = validate_directories(
        source_dir, Path("/nonexistent/assets"), True
    )
    assert result is None


def test_validate_directories_success(tmp_path):
    """Tests successful validation of existing directories."""
    source_dir = tmp_path / "source"
    assets_dir = tmp_path / "assets"
    source_dir.mkdir()
    assets_dir.mkdir()
    result = validate_directories(source_dir, assets_dir, False)
    assert result is None


def test_compile_card_tags():
    """Tests tag compilation from deck and card levels."""
    deck_tags = {"deck-tag"}
    card_tags = ["card-tag1", "card-tag2"]
    final_tags = compile_card_tags(deck_tags, card_tags)
    assert final_tags == {"deck-tag", "card-tag1", "card-tag2"}


def test_compile_card_tags_no_card_tags():
    """Tests tag compilation with only deck-level tags."""
    deck_tags = {"deck-tag"}
    final_tags = compile_card_tags(deck_tags, None)
    assert final_tags == {"deck-tag"}


class TestValidateDeckAndExtractMetadata:
    def test_success(self):
        """Tests successful extraction of all metadata."""
        raw_content = {
            "deck": "My Deck",
            "tags": ["d1"],
            "cards": [{"q": "q", "a": "a"}],
        }
        deck, tags, cards = validate_deck_and_extract_metadata(
            raw_content, Path("f.yaml")
        )
        assert deck == "My Deck"
        assert tags == {"d1"}
        assert len(cards) == 1

    def test_deck_name_error_propagates(self):
        """Tests that an error from extract_deck_name is propagated."""
        raw_content = {"cards": [{}]}
        with pytest.raises(YAMLProcessingError, match="Missing 'deck' field"):
            validate_deck_and_extract_metadata(raw_content, Path("f.yaml"))

    def test_tags_error_propagates(self):
        """Tests that an error from extract_deck_tags is propagated."""
        raw_content = {"deck": "d", "tags": "not-a-list", "cards": [{}]}
        with pytest.raises(
            YAMLProcessingError, match="'tags' field must be a list"
        ):
            validate_deck_and_extract_metadata(raw_content, Path("f.yaml"))

    def test_cards_list_error_propagates(self):
        """Tests that an error from extract_cards_list is propagated."""
        raw_content = {"deck": "d"}
        with pytest.raises(
            YAMLProcessingError, match="Missing or invalid 'cards' list"
        ):
            validate_deck_and_extract_metadata(raw_content, Path("f.yaml"))


class TestValidationHappyPaths:
    """Tests the successful execution paths of validators."""

    def test_run_card_validation_pipeline_success(self, mock_context):
        """Tests the happy path of the entire card validation pipeline."""
        # Arrange
        media_file = mock_context.assets_root_directory / "test.jpg"
        media_file.touch()
        valid_uuid = uuid.uuid4()
        raw_card = _RawYAMLCardEntry(
            q="  <p>Question</p> ",
            a=" <b>Answer</b>  ",
            id=str(valid_uuid),
            tags=["card-tag"],
            media=["test.jpg"],
        )
        deck_tags = {"deck-tag"}

        # Act
        result = run_card_validation_pipeline(
            raw_card, mock_context, deck_tags
        )

        # Assert
        assert not isinstance(result, YAMLProcessingError)
        res_uuid, res_q, res_a, res_tags, res_media = result
        assert res_uuid == valid_uuid
        assert res_q == "<p>Question</p>"
        assert res_a == "<b>Answer</b>"
        assert res_tags == {"deck-tag", "card-tag"}
        assert len(res_media) == 1
        assert res_media[0].name == "test.jpg"

    def test_validate_card_uuid_success(self, mock_context):
        """Tests that a valid UUID is processed correctly."""
        valid_uuid = uuid.uuid4()
        raw_card = _RawYAMLCardEntry(q="q", a="a", id=str(valid_uuid))
        result = validate_card_uuid(raw_card, mock_context)
        assert result == valid_uuid

    def test_validate_media_paths_success(self, mock_context):
        """Tests that a list of valid media paths is processed correctly."""
        (mock_context.assets_root_directory / "good1.jpg").touch()
        sub_dir = mock_context.assets_root_directory / "sub"
        sub_dir.mkdir(parents=True, exist_ok=True)
        (sub_dir / "good2.png").touch()

        raw_media = ["good1.jpg", "sub/good2.png"]
        result = validate_media_paths(raw_media, mock_context)

        assert not isinstance(result, YAMLProcessingError)
        assert len(result) == 2
        assert result[0].name == "good1.jpg"
        assert result[1].name == "good2.png"
