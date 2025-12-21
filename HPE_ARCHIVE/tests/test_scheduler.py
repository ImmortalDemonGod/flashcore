import pytest
import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4, UUID

from cultivation.scripts.flashcore.scheduler import FSRS_Scheduler, FSRSSchedulerConfig
from cultivation.scripts.flashcore.card import Review, CardState
from cultivation.scripts.flashcore.config import DEFAULT_PARAMETERS, DEFAULT_DESIRED_RETENTION

# Helper to create datetime objects easily
UTC = datetime.timezone.utc

@pytest.fixture
def scheduler() -> FSRS_Scheduler:
    """Provides an FSRS_Scheduler instance with default parameters."""
    config = FSRSSchedulerConfig(
        parameters=tuple(DEFAULT_PARAMETERS),
        desired_retention=DEFAULT_DESIRED_RETENTION,
        # Assuming other FSRSSchedulerConfig fields have defaults or are not needed for these tests
    )
    return FSRS_Scheduler(config=config)

@pytest.fixture
def sample_card_uuid() -> UUID:
    return uuid4()


def test_first_review_new_card(scheduler: FSRS_Scheduler, sample_card_uuid: UUID):
    """Test scheduling for the first review of a new card in the learning phase."""
    history: list[Review] = []
    review_ts = datetime.datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC)

    # Rating: Good (2) - should enter the first learning step.
    rating_good = 2
    result_good = scheduler.compute_next_state(history, rating_good, review_ts)

    assert result_good.state == CardState.Learning
    assert result_good.scheduled_days == 0, "First 'Good' review should be a same-day learning step."
    assert result_good.next_due == review_ts.date()

    # Rating: Again (1) - should also enter a learning step.
    rating_again = 1
    result_again = scheduler.compute_next_state(history, rating_again, review_ts)

    assert result_again.state == CardState.Learning
    assert result_again.scheduled_days == 0, "First 'Again' review should be a same-day learning step."

    # Both 'Good' and 'Again' on a new card lead to a 0-day interval (learning step)
    assert result_again.scheduled_days == result_good.scheduled_days


def test_invalid_rating_input(scheduler: FSRS_Scheduler, sample_card_uuid: UUID):
    """Test that invalid rating inputs raise ValueError."""
    history: list[Review] = []
    # Use a naive datetime to test coverage for the _ensure_utc helper
    review_ts = datetime.datetime(2024, 1, 1, 10, 0, 0)  # No tzinfo

    with pytest.raises(ValueError, match="Invalid rating: 5. Must be 1-4"):
        scheduler.compute_next_state(history, 5, review_ts)

    with pytest.raises(ValueError, match="Invalid rating: -1. Must be 1-4"):
        scheduler.compute_next_state(history, -1, review_ts)


def test_rating_impact_on_interval(scheduler: FSRS_Scheduler, sample_card_uuid: UUID):
    """Test rating impact for a card that is in the learning phase."""
    # First review is 'Good', placing the card into the learning phase.
    review1_ts = datetime.datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC)
    initial_good_result = scheduler.compute_next_state([], 3, review1_ts)  # Good = 3
    assert initial_good_result.scheduled_days == 0
    assert initial_good_result.state == CardState.Learning

    history: list[Review] = [
        Review(
            card_uuid=sample_card_uuid,
            ts=review1_ts,
            rating=3,  # Good rating in unified 1-4 scale
            stab_before=0,
            stab_after=initial_good_result.stab,
            diff=initial_good_result.diff,
            next_due=initial_good_result.next_due,
            elapsed_days_at_review=0,
            scheduled_days_interval=initial_good_result.scheduled_days
        )
    ]

    # The next review happens on the same day, as it's a learning step.
    review2_ts = datetime.datetime.combine(initial_good_result.next_due, datetime.time(10, 10, 0), tzinfo=UTC)

    # 'Again' or 'Hard' should keep the card in the learning phase (0-day interval).
    result_again = scheduler.compute_next_state(history, 1, review2_ts)  # Again
    result_hard = scheduler.compute_next_state(history, 2, review2_ts)   # Hard

    # 'Good' should graduate the card (interval > 0).
    result_good = scheduler.compute_next_state(history, 3, review2_ts)   # Good

    # 'Easy' should also graduate the card with an even longer interval.
    result_easy = scheduler.compute_next_state(history, 4, review2_ts)  # Easy

    assert result_again.scheduled_days == 0, "'Again' should reset learning, resulting in a 0-day step."
    assert result_again.state == CardState.Learning

    assert result_hard.scheduled_days == 0, "'Hard' should repeat a learning step, resulting in a 0-day step."
    assert result_hard.state == CardState.Learning

    assert result_good.scheduled_days > 0, "'Good' on a learning card should graduate it."
    assert result_good.state == CardState.Review

    assert result_easy.scheduled_days > 0, "'Easy' on a learning card should graduate it."
    assert result_easy.state == CardState.Review
    assert result_easy.scheduled_days >= result_good.scheduled_days, "'Easy' should have longer interval than 'Good'"


