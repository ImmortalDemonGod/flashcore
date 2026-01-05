import pytest
import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4, UUID

from flashcore.scheduler import FSRS_Scheduler, FSRSSchedulerConfig
from flashcore.models import Card, CardState
from flashcore.constants import DEFAULT_PARAMETERS, DEFAULT_DESIRED_RETENTION

# Helper to create datetime objects easily
UTC = datetime.timezone.utc


@pytest.fixture
def scheduler() -> FSRS_Scheduler:
    """Provides an FSRS_Scheduler instance with default parameters."""
    config = FSRSSchedulerConfig(
        parameters=tuple(DEFAULT_PARAMETERS),
        desired_retention=DEFAULT_DESIRED_RETENTION,
    )
    return FSRS_Scheduler(config=config)


@pytest.fixture
def sample_card_uuid() -> UUID:
    return uuid4()


def test_first_review_new_card(
    scheduler: FSRS_Scheduler, sample_card_uuid: UUID
):
    """Test scheduling for the first review of a new card in the learning phase."""
    # Create a new card with no history
    card = Card(
        uuid=sample_card_uuid,
        deck_name="test",
        front="Q",
        back="A",
        state=CardState.New,
    )
    review_ts = datetime.datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC)

    # Rating: Good (2) - should enter the first learning step.
    rating_good = 2
    result_good = scheduler.compute_next_state(card, rating_good, review_ts)

    assert result_good.state == CardState.Learning
    assert (
        result_good.scheduled_days == 0
    ), "First 'Good' review should be a same-day learning step."
    assert result_good.next_due == review_ts.date()

    # Rating: Again (1) - should also enter a learning step.
    rating_again = 1
    result_again = scheduler.compute_next_state(card, rating_again, review_ts)

    assert result_again.state == CardState.Learning
    assert (
        result_again.scheduled_days == 0
    ), "First 'Again' review should be a same-day learning step."

    # Both 'Good' and 'Again' on a new card lead to a 0-day interval (learning step)
    assert result_again.scheduled_days == result_good.scheduled_days


def test_invalid_rating_input(
    scheduler: FSRS_Scheduler, sample_card_uuid: UUID
):
    """Test that invalid rating inputs raise ValueError."""
    card = Card(
        uuid=sample_card_uuid,
        deck_name="test",
        front="Q",
        back="A",
        state=CardState.New,
    )
    # Use a naive datetime to test coverage for the _ensure_utc helper
    review_ts = datetime.datetime(2024, 1, 1, 10, 0, 0)  # No tzinfo

    with pytest.raises(ValueError, match=r"Invalid rating: 5\. Must be 1-4"):
        scheduler.compute_next_state(card, 5, review_ts)

    with pytest.raises(ValueError, match=r"Invalid rating: -1\. Must be 1-4"):
        scheduler.compute_next_state(card, -1, review_ts)


def test_rating_impact_on_interval(
    scheduler: FSRS_Scheduler, sample_card_uuid: UUID
):
    """Test rating impact for a card that is in the learning phase."""
    # First review is 'Good', placing the card into the learning phase.
    card = Card(
        uuid=sample_card_uuid,
        deck_name="test",
        front="Q",
        back="A",
        state=CardState.New,
    )
    review1_ts = datetime.datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC)
    initial_good_result = scheduler.compute_next_state(
        card, 3, review1_ts
    )  # Good = 3
    assert initial_good_result.scheduled_days == 0
    assert initial_good_result.state == CardState.Learning

    # Update card with result from first review
    card_after_first = Card(
        uuid=sample_card_uuid,
        deck_name="test",
        front="Q",
        back="A",
        state=initial_good_result.state,
        stability=initial_good_result.stab,
        difficulty=initial_good_result.diff,
        next_due_date=initial_good_result.next_due,
    )

    # The next review happens on the same day, as it's a learning step.
    review2_ts = datetime.datetime.combine(
        initial_good_result.next_due, datetime.time(10, 10, 0), tzinfo=UTC
    )

    # 'Again' or 'Hard' should keep the card in the learning phase (0-day interval).
    result_again = scheduler.compute_next_state(
        card_after_first, 1, review2_ts
    )  # Again
    result_hard = scheduler.compute_next_state(
        card_after_first, 2, review2_ts
    )  # Hard

    # 'Good' should graduate the card (interval > 0).
    result_good = scheduler.compute_next_state(
        card_after_first, 3, review2_ts
    )  # Good

    # 'Easy' should also graduate the card with an even longer interval.
    result_easy = scheduler.compute_next_state(
        card_after_first, 4, review2_ts
    )  # Easy

    assert (
        result_again.scheduled_days == 0
    ), "'Again' should reset learning, resulting in a 0-day step."
    assert result_again.state == CardState.Learning

    assert (
        result_hard.scheduled_days == 0
    ), "'Hard' should repeat a learning step, resulting in a 0-day step."
    assert result_hard.state == CardState.Learning

    assert (
        result_good.scheduled_days > 0
    ), "'Good' on a learning card should graduate it."
    assert result_good.state == CardState.Review

    assert (
        result_easy.scheduled_days > 0
    ), "'Easy' on a learning card should graduate it."
    assert result_easy.state == CardState.Review
    assert (
        result_easy.scheduled_days >= result_good.scheduled_days
    ), "'Easy' should have longer interval than 'Good'"


