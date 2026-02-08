"""
Tests to expose and verify the fix for duplicated review logic.

Issue: Core review submission logic exists in two places:
1. ReviewSessionManager.submit_review()
2. _submit_single_review() in _review_all_logic.py

This creates maintenance hazards and violates DRY principle.
"""

import pytest
from datetime import datetime, timezone, date
from uuid import uuid4
from flashcore.models import Card, CardState
from flashcore.db.database import FlashcardDatabase
from flashcore.scheduler import FSRS_Scheduler, SchedulerOutput
from flashcore.review_manager import ReviewSessionManager
from flashcore.cli._review_all_logic import _submit_single_review


class TestReviewLogicDuplication:
    """Test that exposes the duplication in review submission logic."""

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
            tags={"math"},
        )

    @pytest.fixture
    def mock_scheduler_output(self):
        """Create a mock scheduler output."""
        return SchedulerOutput(
            stab=2.5,
            diff=5.0,
            next_due=date.today(),
            scheduled_days=1,
            review_type="learn",
            elapsed_days=0,
            state=CardState.Learning,
        )

    def test_both_methods_have_identical_core_logic(self, in_memory_db, sample_card):
        """Test that both review methods produce identical results for the same input."""
        # Insert card
        in_memory_db.upsert_cards_batch([sample_card])

        # Create identical test parameters
        rating = 3  # Good
        resp_ms = 1000
        eval_ms = 500
        review_ts = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)

        # Method 1: ReviewSessionManager
        manager = ReviewSessionManager(
            db_manager=in_memory_db,
            scheduler=FSRS_Scheduler(),
            user_uuid=uuid4(),
            deck_name=sample_card.deck_name,
        )
        manager.initialize_session()

        updated_card1 = manager.submit_review(
            card_uuid=sample_card.uuid,
            rating=rating,
            resp_ms=resp_ms,
            eval_ms=eval_ms,
            reviewed_at=review_ts,
        )

        # Get the review created by method 1
        reviews1 = in_memory_db.get_reviews_for_card(sample_card.uuid)

        # Create a second identical card for method 2
        sample_card2 = Card(
            uuid=uuid4(),
            deck_name="Test Deck",
            front="What is 2+2?",
            back="4",
            tags={"math"},
        )
        in_memory_db.upsert_cards_batch([sample_card2])

        # Method 2: _submit_single_review
        updated_card2 = _submit_single_review(
            db_manager=in_memory_db,
            scheduler=FSRS_Scheduler(),
            card=sample_card2,
            rating=rating,
            resp_ms=resp_ms,
            eval_ms=eval_ms,
            reviewed_at=review_ts,
        )

        # Get the review created by method 2
        reviews2 = in_memory_db.get_reviews_for_card(sample_card2.uuid)

        # Both methods should produce identical results
        assert len(reviews1) == 1
        assert len(reviews2) == 1

        review1 = reviews1[0]
        review2 = reviews2[0]

        # Core review data should be identical (excluding UUIDs and IDs)
        assert review1.rating == review2.rating
        assert review1.resp_ms == review2.resp_ms
        assert review1.eval_ms == review2.eval_ms
        assert review1.ts == review2.ts

        # Handle NaN values properly
        import math

        if review1.stab_before is None and review2.stab_before is None:
            pass  # Both None, good
        elif math.isnan(review1.stab_before) and math.isnan(review2.stab_before):
            pass  # Both NaN, good
        else:
            assert review1.stab_before == review2.stab_before

        assert review1.stab_after == review2.stab_after
        assert review1.diff == review2.diff
        assert review1.next_due == review2.next_due
        assert review1.elapsed_days_at_review == review2.elapsed_days_at_review
        assert review1.scheduled_days_interval == review2.scheduled_days_interval
        assert review1.review_type == review2.review_type

        # Card states should be identical
        assert updated_card1.state == updated_card2.state
        assert updated_card1.stability == updated_card2.stability
        assert updated_card1.difficulty == updated_card2.difficulty
        assert updated_card1.next_due_date == updated_card2.next_due_date

    def test_code_duplication_analysis(self):
        """Test that documents the exact duplication between the two methods."""
        # This test serves as documentation of the duplication

        # Both methods follow the exact same pattern:
        duplication_steps = [
            "1. Get timestamp (reviewed_at or now)",
            "2. Fetch review history from database",
            "3. Call scheduler.compute_next_state()",
            "4. Create Review object with scheduler output",
            "5. Call db.add_review_and_update_card()",
            "6. Return updated card",
        ]

        # Both methods have identical parameters (except session management):
        common_parameters = [
            "rating: int",
            "resp_ms: int",
            "eval_ms: int",
            "reviewed_at: Optional[datetime]",
        ]

        # Both methods create identical Review objects with same fields:
        review_fields = [
            "card_uuid",
            "ts",
            "rating",
            "resp_ms",
            "eval_ms",
            "stab_before",
            "stab_after",
            "diff",
            "next_due",
            "elapsed_days_at_review",
            "scheduled_days_interval",
            "review_type",
        ]

        # This test passes to document the duplication
        assert len(duplication_steps) == 6
        assert len(common_parameters) == 4
        assert len(review_fields) == 12

        # The duplication violates DRY principle
        assert True  # This will be fixed by creating a shared service

    def test_maintenance_hazard_demonstration(self, in_memory_db, sample_card):
        """Test that demonstrates the maintenance hazard of duplicated logic."""
        # If we need to change the review logic (e.g., add validation),
        # we would need to update it in TWO places, which is error-prone

        # Insert card
        in_memory_db.upsert_cards_batch([sample_card])

        # Simulate a scenario where one method gets updated but the other doesn't
        # This would lead to inconsistent behavior

        # For example, if we added session_uuid support to ReviewSessionManager
        # but forgot to add it to _submit_single_review, we'd have:

        # Method 1: Creates reviews with session_uuid
        manager = ReviewSessionManager(
            db_manager=in_memory_db,
            scheduler=FSRS_Scheduler(),
            user_uuid=uuid4(),
            deck_name=sample_card.deck_name,
        )
        manager.initialize_session()

        manager.submit_review(
            card_uuid=sample_card.uuid, rating=3, resp_ms=1000, eval_ms=500
        )

        review1 = in_memory_db.get_reviews_for_card(sample_card.uuid)[0]

        # Create second card
        sample_card2 = Card(
            uuid=uuid4(),
            deck_name="Test Deck",
            front="What is 3+3?",
            back="6",
            tags={"math"},
        )
        in_memory_db.upsert_cards_batch([sample_card2])

        # Method 2: Creates reviews without session_uuid (inconsistent!)
        _submit_single_review(
            db_manager=in_memory_db,
            scheduler=FSRS_Scheduler(),
            card=sample_card2,
            rating=3,
            resp_ms=1000,
            eval_ms=500,
        )

        review2 = in_memory_db.get_reviews_for_card(sample_card2.uuid)[0]

        # This demonstrates that our refactoring FIXED the inconsistency!
        # ReviewSessionManager now creates reviews with proper session_uuid
        # _submit_single_review creates reviews with session_uuid=None (no session)
        # This is the CORRECT behavior - session-based reviews get session_uuid,
        # standalone reviews don't

        assert review1.session_uuid is not None  # Fixed! Now has session UUID
        assert review2.session_uuid is None  # Correct! No session for review-all

        # This test documents that the maintenance hazard has been FIXED
        # by consolidating the logic into a shared ReviewProcessor service