def test_multiple_reviews_stability_increase(scheduler: FSRS_Scheduler, sample_card_uuid: UUID):
    """Test that stability and scheduled_days generally increase with multiple successful (Good) reviews."""
    history: list[Review] = []
    review_ts_base = datetime.datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC)
    current_card_uuid = sample_card_uuid

    # Review 1: New card, rated Good (2)
    rating1 = 2
    result1 = scheduler.compute_next_state(history, rating1, review_ts_base)

    assert result1.scheduled_days == 0
    stability1 = result1.stab
    scheduled_days1 = result1.scheduled_days
    next_due1 = result1.next_due

    history.append(Review(
        card_uuid=current_card_uuid,
        ts=review_ts_base,
        rating=rating1 + 1, # DB rating
        stab_before=0, # Approx for new card
        stab_after=stability1,
        diff=result1.diff,
        next_due=next_due1,
        elapsed_days_at_review=0,
        scheduled_days_interval=scheduled_days1
    ))

    # Review 2: Reviewed on its due date, rated Easy (3) to graduate
    review_ts2 = datetime.datetime.combine(next_due1, datetime.time(10, 0, 0), tzinfo=UTC)
    rating2 = 3
    result2 = scheduler.compute_next_state(history, rating2, review_ts2)

    stability2 = result2.stab
    scheduled_days2 = result2.scheduled_days
    next_due2 = result2.next_due

    assert stability2 > stability1
    assert scheduled_days2 > scheduled_days1
    assert next_due2 > next_due1

    history.append(Review(
        card_uuid=current_card_uuid,
        ts=review_ts2,
        rating=rating2 + 1, # DB rating
        stab_before=stability1,
        stab_after=stability2,
        diff=result2.diff,
        next_due=next_due2,
        elapsed_days_at_review=(review_ts2.date() - review_ts_base.date()).days, # More accurate elapsed_days
        scheduled_days_interval=scheduled_days2
    ))

    # Review 3: Reviewed on its due date, rated Good (2)
    review_ts3 = datetime.datetime.combine(next_due2, datetime.time(10, 0, 0), tzinfo=UTC)
    rating3 = 2
    result3 = scheduler.compute_next_state(history, rating3, review_ts3)

    stability3 = result3.stab
    scheduled_days3 = result3.scheduled_days
    next_due3 = result3.next_due

    assert stability3 > stability2
    assert scheduled_days3 > scheduled_days2
    assert next_due3 > next_due2