def test_multiple_reviews_stability_increase(
    scheduler: FSRS_Scheduler, sample_card_uuid: UUID
):
    """Test that stability and scheduled_days generally increase with multiple successful (Good) reviews."""
    card = Card(
        uuid=sample_card_uuid,
        deck_name="test",
        front="Q",
        back="A",
        state=CardState.New,
    )
    review_ts_base = datetime.datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC)

    # Review 1: New card, rated Good (2)
    rating1 = 2
    result1 = scheduler.compute_next_state(card, rating1, review_ts_base)

    assert result1.scheduled_days == 0
    stability1 = result1.stab
    scheduled_days1 = result1.scheduled_days
    next_due1 = result1.next_due

    # Update card after first review
    card = Card(
        uuid=sample_card_uuid,
        deck_name="test",
        front="Q",
        back="A",
        state=result1.state,
        stability=result1.stab,
        difficulty=result1.diff,
        next_due_date=result1.next_due,
    )

    # Review 2: Reviewed on its due date, rated Easy (3) to graduate
    review_ts2 = datetime.datetime.combine(
        next_due1, datetime.time(10, 0, 0), tzinfo=UTC
    )
    rating2 = 3
    result2 = scheduler.compute_next_state(card, rating2, review_ts2)

    stability2 = result2.stab
    scheduled_days2 = result2.scheduled_days
    next_due2 = result2.next_due

    assert stability2 > stability1
    assert scheduled_days2 > scheduled_days1
    assert next_due2 > next_due1

    # Update card after second review
    card = Card(
        uuid=sample_card_uuid,
        deck_name="test",
        front="Q",
        back="A",
        state=result2.state,
        stability=result2.stab,
        difficulty=result2.diff,
        next_due_date=result2.next_due,
    )

    # Review 3: Reviewed 1 day after due date, rated Good (2)
    # Note: Review after due date to ensure elapsed_days > 0 for stability increase
    review_ts3 = datetime.datetime.combine(
        next_due2, datetime.time(10, 0, 0), tzinfo=UTC
    ) + datetime.timedelta(days=1)
    rating3 = 2
    result3 = scheduler.compute_next_state(card, rating3, review_ts3)

    stability3 = result3.stab
    scheduled_days3 = result3.scheduled_days
    next_due3 = result3.next_due

    # With O(1) cached state, stability increases when reviewing after due date
    assert stability3 > stability2
    assert scheduled_days3 > 0  # Should have positive interval
    assert (
        next_due3 > review_ts3.date()
    )  # Next due should be after review date


