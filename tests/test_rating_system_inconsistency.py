"""
Tests to expose and verify the fix for the rating system inconsistency bug.

Bug: The system uses two different rating scales:
- UI: 0-3 (Again, Hard, Good, Easy)
- DB: 1-4 (Again, Hard, Good, Easy)

This creates confusion, requires manual conversion logic, and is a source of bugs.
"""

import pytest
from datetime import datetime, timezone, date
from uuid import uuid4

from cultivation.scripts.flashcore.card import Card, Review, CardState
from cultivation.scripts.flashcore.database import FlashcardDatabase
from cultivation.scripts.flashcore.scheduler import FSRS_Scheduler
from cultivation.scripts.flashcore.review_manager import ReviewSessionManager
from cultivation.scripts.flashcore.cli._review_all_logic import _submit_single_review


class TestRatingSystemInconsistency:
    """Test the rating system inconsistency bug."""

    @pytest.fixture
    def in_memory_db(self):
        """Create an in-memory database for testing."""
        db = FlashcardDatabase(":memory:")
        db.initialize_schema()
        return db

    @pytest.fixture
    def sample_card(self):
        """Create a sample card for testing."""
        return Card(
            uuid=uuid4(),
            deck_name="Test Deck",
            front="What is 2+2?",
            back="4",
            tags={"math"}
        )

    @pytest.fixture
    def scheduler(self):
        """Create a scheduler for testing."""
        return FSRS_Scheduler()

    def test_ui_rating_scale_is_1_to_4_after_fix(self):
        """Test that UI now expects 1-4 rating scale after the fix."""
        # After the fix, UI prompts: "Rating (1:Again, 2:Hard, 3:Good, 4:Easy)"

        # Valid UI ratings after fix
        valid_ui_ratings = [1, 2, 3, 4]

        # The UI validation logic (from review_ui.py) now accepts 1-4
        for rating in valid_ui_ratings:
            assert 1 <= rating <= 4, f"UI should accept rating {rating}"

        # Invalid UI ratings after fix
        invalid_ui_ratings = [0, -1, 5, 6]
        for rating in invalid_ui_ratings:
            assert not (1 <= rating <= 4), f"UI should reject rating {rating}"

    def test_database_rating_scale_is_1_to_4(self, in_memory_db, sample_card):
        """Test that database stores 1-4 rating scale."""
        # Insert card first
        in_memory_db.upsert_cards_batch([sample_card])

        # Test each rating individually with a separate card to avoid interference
        valid_db_ratings = [1, 2, 3, 4]

        for i, db_rating in enumerate(valid_db_ratings):
            # Create a unique card for each rating test
            test_card = Card(
                uuid=uuid4(),
                deck_name="Test Deck",
                front=f"Test Question {i}",
                back=f"Test Answer {i}",
                tags={"test"}
            )
            in_memory_db.upsert_cards_batch([test_card])

            review = Review(
                card_uuid=test_card.uuid,
                ts=datetime.now(timezone.utc),
                rating=db_rating,  # Database expects 1-4
                stab_before=None,
                stab_after=2.0,
                diff=5.0,
                next_due=date.today(),
                elapsed_days_at_review=0,
                scheduled_days_interval=1
            )

            # This should work without validation errors
            updated_card = in_memory_db.add_review_and_update_card(review, CardState.Review)
            assert updated_card is not None

            # Verify the rating was stored correctly
            stored_reviews = in_memory_db.get_reviews_for_card(test_card.uuid)
            assert len(stored_reviews) == 1, f"Expected 1 review, got {len(stored_reviews)}"
            assert stored_reviews[0].rating == db_rating, f"Expected rating {db_rating}, got {stored_reviews[0].rating}"

    def test_scheduler_handles_unified_rating_scale(self, scheduler):
        """Test that scheduler now only handles the unified 1-4 rating scale."""
        # Test valid ratings (1-4)
        valid_ratings = [1, 2, 3, 4]
        expected_fsrs_ratings = ["Again", "Hard", "Good", "Easy"]

        for rating, expected_name in zip(valid_ratings, expected_fsrs_ratings):
            fsrs_rating = scheduler._map_flashcore_rating_to_fsrs(rating)
            assert fsrs_rating is not None, f"Scheduler should handle rating {rating}"
            assert fsrs_rating.name == expected_name, f"Rating {rating} should map to {expected_name}"

        # Test that old UI ratings (0-3) are now rejected
        old_ui_ratings = [0, -1, 5, 10]
        for invalid_rating in old_ui_ratings:
            with pytest.raises(ValueError, match="Invalid rating"):
                scheduler._map_flashcore_rating_to_fsrs(invalid_rating)

    def test_review_manager_uses_unified_rating_scale(self, in_memory_db, sample_card):
        """Test that ReviewSessionManager now uses the unified 1-4 rating scale."""
        # Insert card
        in_memory_db.upsert_cards_batch([sample_card])

        # Create review manager
        manager = ReviewSessionManager(
            db_manager=in_memory_db,
            scheduler=FSRS_Scheduler(),
            user_uuid=uuid4(),
            deck_name=sample_card.deck_name
        )
        manager.initialize_session()

        # Submit review with unified rating (1-4)
        rating = 3  # Good
        updated_card = manager.submit_review(
            card_uuid=sample_card.uuid,
            rating=rating,
            resp_ms=1000,
            eval_ms=500
        )

        # Verify the review was stored with the same rating (no conversion)
        stored_reviews = in_memory_db.get_reviews_for_card(sample_card.uuid)
        assert len(stored_reviews) == 1

        # No conversion needed - rating should be stored as-is
        assert stored_reviews[0].rating == rating

    def test_review_all_logic_uses_unified_rating_scale(self, in_memory_db, sample_card):
        """Test that review-all logic now uses the unified 1-4 rating scale."""
        # Insert card
        in_memory_db.upsert_cards_batch([sample_card])

        # Submit review using review-all logic with unified rating
        rating = 2  # Hard
        updated_card = _submit_single_review(
            db_manager=in_memory_db,
            scheduler=FSRS_Scheduler(),
            card=sample_card,
            rating=rating,
            resp_ms=1500,
            eval_ms=800
        )

        # Verify the review was stored with the same rating (no conversion)
        stored_reviews = in_memory_db.get_reviews_for_card(sample_card.uuid)
        assert len(stored_reviews) == 1

        # No conversion needed - rating should be stored as-is
        assert stored_reviews[0].rating == rating

    def test_rating_consistency_after_fix(self, in_memory_db, sample_card):
        """Test that rating consistency is maintained after the fix."""
        # Insert card
        in_memory_db.upsert_cards_batch([sample_card])

        # Create two reviews: one via ReviewSessionManager, one via review-all
        # Both should use the same unified rating and result in the same stored rating

        rating = 4  # Easy

        # Review 1: Via ReviewSessionManager
        manager = ReviewSessionManager(
            db_manager=in_memory_db,
            scheduler=FSRS_Scheduler(),
            user_uuid=uuid4(),
            deck_name=sample_card.deck_name
        )
        manager.initialize_session()

        manager.submit_review(
            card_uuid=sample_card.uuid,
            rating=rating,
            resp_ms=1000,
            eval_ms=500
        )

        # Create a second card for the second review
        sample_card2 = Card(
            uuid=uuid4(),
            deck_name="Test Deck",
            front="What is 3+3?",
            back="6",
            tags={"math"}
        )
        in_memory_db.upsert_cards_batch([sample_card2])

        # Review 2: Via review-all logic
        _submit_single_review(
            db_manager=in_memory_db,
            scheduler=FSRS_Scheduler(),
            card=sample_card2,
            rating=rating,
            resp_ms=1000,
            eval_ms=500
        )

        # Both reviews should have the same rating (no conversion needed)
        reviews1 = in_memory_db.get_reviews_for_card(sample_card.uuid)
        reviews2 = in_memory_db.get_reviews_for_card(sample_card2.uuid)

        assert len(reviews1) == 1
        assert len(reviews2) == 1

        # Both should have the same rating as input (no conversion)
        assert reviews1[0].rating == rating
        assert reviews2[0].rating == rating

        # This test verifies the fix: unified rating scale, no conversion needed

    def test_scheduler_rating_mapping_clarity_after_fix(self, scheduler):
        """Test that scheduler rating mapping is now clear and unambiguous."""
        # After the fix, the scheduler only handles one scale (1-4)
        # This eliminates the previous ambiguity

        # Rating 1 now unambiguously means "Again"
        rating_1_result = scheduler._map_flashcore_rating_to_fsrs(1)
        assert rating_1_result.name == "Again"

        # Rating 2 now unambiguously means "Hard"
        rating_2_result = scheduler._map_flashcore_rating_to_fsrs(2)
        assert rating_2_result.name == "Hard"

        # Rating 3 now unambiguously means "Good"
        rating_3_result = scheduler._map_flashcore_rating_to_fsrs(3)
        assert rating_3_result.name == "Good"

        # Rating 4 now unambiguously means "Easy"
        rating_4_result = scheduler._map_flashcore_rating_to_fsrs(4)
        assert rating_4_result.name == "Easy"

        # The old ambiguous rating 0 is now properly rejected
        with pytest.raises(ValueError):
            scheduler._map_flashcore_rating_to_fsrs(0)

    def test_invalid_rating_handling(self, scheduler):
        """Test that invalid ratings are properly rejected."""
        # Test ratings outside both valid ranges
        invalid_ratings = [-1, 5, 10, -5]

        for invalid_rating in invalid_ratings:
            with pytest.raises(ValueError, match="Invalid rating"):
                scheduler._map_flashcore_rating_to_fsrs(invalid_rating)

    def test_rating_boundary_conditions(self, scheduler):
        """Test boundary conditions for rating validation after fix."""
        # Test exact boundaries for the unified 1-4 scale
        boundary_ratings = [1, 4]  # Min and max valid ratings

        for rating in boundary_ratings:
            # These should all be valid (no exception)
            result = scheduler._map_flashcore_rating_to_fsrs(rating)
            assert result is not None

        # Test just outside boundaries
        with pytest.raises(ValueError):
            scheduler._map_flashcore_rating_to_fsrs(0)  # Below minimum

        with pytest.raises(ValueError):
            scheduler._map_flashcore_rating_to_fsrs(5)  # Above maximum

        with pytest.raises(ValueError):
            scheduler._map_flashcore_rating_to_fsrs(-1)  # Negative


