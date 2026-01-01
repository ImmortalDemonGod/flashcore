import pytest
import uuid
from datetime import datetime, date, timezone, timedelta
from pathlib import Path

from pydantic import ValidationError

from flashcore.models import Card, Review, Session, CardState, Rating


# --- Card Model Tests ---

class TestCardModel:
    def test_card_creation_minimal_required(self):
        """Test Card creation with only absolutely required fields (others have defaults)."""
        card = Card(
            deck_name="Minimal Deck",
            front="Minimal Q?",
            back="Minimal A."
        )
        assert isinstance(card.uuid, uuid.UUID)
        assert card.deck_name == "Minimal Deck"
        assert card.front == "Minimal Q?"
        assert card.back == "Minimal A."
        assert card.tags == set()  # default_factory=set
        assert isinstance(card.added_at, datetime)
        assert card.added_at.tzinfo == timezone.utc
        assert card.origin_task is None
        assert card.media == []
        assert card.source_yaml_file is None
        assert card.internal_note is None

    def test_card_creation_all_fields_valid(self):
        """Test Card creation with all fields populated with valid data."""
        specific_uuid = uuid.uuid4()
        specific_added_at = datetime.now(timezone.utc) - timedelta(days=1)
        card = Card(
            uuid=specific_uuid,
            deck_name="Full Deck::SubDeck",
            front="Comprehensive question with details?",
            back="Comprehensive answer with `code` and **markdown**.",
            tags={"valid-tag", "another-valid-one"},
            added_at=specific_added_at,
            origin_task="TASK-001",
            media=[Path("assets/image.png"), Path("assets/audio.mp3")],
            source_yaml_file=Path("outputs/flashcards/yaml/feature_showcase.yaml"),
            internal_note="This card was programmatically generated."
        )
        assert card.uuid == specific_uuid
        assert card.deck_name == "Full Deck::SubDeck"
        assert card.tags == {"valid-tag", "another-valid-one"}
        assert card.added_at == specific_added_at
        assert card.origin_task == "TASK-001"
        assert card.media == [Path("assets/image.png"), Path("assets/audio.mp3")]
        assert card.source_yaml_file == Path("outputs/flashcards/yaml/feature_showcase.yaml")
        assert card.internal_note == "This card was programmatically generated."

    def test_card_uuid_default_generation(self):
        """Ensure UUIDs are different for different instances if not provided."""
        card1 = Card(deck_name="D1", front="Q1", back="A1")
        card2 = Card(deck_name="D2", front="Q2", back="A2")
        assert card1.uuid != card2.uuid

    def test_card_added_at_default_is_utc_and_recent(self):
        """Ensure added_at default is a recent UTC timestamp."""
        card = Card(deck_name="D", front="Q", back="A")
        now_utc = datetime.now(timezone.utc)
        assert card.added_at.tzinfo == timezone.utc
        assert (now_utc - card.added_at).total_seconds() < 5  # Check it's recent

    @pytest.mark.parametrize("valid_tag_set", [
        set(),
        {"simple"},
        {"tag-with-hyphens"},
        {"tag1", "tag2-more"},
        {"alphanum123", "123tag"}
    ])
    def test_card_tags_valid_kebab_case(self, valid_tag_set):
        card = Card(deck_name="D", front="Q", back="A", tags=valid_tag_set)
        assert card.tags == valid_tag_set

    @pytest.mark.parametrize("invalid_tag_set, expected_error_part", [
        ({"Invalid Tag"}, "Tag 'Invalid Tag' is not in kebab-case."), # Space
        ({"_invalid-start"}, "Tag '_invalid-start' is not in kebab-case."), # Underscore start
        ({"invalid-end-"}, "Tag 'invalid-end-' is not in kebab-case."), # Hyphen end
        ({"UPPERCASE"}, "Tag 'UPPERCASE' is not in kebab-case."), # Uppercase
        ({"tag", 123}, "Input should be a valid string"), # Non-string in set
        ({"valid-tag", "Tag With Space"}, "Tag 'Tag With Space' is not in kebab-case.")
    ])
    def test_card_tags_invalid_format(self, invalid_tag_set, expected_error_part):
        with pytest.raises(ValidationError) as excinfo:
            Card(deck_name="D", front="Q", back="A", tags=invalid_tag_set)
        assert expected_error_part in str(excinfo.value)

    @pytest.mark.parametrize("field, max_len", [("front", 1024), ("back", 1024)])
    def test_card_text_fields_max_length(self, field, max_len):
        long_text = "a" * (max_len + 1)
        valid_text = "a" * max_len

        # Set the other field to a default value not being tested.
        other_field = "back" if field == "front" else "front"
        valid_kwargs = {field: valid_text, other_field: "A"}
        long_kwargs = {field: long_text, other_field: "A"}
        Card(deck_name="D", **valid_kwargs)

        # Test invalid length
        with pytest.raises(ValidationError) as excinfo:
            Card(deck_name="D", **long_kwargs)
        assert f"String should have at most {max_len} characters" in str(excinfo.value)

    def test_card_deck_name_min_length(self):
        with pytest.raises(ValidationError) as excinfo:
            Card(deck_name="", front="Q", back="A")
        assert "String should have at least 1 character" in str(excinfo.value)

    def test_card_extra_fields_forbidden(self):
        """Test that extra fields raise an error due to Config.extra = 'forbid'."""
        with pytest.raises(ValidationError) as excinfo:
            Card(
                deck_name="Deck",
                front="Q",
                back="A",
                unexpected_field="some_value" # type: ignore
            )
        assert "Extra inputs are not permitted" in str(excinfo.value) or \
               "unexpected_field" in str(excinfo.value) # Pydantic v1 vs v2 error msg

    def test_card_validate_assignment(self):
        """Test that validation occurs on attribute assignment if Config.validate_assignment = True."""
        card = Card(deck_name="D", front="Q", back="A")
        with pytest.raises(ValidationError):
            card.front = "a" * 2000 # Exceeds max_length
        with pytest.raises(ValidationError):
            card.tags = {"Invalid Tag"} # type: ignore


