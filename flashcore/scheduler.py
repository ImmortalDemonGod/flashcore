# flashcore/scheduler.py

"""
Defines the BaseScheduler abstract class and the FSRS_Scheduler for flashcore,
integrating py-fsrs for scheduling.
"""

import logging
from abc import ABC, abstractmethod
import datetime
from dataclasses import dataclass
from typing import List, Optional, Tuple

from pydantic import BaseModel, Field

from .constants import (
    DEFAULT_PARAMETERS,
    DEFAULT_DESIRED_RETENTION,
)

from fsrs import Card as FSRSCard  # type: ignore
from fsrs import Rating as FSRSRating  # type: ignore

try:
    # Newer py-fsrs API (v3+): main scheduler class renamed to FSRS
    from fsrs import FSRS as PyFSRSScheduler  # type: ignore
except ImportError:  # pragma: no cover - fallback for older py-fsrs versions
    # Older py-fsrs API: scheduler class is exposed as Scheduler
    from fsrs import Scheduler as PyFSRSScheduler  # type: ignore

from .models import Card, Review, CardState

logger = logging.getLogger(__name__)


@dataclass
class SchedulerOutput:
    stab: float
    diff: float
    next_due: datetime.date
    scheduled_days: int
    review_type: str
    elapsed_days: int
    state: CardState


class BaseScheduler(ABC):
    """
    Abstract base class for all schedulers in flashcore.
    """

    @abstractmethod
    def compute_next_state(
        self, card: Card, new_rating: int, review_ts: datetime.datetime
    ) -> SchedulerOutput:
        """
        Computes the next state of a card based on its cached state and a new rating.

        Args:
            card: The Card object containing cached state (stability, difficulty, state).
            new_rating: The rating given for the current review (1=Again, 2=Hard, 3=Good, 4=Easy).
            review_ts: The UTC timestamp of the current review.

        Returns:
            A SchedulerOutput object containing the new state.

        Raises:
            ValueError: If the new_rating is invalid.
        """
        pass


class FSRSSchedulerConfig(BaseModel):
    """Configuration for the FSRS Scheduler."""

    parameters: Tuple[float, ...] = Field(default_factory=lambda: tuple(DEFAULT_PARAMETERS))
    desired_retention: float = DEFAULT_DESIRED_RETENTION
    learning_steps: Tuple[datetime.timedelta, ...] = Field(
        default_factory=lambda: (datetime.timedelta(minutes=1), datetime.timedelta(minutes=10))
    )
    relearning_steps: Tuple[datetime.timedelta, ...] = Field(
        default_factory=lambda: (datetime.timedelta(minutes=10),)
    )
    max_interval: int = 36500


class FSRS_Scheduler(BaseScheduler):
    """
    FSRS (Free Spaced Repetition Scheduler) implementation for flashcore.
    This scheduler uses the py-fsrs library to determine card states and next review dates.
    """

    REVIEW_TYPE_MAP = {
        "new": "learn",
        "learning": "learn",
        "review": "review",
        "relearning": "relearn",
    }

    RATING_MAP = {
        1: FSRSRating.Again,
        2: FSRSRating.Hard,
        3: FSRSRating.Good,
        4: FSRSRating.Easy,
    }

    def __init__(self, config: Optional[FSRSSchedulerConfig] = None):
        if config is None:
            config = FSRSSchedulerConfig()
        self.config = config

        # Initialize the FSRS scheduler with our configuration
        # Prefer the newer FSRS-style API; fall back to older Scheduler signature.
        try:
            # Newer py-fsrs (v3+): FSRS(w=..., request_retention=..., maximum_interval=...)
            self.fsrs_scheduler = PyFSRSScheduler(
                w=tuple(self.config.parameters),
                request_retention=self.config.desired_retention,
                maximum_interval=self.config.max_interval,
            )
        except TypeError:
            # Older py-fsrs (v2): Scheduler(parameters, desired_retention, learning_steps, relearning_steps, maximum_interval, enable_fuzzing)
            self.fsrs_scheduler = PyFSRSScheduler(
                tuple(self.config.parameters),
                self.config.desired_retention,
                self.config.learning_steps,
                self.config.relearning_steps,
                self.config.max_interval,
                True,
            )

    def _ensure_utc(self, ts: datetime.datetime) -> datetime.datetime:
        """Ensures the given datetime is UTC. Assumes UTC if naive."""
        if ts.tzinfo is None or ts.tzinfo.utcoffset(ts) is None:
            return ts.replace(tzinfo=datetime.timezone.utc)
        if ts.tzinfo != datetime.timezone.utc:
            return ts.astimezone(datetime.timezone.utc)
        return ts

    def _map_flashcore_rating_to_fsrs(self, flashcore_rating: int) -> FSRSRating:
        """Maps flashcore rating (1-4) to FSRSRating and validates."""
        if not (1 <= flashcore_rating <= 4):
            raise ValueError(f"Invalid rating: {flashcore_rating}. Must be 1-4 (1=Again, 2=Hard, 3=Good, 4=Easy).")

        return self.RATING_MAP[flashcore_rating]

    def compute_next_state(
        self, card: Card, new_rating: int, review_ts: datetime.datetime
    ) -> SchedulerOutput:
        """
        Computes the next state of a card by replaying its entire history.
        """
        # Start with a fresh card object.
        fsrs_card = FSRSCard()

        # Capture the state before the new review to determine the review type.
        state_before_review = fsrs_card.state

        # Manually calculate elapsed_days for the current review.
        if hasattr(fsrs_card, "last_review") and fsrs_card.last_review:
            elapsed_days = (review_ts.date() - fsrs_card.last_review.date()).days
        else:
            # For a new card, there are no elapsed days since a prior review.
            elapsed_days = 0

        # Now, apply the new review to the final state.
        current_fsrs_rating = self._map_flashcore_rating_to_fsrs(new_rating)
        utc_review_ts = self._ensure_utc(review_ts)
        updated_fsrs_card, log = self.fsrs_scheduler.review_card(
            fsrs_card, current_fsrs_rating, now=utc_review_ts
        )

        # Calculate scheduled days based on the new due date.
        scheduled_days = (updated_fsrs_card.due.date() - utc_review_ts.date()).days

        # Map FSRS state string back to our CardState enum
        try:
            new_card_state = CardState[updated_fsrs_card.state.name.title()]
        except KeyError:
            logger.error(f"Unknown FSRS state: {updated_fsrs_card.state.name}")
            # Default to Review state or raise a more specific error
            raise ValueError(
                f"Cannot map FSRS state '{updated_fsrs_card.state.name}' to CardState enum"
            )

        return SchedulerOutput(
            stab=updated_fsrs_card.stability,
            diff=updated_fsrs_card.difficulty,
            next_due=updated_fsrs_card.due.date(),
            scheduled_days=scheduled_days,
            review_type=self.REVIEW_TYPE_MAP.get(
                state_before_review.name.lower(), "review"
            ),
            elapsed_days=elapsed_days,
            state=new_card_state
        )