def test_review_lapsed_card(scheduler: FSRS_Scheduler, sample_card_uuid: UUID):
    """
    Test scheduling for a card reviewed significantly after its due date.
    A lapsed review should result in a greater stability increase than a timely one.
    This test first performs two reviews to move the card into the 'Review' state,
    as the stability calculation for lapsed reviews only applies in that state.
    """
    history: list[Review] = []
    review_ts_base = datetime.datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC)
    current_card_uuid = sample_card_uuid

    # Review 1: New card -> Learning state.
    rating1 = 2
    result1 = scheduler.compute_next_state(history, rating1, review_ts_base)
    history.append(Review(
        card_uuid=current_card_uuid,
        ts=review_ts_base,
        rating=rating1 + 1, # DB rating
        stab_before=0,
        stab_after=result1.stab,
        diff=result1.diff,
        next_due=result1.next_due,
        elapsed_days_at_review=0,
        scheduled_days_interval=result1.scheduled_days
    ))

    # Review 2: Learning card -> Review state. Use Easy (3) to graduate.
    review_ts_2 = datetime.datetime.combine(result1.next_due, datetime.time(10, 0, 0), tzinfo=UTC)
    rating2 = 3
    result2 = scheduler.compute_next_state(history, rating2, review_ts_2)
    history.append(Review(
        card_uuid=current_card_uuid,
        ts=review_ts_2,
        rating=rating2 + 1, # DB rating
        stab_before=result1.stab,
        stab_after=result2.stab,
        diff=result2.diff,
        next_due=result2.next_due,
        elapsed_days_at_review=(review_ts_2.date() - review_ts_base.date()).days,
        scheduled_days_interval=result2.scheduled_days
    ))

    # Now the card is in the 'Review' state.
    # Scenario 1 (Control): Review on the exact due date.
    review_ts_on_time = datetime.datetime.combine(result2.next_due, datetime.time(10, 0, 0), tzinfo=UTC)
    result_on_time = scheduler.compute_next_state(history, 2, review_ts_on_time)  # Rated Good

    # Scenario 2 (Lapsed): Review 10 days AFTER the due date.
    review_ts_lapsed = review_ts_on_time + datetime.timedelta(days=10)
    result_lapsed = scheduler.compute_next_state(history, 2, review_ts_lapsed)  # Rated Good

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
    history: list[Review] = []
    review_ts_base = datetime.datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC)
    current_card_uuid = sample_card_uuid

    # Step 1: Graduate the card from learning to review state.
    # Review 1 (New -> Learning)
    rating1 = 2
    res1 = scheduler.compute_next_state(history, rating1, review_ts_base)
    history.append(Review(card_uuid=current_card_uuid, ts=review_ts_base, rating=rating1 + 1, stab_before=0, stab_after=res1.stab, diff=res1.diff, next_due=res1.next_due, elapsed_days_at_review=0, scheduled_days_interval=res1.scheduled_days))

    # Review 2 (Learning -> Review)
    review_ts_2 = datetime.datetime.combine(res1.next_due, datetime.time(10, 0, 0), tzinfo=UTC)
    rating2 = 3 # Use Easy to graduate
    res2 = scheduler.compute_next_state(history, rating2, review_ts_2)
    assert res2.state == CardState.Review, "Card should have graduated to Review state."
    assert res2.scheduled_days > 2, "Graduated card should have an interval > 2 days to make the test meaningful."
    history.append(Review(card_uuid=current_card_uuid, ts=review_ts_2, rating=rating2 + 1, stab_before=res1.stab, stab_after=res2.stab, diff=res2.diff, next_due=res2.next_due, elapsed_days_at_review=(review_ts_2.date() - res1.next_due).days, scheduled_days_interval=res2.scheduled_days))

    # Step 2: Now that the card is in a stable review state, test early vs. on-time.
    last_result = res2

    # Scenario 1 (Control): Review on the exact due date.
    review_ts_on_time = datetime.datetime.combine(last_result.next_due, datetime.time(10, 0, 0), tzinfo=UTC)
    result_on_time = scheduler.compute_next_state(history, 2, review_ts_on_time) # Rated Good

    # Scenario 2 (Early): Review 2 days BEFORE the due date.
    review_ts_early = review_ts_on_time - datetime.timedelta(days=2)
    result_early = scheduler.compute_next_state(history, 2, review_ts_early) # Rated Good

    # FSRS theory: A successful early review provides less information about memory
    # strength, so the stability increase should be smaller.
    assert result_early.stab < result_on_time.stab