# --- Review Model Tests ---

class TestReviewModel:
    def test_review_creation_minimal_required(self, valid_card_uuid):
        """Test Review creation with only absolutely required fields."""
        review = Review(
            card_uuid=valid_card_uuid,
            rating=1, # Hard
            stab_after=1.5,
            diff=5.0,
            next_due=date.today() + timedelta(days=1),
            elapsed_days_at_review=0,
            scheduled_days_interval=1
        )
        assert review.card_uuid == valid_card_uuid
        assert review.rating == 1
        assert isinstance(review.ts, datetime)
        assert review.ts.tzinfo == timezone.utc
        assert review.review_id is None
        assert review.resp_ms is None
        assert review.stab_before is None
        assert review.review_type == "review" # Default

    def test_review_creation_all_fields_valid(self, valid_card_uuid):
        specific_ts = datetime.now(timezone.utc) - timedelta(hours=1)
        review = Review(
            review_id=123,
            card_uuid=valid_card_uuid,
            ts=specific_ts,
            rating=3, # Easy
            resp_ms=2500,
            stab_before=20.0,
            stab_after=50.5,
            diff=2.5,
            next_due=date.today() + timedelta(days=50),
            elapsed_days_at_review=20,
            scheduled_days_interval=50,
            review_type="relearn"
        )
        assert review.review_id == 123
        assert review.ts == specific_ts
        assert review.rating == 3
        assert review.resp_ms == 2500
        assert review.stab_before == 20.0
        assert review.stab_after == 50.5
        assert review.diff == 2.5
        assert review.review_type == "relearn"

    def test_review_ts_default_is_utc_and_recent(self, valid_card_uuid):
        review = Review(card_uuid=valid_card_uuid, rating=1, stab_after=1.0, diff=7.0,
                        next_due=date.today() + timedelta(days=1), elapsed_days_at_review=0,
                        scheduled_days_interval=1)
        now_utc = datetime.now(timezone.utc)
        assert review.ts.tzinfo == timezone.utc
        assert (now_utc - review.ts).total_seconds() < 5

    @pytest.mark.parametrize("valid_rating", [1, 2, 3, 4])
    def test_review_rating_valid(self, valid_card_uuid, valid_rating):
        Review(card_uuid=valid_card_uuid, rating=valid_rating, stab_after=1.0, diff=7.0,
               next_due=date.today() + timedelta(days=1), elapsed_days_at_review=0,
               scheduled_days_interval=1) # Should not raise

    @pytest.mark.parametrize("invalid_rating", [-1, 0, 5, 3.5])
    def test_review_rating_invalid(self, valid_card_uuid, invalid_rating):
        with pytest.raises(ValidationError) as excinfo:
            Review(card_uuid=valid_card_uuid, rating=invalid_rating, stab_after=1.0, diff=7.0, # type: ignore
                   next_due=date.today() + timedelta(days=1), elapsed_days_at_review=0,
                   scheduled_days_interval=1)
        err = str(excinfo.value)
        assert (
            "Input should be a valid integer" in err
            or "ensure this value is" in err
            or "greater than or equal to 1" in err
            or "less than or equal to 4" in err
        )  # Accept Pydantic v2 error messages

    def test_review_resp_ms_validation(self, valid_card_uuid):
        Review(card_uuid=valid_card_uuid, rating=1, resp_ms=0, stab_after=1.0, diff=7.0,
               next_due=date.today() + timedelta(days=1), elapsed_days_at_review=0,
               scheduled_days_interval=1) # Valid: 0
        with pytest.raises(ValidationError):
            Review(card_uuid=valid_card_uuid, rating=1, resp_ms=-100, stab_after=1.0, diff=7.0,
                   next_due=date.today() + timedelta(days=1), elapsed_days_at_review=0,
                   scheduled_days_interval=1)

    def test_review_stab_after_validation(self, valid_card_uuid):
        Review(card_uuid=valid_card_uuid, rating=1, stab_after=0.1, diff=7.0,
               next_due=date.today() + timedelta(days=1), elapsed_days_at_review=0,
               scheduled_days_interval=1) # Valid: 0.1
        with pytest.raises(ValidationError):
            Review(card_uuid=valid_card_uuid, rating=1, stab_after=0.05, diff=7.0,
                   next_due=date.today() + timedelta(days=1), elapsed_days_at_review=0,
                   scheduled_days_interval=1)

    def test_review_elapsed_days_validation(self, valid_card_uuid):
        Review(card_uuid=valid_card_uuid, rating=1, stab_after=1.0, diff=7.0,
               next_due=date.today() + timedelta(days=1), elapsed_days_at_review=0,
               scheduled_days_interval=1) # Valid: 0
        with pytest.raises(ValidationError):
            Review(card_uuid=valid_card_uuid, rating=1, stab_after=1.0, diff=7.0,
                   next_due=date.today() + timedelta(days=1), elapsed_days_at_review=-1,
                   scheduled_days_interval=1)

    def test_review_scheduled_interval_validation(self, valid_card_uuid):
        # Valid: 0 and 1 are now allowed for learning steps.
        Review(card_uuid=valid_card_uuid, rating=1, stab_after=1.0, diff=7.0,
               next_due=date.today(), elapsed_days_at_review=0,
               scheduled_days_interval=0)
        Review(card_uuid=valid_card_uuid, rating=1, stab_after=1.0, diff=7.0,
               next_due=date.today() + timedelta(days=1), elapsed_days_at_review=0,
               scheduled_days_interval=1)

        # Invalid: Negative intervals are not allowed.
        with pytest.raises(ValidationError):
            Review(card_uuid=valid_card_uuid, rating=1, stab_after=1.0, diff=7.0,
                   next_due=date.today() + timedelta(days=1), elapsed_days_at_review=0,
                   scheduled_days_interval=-1)

    @pytest.mark.parametrize("valid_review_type", ["learn", "review", "relearn", "manual", None])
    def test_review_type_valid(self, valid_card_uuid, valid_review_type):
        review = Review(card_uuid=valid_card_uuid, rating=1, stab_after=1.0, diff=7.0,
                        next_due=date.today() + timedelta(days=1), elapsed_days_at_review=0,
                        scheduled_days_interval=1, review_type=valid_review_type)
        assert review.review_type == valid_review_type

    def test_review_type_invalid(self, valid_card_uuid):
        with pytest.raises(ValidationError) as excinfo:
            Review(card_uuid=valid_card_uuid, rating=1, stab_after=1.0, diff=7.0,
                   next_due=date.today() + timedelta(days=1), elapsed_days_at_review=0,
                   scheduled_days_interval=1, review_type="invalid_type")
        assert "Invalid review_type" in str(excinfo.value)

    def test_review_extra_fields_forbidden(self, valid_card_uuid):
        with pytest.raises(ValidationError) as excinfo:
            Review(
                card_uuid=valid_card_uuid,
                rating=1,
                stab_after=1.0,
                diff=7.0,
                next_due=date.today() + timedelta(days=1),
                elapsed_days_at_review=0,
                scheduled_days_interval=1,
                unexpected_field="foo" # type: ignore
            )
        assert "Extra inputs are not permitted" in str(excinfo.value) or \
               "unexpected_field" in str(excinfo.value)


# --- Fixtures ---

@pytest.fixture
def valid_card_uuid() -> uuid.UUID:
    """Provides a valid UUID for review tests."""
    return uuid.uuid4()