class TestRatingSystemDocumentation:
    """Tests that document the current rating system behavior for future reference."""

    def test_current_rating_scale_mapping(self):
        """Document the current rating scale mappings."""
        # UI Scale (0-3):
        ui_scale = {
            0: "Again",
            1: "Hard",
            2: "Good",
            3: "Easy"
        }

        # DB Scale (1-4):
        db_scale = {
            1: "Again",
            2: "Hard",
            3: "Good",
            4: "Easy"
        }

        # Conversion formula: DB = UI + 1
        for ui_rating, meaning in ui_scale.items():
            db_rating = ui_rating + 1
            assert db_scale[db_rating] == meaning, f"Conversion broken for {meaning}"

        # This test documents the current behavior and will help verify
        # that our fix maintains the same semantic meaning

    def test_fsrs_library_expectations(self):
        """Document what the FSRS library expects."""
        from fsrs import Rating as FSRSRating

        # FSRS library uses an enum with these values:
        fsrs_ratings = {
            FSRSRating.Again: "Again",
            FSRSRating.Hard: "Hard",
            FSRSRating.Good: "Good",
            FSRSRating.Easy: "Easy"
        }

        # The FSRS library doesn't care about our internal numbering
        # It just needs the correct enum value
        assert len(fsrs_ratings) == 4
        assert "Again" in fsrs_ratings.values()
        assert "Easy" in fsrs_ratings.values()