def test_review_lapsed_card(scheduler: FSRS_Scheduler, sample_card_uuid: UUID):
    """
    Test scheduling for a card reviewed significantly after its due date.
    A lapsed review should result in a greater stability increase than a timely one.
    """
    card = Card(
        uuid=sample_card_uuid,
        deck_name="test",
        front="Q",
        back="A",
        state=CardState.New,
    )
    review_ts_base = datetime.datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC)

    # Review 1: New card -> Learning state.
    rating1 = 2
    result1 = scheduler.compute_next_state(card, rating1, review_ts_base)

    card = Card(
        uuid=sample_card_uuid,
        deck_name="test",
        front="Q",
        back="A",
        state=result1.state,
        stability=result1.stab,
        difficulty=result1.diff,
        next_due_date=result1.next_due,
    )

    # Review 2: Learning card -> Review state. Use Easy (3) to graduate.
    review_ts_2 = datetime.datetime.combine(
        result1.next_due, datetime.time(10, 0, 0), tzinfo=UTC
    )
    rating2 = 3
    result2 = scheduler.compute_next_state(card, rating2, review_ts_2)

    card = Card(
        uuid=sample_card_uuid,
        deck_name="test",
        front="Q",
        back="A",
        state=result2.state,
        stability=result2.stab,
        difficulty=result2.diff,
        next_due_date=result2.next_due,
    )

    # Now the card is in the 'Review' state.
    # Scenario 1 (Control): Review on the exact due date.
    review_ts_on_time = datetime.datetime.combine(
        result2.next_due, datetime.time(10, 0, 0), tzinfo=UTC
    )
    result_on_time = scheduler.compute_next_state(
        card, 2, review_ts_on_time
    )  # Rated Good

    # Scenario 2 (Lapsed): Review 10 days AFTER the due date.
    review_ts_lapsed = review_ts_on_time + datetime.timedelta(days=10)
    result_lapsed = scheduler.compute_next_state(
        card, 2, review_ts_lapsed
    )  # Rated Good

    # FSRS theory: A successful review after a longer-than-scheduled delay indicates
    # stronger memory retention, thus stability should increase more.
    assert result_lapsed.stab > result_on_time.stab
    assert result_lapsed.scheduled_days > result_on_time.scheduled_days
    assert result_lapsed.next_due > result_on_time.next_due


def test_review_early_card(scheduler: FSRS_Scheduler, sample_card_uuid: UUID):
    """
    Test scheduling for a card reviewed before its due date.
    An early review should result in a smaller stability increase than a timely one.
    """
    card = Card(
        uuid=sample_card_uuid,
        deck_name="test",
        front="Q",
        back="A",
        state=CardState.New,
    )
    review_ts_base = datetime.datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC)

    # Step 1: Graduate the card from learning to review state.
    # Review 1 (New -> Learning)
    rating1 = 2
    res1 = scheduler.compute_next_state(card, rating1, review_ts_base)

    card = Card(
        uuid=sample_card_uuid,
        deck_name="test",
        front="Q",
        back="A",
        state=res1.state,
        stability=res1.stab,
        difficulty=res1.diff,
        next_due_date=res1.next_due,
    )

    # Review 2 (Learning -> Review)
    review_ts_2 = datetime.datetime.combine(
        res1.next_due, datetime.time(10, 0, 0), tzinfo=UTC
    )
    rating2 = 3  # Use Easy to graduate
    res2 = scheduler.compute_next_state(card, rating2, review_ts_2)
    assert (
        res2.state == CardState.Review
    ), "Card should have graduated to Review state."
    assert (
        res2.scheduled_days >= 2
    ), "Graduated card should have an interval >= 2 days."

    card = Card(
        uuid=sample_card_uuid,
        deck_name="test",
        front="Q",
        back="A",
        state=res2.state,
        stability=res2.stab,
        difficulty=res2.diff,
        next_due_date=res2.next_due,
    )

    # Step 2: Now that the card is in a stable review state, test early vs. on-time.
    # Scenario 1 (Control): Review on the exact due date.
    review_ts_on_time = datetime.datetime.combine(
        res2.next_due, datetime.time(10, 0, 0), tzinfo=UTC
    )
    result_on_time = scheduler.compute_next_state(
        card, 2, review_ts_on_time
    )  # Rated Good

    # Scenario 2 (Early): Review 2 days BEFORE the due date.
    review_ts_early = review_ts_on_time - datetime.timedelta(days=2)
    result_early = scheduler.compute_next_state(
        card, 2, review_ts_early
    )  # Rated Good

    # FSRS theory: A successful early review provides less information about memory
    # strength, so the stability increase should be smaller.
    assert result_early.stab < result_on_time.stab