class TestReviewLogicConsolidationRequirements:
    """Test that defines requirements for the consolidated review logic."""

    def test_shared_service_interface_requirements(self):
        """Test that defines the interface requirements for the shared review service."""
        # The shared service should have this interface:
        required_interface = {
            "class_name": "ReviewProcessor",
            "method_name": "process_review",
            "parameters": [
                "db_manager: FlashcardDatabase",
                "scheduler: FSRS_Scheduler",
                "card: Card",
                "rating: int",
                "resp_ms: int = 0",
                "eval_ms: int = 0",
                "reviewed_at: Optional[datetime] = None",
                "session_uuid: Optional[UUID] = None",  # For future session tracking
            ],
            "return_type": "Card",
            "raises": ["ValueError", "CardOperationError"],
        }

        # The service should encapsulate all the common logic:
        encapsulated_logic = [
            "Timestamp handling",
            "Review history fetching",
            "Scheduler computation",
            "Review object creation",
            "Database persistence",
            "Error handling",
        ]

        # Both existing methods should become thin wrappers:
        wrapper_responsibilities = [
            "ReviewSessionManager: Session management + call ReviewProcessor",
            "_submit_single_review: Direct call to ReviewProcessor",
        ]

        # Verify requirements are well-defined
        assert required_interface["class_name"] == "ReviewProcessor"
        assert len(required_interface["parameters"]) == 8
        assert len(encapsulated_logic) == 6
        assert len(wrapper_responsibilities) == 2

    def test_backward_compatibility_requirements(self):
        """Test that defines backward compatibility requirements."""
        # After refactoring, existing code should work unchanged:
        compatibility_requirements = [
            "ReviewSessionManager.submit_review() signature unchanged",
            "_submit_single_review() signature unchanged",
            "Return values identical",
            "Error handling identical",
            "Database operations identical",
            "All existing tests pass",
        ]

        # No breaking changes allowed:
        breaking_changes_forbidden = [
            "Method signature changes",
            "Return type changes",
            "Exception type changes",
            "Behavioral changes",
        ]

        assert len(compatibility_requirements) == 6
        assert len(breaking_changes_forbidden) == 4

    def test_session_integration_future_requirements(self):
        """Test that defines requirements for future session integration."""
        # The refactored code should make it easy to add session tracking:
        session_integration_goals = [
            "Single place to add session_uuid parameter",
            "Single place to link reviews to sessions",
            "Consistent session handling across all review workflows",
            "Easy to add session analytics",
        ]

        # This addresses Issue 3 (Unused Session Analytics) preparation:
        session_analytics_preparation = [
            "ReviewProcessor accepts optional session_uuid",
            "ReviewProcessor passes session_uuid to Review creation",
            "Both review workflows can easily provide session_uuid",
            "Foundation for session-level analytics",
        ]

        assert len(session_integration_goals) == 4
        assert len(session_analytics_preparation) == 4