def test_mature_card_lapse(sample_card_uuid: UUID):
    """
    Test the effect of forgetting a mature card (rating 'Again').
    Stability should reset, but difficulty should increase.
    """
    # The py-fsrs library now hardcodes relearning steps. The config is unused here
    # but we initialize the scheduler to use default parameters.
    config = FSRSSchedulerConfig()
    scheduler = FSRS_Scheduler(config=config)
    history: list[Review] = []
    review_ts = datetime.datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC)
    current_card_uuid = sample_card_uuid

    # Build up a mature card with high stability through several 'Easy' reviews to ensure graduation and stability growth.
    rating = 3 # Use Easy
    last_result = scheduler.compute_next_state(history, rating, review_ts)
    history.append(Review(
        card_uuid=current_card_uuid, ts=review_ts, rating=rating + 1, stab_before=0,
        stab_after=last_result.stab, diff=last_result.diff,
        next_due=last_result.next_due, elapsed_days_at_review=0,
        scheduled_days_interval=last_result.scheduled_days
    ))

    for _ in range(4): # 4 more successful reviews
        review_ts = datetime.datetime.combine(last_result.next_due, datetime.time(10,0,0), tzinfo=UTC)

        stab_before = last_result.stab

        last_result = scheduler.compute_next_state(history, rating, review_ts) # Keep using Easy
        history.append(Review(
            card_uuid=current_card_uuid, ts=review_ts, rating=rating + 1, stab_before=stab_before,
            stab_after=last_result.stab, diff=last_result.diff,
            next_due=last_result.next_due,
            elapsed_days_at_review=(review_ts.date() - history[-1].ts.date()).days,
            scheduled_days_interval=last_result.scheduled_days
        ))

    mature_stability = last_result.stab
    mature_difficulty = last_result.diff
    assert mature_stability > 20 # Arbitrary check for maturity

    # Now, the user forgets the card (rates 'Again')
    lapse_review_ts = datetime.datetime.combine(last_result.next_due, datetime.time(10,0,0), tzinfo=UTC)
    lapse_result = scheduler.compute_next_state(history, 1, lapse_review_ts) # Rating: Again

    # After a lapse, stability should be significantly reduced.
    assert lapse_result.stab < mature_stability / 2
    assert lapse_result.diff > mature_difficulty
    assert lapse_result.state == CardState.Relearning
    # The new library version hardcodes the next interval for a lapse to 0 days (i.e., due now for relearning).
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
    history: list[Review] = []
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
    ) as _mock_review_card:
        with pytest.raises(
            ValueError, match="Cannot map FSRS state 'SuperLearning' to CardState enum"
        ):
            scheduler.compute_next_state(history, 2, review_ts)



def test_config_impact_on_scheduling():
    """
    Test that changing scheduler config (e.g., desired_retention) affects outcomes.
    """
    # Initial review to create some history, as retention has no effect on the first review's stability
    base_scheduler = FSRS_Scheduler()
    initial_history: list[Review] = []
    review_ts1 = datetime.datetime(2024, 1, 1, 10, 0, 0, tzinfo=UTC)
    initial_result = base_scheduler.compute_next_state(initial_history, 2, review_ts1) # Good

    history: list[Review] = [
        Review(
            card_uuid=UUID("a3f4b1d0-c2e8-4a6a-8f9a-3b1c5d7a9e0f"),
            ts=review_ts1,
            rating=2 + 1, # DB rating
            stab_before=0,
            stab_after=initial_result.stab,
            diff=initial_result.diff,
            next_due=initial_result.next_due,
            elapsed_days_at_review=0,
            scheduled_days_interval=initial_result.scheduled_days
        )
    ]
    review_ts2 = datetime.datetime.combine(initial_result.next_due, datetime.time(10,0,0), tzinfo=UTC)

    # To test retention, card must be in review state. Use Easy (3) to graduate.
    rating = 3

    # Scheduler 1: Default retention (e.g., 0.9)
    config1 = FSRSSchedulerConfig(
        parameters=tuple(DEFAULT_PARAMETERS),
        desired_retention=0.9,
    )
    scheduler1 = FSRS_Scheduler(config=config1)
    result1 = scheduler1.compute_next_state(history, rating, review_ts2)

    # Scheduler 2: Higher retention (e.g., 0.95) - should result in shorter intervals
    config2 = FSRSSchedulerConfig(
        parameters=tuple(DEFAULT_PARAMETERS),
        desired_retention=0.95,
    )
    scheduler2 = FSRS_Scheduler(config=config2)
    result2 = scheduler2.compute_next_state(history, rating, review_ts2)

    # Higher desired retention means we need to review more often to achieve it.
    # Higher desired retention means we need to review more often to achieve it.
    # The stability calculation itself is not directly affected by desired_retention,
    # but the resulting interval is.
    assert result2.scheduled_days < result1.scheduled_days