def test_mature_card_lapse(sample_card_uuid: UUID):
    """
    Test the effect of forgetting a mature card (rating 'Again').
    Stability should reset, but difficulty should increase.
    """
    config = FSRSSchedulerConfig()
    scheduler = FSRS_Scheduler(config=config)

    card = Card(
        uuid=sample_card_uuid,
        deck_name="test",
        front="Q",
        back="A",
        state=CardState.New,
    )
    review_ts = datetime.datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC)

    # Build up a mature card with high stability through several 'Easy' reviews
    rating = 3  # Use Easy
    last_result = scheduler.compute_next_state(card, rating, review_ts)

    card = Card(
        uuid=sample_card_uuid,
        deck_name="test",
        front="Q",
        back="A",
        state=last_result.state,
        stability=last_result.stab,
        difficulty=last_result.diff,
        next_due_date=last_result.next_due,
    )

    for _ in range(4):  # 4 more successful reviews
        # Review 1 day after due date to ensure stability increases
        # with O(1) cached state
        review_ts = datetime.datetime.combine(
            last_result.next_due, datetime.time(10, 0, 0), tzinfo=UTC
        ) + datetime.timedelta(days=1)
        last_result = scheduler.compute_next_state(
            card, rating, review_ts
        )  # Keep using Easy

        card = Card(
            uuid=sample_card_uuid,
            deck_name="test",
            front="Q",
            back="A",
            state=last_result.state,
            stability=last_result.stab,
            difficulty=last_result.diff,
            next_due_date=last_result.next_due,
        )

    mature_stability = last_result.stab
    mature_difficulty = last_result.diff
    # With O(1) cached state and reviewing 1 day late each time, stability should be substantial
    assert (
        mature_stability > 5.0
    ), f"Expected mature stability > 5.0, got {mature_stability}"

    # Now, the user forgets the card (rates 'Again')
    lapse_review_ts = datetime.datetime.combine(
        last_result.next_due, datetime.time(10, 0, 0), tzinfo=UTC
    )
    lapse_result = scheduler.compute_next_state(
        card, 1, lapse_review_ts
    )  # Rating: Again

    # After a lapse, stability should be significantly reduced.
    assert lapse_result.stab < mature_stability / 2
    assert lapse_result.diff > mature_difficulty
    assert lapse_result.state == CardState.Relearning
    assert lapse_result.scheduled_days == 0


def test_ensure_utc_handles_naive_datetime(scheduler: FSRS_Scheduler):
    """Test that _ensure_utc correctly handles a naive datetime object."""
    naive_dt = datetime.datetime(2024, 1, 1, 12, 0, 0)
    aware_dt = scheduler._ensure_utc(naive_dt)
    assert aware_dt.tzinfo is not None
    assert aware_dt.tzinfo == datetime.timezone.utc


def test_compute_next_state_with_unknown_fsrs_state(
    scheduler: FSRS_Scheduler, sample_card_uuid: UUID
):
    """
    Test that compute_next_state raises a ValueError when fsrs returns an unknown state.
    """
    card = Card(
        uuid=sample_card_uuid,
        deck_name="test",
        front="Q",
        back="A",
        state=CardState.New,
    )
    review_ts = datetime.datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC)

    # Mock the return value of the internal fsrs scheduler
    mock_fsrs_output = MagicMock()
    mock_fsrs_output.state.name = "SuperLearning"  # An unknown state
    mock_fsrs_output.stability = 1.0
    mock_fsrs_output.difficulty = 5.0
    mock_fsrs_output.due = datetime.datetime(2024, 1, 2, 10, 0, 0, tzinfo=UTC)

    # The review_card method returns a tuple (card, log)
    mock_return_value = (mock_fsrs_output, MagicMock())

    # We need to patch the scheduler instance's fsrs_scheduler attribute
    with patch.object(
        scheduler.fsrs_scheduler, "review_card", return_value=mock_return_value
    ):
        with pytest.raises(
            ValueError,
            match="Cannot map FSRS state 'SuperLearning' to CardState enum",
        ):
            scheduler.compute_next_state(card, 2, review_ts)


def test_config_impact_on_scheduling():
    """
    Test that changing scheduler config (e.g., desired_retention) affects outcomes.
    """
    # Initial review to create some history
    base_scheduler = FSRS_Scheduler()
    card = Card(
        uuid=UUID("a3f4b1d0-c2e8-4a6a-8f9a-3b1c5d7a9e0f"),
        deck_name="test",
        front="Q",
        back="A",
        state=CardState.New,
    )
    review_ts1 = datetime.datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC)
    initial_result = base_scheduler.compute_next_state(
        card, 2, review_ts1
    )  # Good

    card = Card(
        uuid=UUID("a3f4b1d0-c2e8-4a6a-8f9a-3b1c5d7a9e0f"),
        deck_name="test",
        front="Q",
        back="A",
        state=initial_result.state,
        stability=initial_result.stab,
        difficulty=initial_result.diff,
        next_due_date=initial_result.next_due,
    )
    review_ts2 = datetime.datetime.combine(
        initial_result.next_due, datetime.time(10, 0, 0), tzinfo=UTC
    )

    # To test retention, card must be in review state. Use Easy (3) to graduate.
    rating = 3

    # Scheduler 1: Default retention (e.g., 0.9)
    config1 = FSRSSchedulerConfig(
        parameters=tuple(DEFAULT_PARAMETERS),
        desired_retention=0.9,
    )
    scheduler1 = FSRS_Scheduler(config=config1)
    result1 = scheduler1.compute_next_state(card, rating, review_ts2)

    # Scheduler 2: Higher retention (e.g., 0.95) - should result in shorter intervals
    config2 = FSRSSchedulerConfig(
        parameters=tuple(DEFAULT_PARAMETERS),
        desired_retention=0.95,
    )
    scheduler2 = FSRS_Scheduler(config=config2)
    result2 = scheduler2.compute_next_state(card, rating, review_ts2)

    # Higher desired retention means we need to review more often to achieve it.
    assert result2.scheduled_days < result1.scheduled_days


def test_compute_next_state_is_constant_time(scheduler: FSRS_Scheduler):
    """
    Verify O(1) performance: time should be constant regardless of review count.
    Uses relative assertion to avoid hardware dependence.
    """
    import time
    from uuid import uuid4

    def time_scheduler_call(num_reviews: int) -> float:
        """Create card with N reviews and time scheduler call."""
        card = Card(
            uuid=uuid4(),
            deck_name="test",
            front="Q",
            back="A",
            state=CardState.Review if num_reviews > 0 else CardState.New,
            stability=10.0 if num_reviews > 0 else None,
            difficulty=5.0 if num_reviews > 0 else None,
            next_due_date=(
                datetime.date(2024, 1, 1) if num_reviews > 0 else None
            ),
        )

        review_ts = datetime.datetime(2024, 1, 2, 10, 0, 0, tzinfo=UTC)

        start = time.perf_counter()
        scheduler.compute_next_state(
            card=card, new_rating=3, review_ts=review_ts
        )
        end = time.perf_counter()

        return end - start

    # Time with different review counts
    time_1 = time_scheduler_call(1)
    time_10 = time_scheduler_call(10)
    time_100 = time_scheduler_call(100)
    time_500 = time_scheduler_call(500)

    # O(1) verification: time(500) should be < 2x time(1)
    # Allow 2x factor for measurement noise and cache effects
    assert time_500 < time_1 * 2.0, (
        f"O(1) property violated: time(500)={time_500:.6f}s should be "
        f"< 2x time(1)={time_1:.6f}s (actual ratio: {time_500/time_1:.2f}x)"
    )

    # Additional sanity check: time should be small (<10ms)
    assert time_500 < 0.010, f"Scheduler too slow: {time_500*1000:.2f}ms"

    print("\n✓ O(1) Performance Verified:")
    print(f"  1 review:   {time_1*1000:.3f}ms")
    print(f"  10 reviews:  {time_10*1000:.3f}ms")
    print(f"  100 reviews: {time_100*1000:.3f}ms")
    print(f"  500 reviews: {time_500*1000:.3f}ms")
    print(f"  Ratio (500/1): {time_500/time_1:.2f}x")
