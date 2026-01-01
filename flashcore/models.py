"""
_summary_
"""

from __future__ import annotations

import uuid
import re
from enum import IntEnum
from uuid import UUID
from datetime import datetime, date, timezone
from typing import List, Optional, Set
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Regex for Kebab-case validation (e.g., "my-cool-tag", "learning-python-3")
KEBAB_CASE_REGEX_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"


class CardState(IntEnum):
    """
    Represents the FSRS-defined state of a card's memory trace.
    """

    New = 0
    Learning = 1
    Review = 2
    Relearning = 3


class Rating(IntEnum):
    """
    Represents the user's rating of their recall performance.
    """

    Again = 1
    Hard = 2
    Good = 3
    Easy = 4


class Card(BaseModel):
    """
    Flashcard after parsing from YAML.
    Canonical representation of card content and metadata.

    Media paths relative to configured assets directory.
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    uuid: UUID = Field(
        default_factory=uuid.uuid4,
        description="Unique UUIDv4 for the card. Auto-generated.",
    )
    last_review_id: Optional[int] = Field(
        default=None,
        description="ID of the last review record for this card.",
    )
    next_due_date: Optional[date] = Field(
        default=None,
        description="The next date the card is scheduled for review.",
    )
    state: CardState = Field(
        default=CardState.New,
        description="The current FSRS state of the card.",
    )
    stability: Optional[float] = Field(
        default=None,
        description="The stability of the card's memory trace (in days).",
    )
    difficulty: Optional[float] = Field(
        default=None, description="The difficulty of the card."
    )

    deck_name: str = Field(
        ...,
        min_length=1,
        description="Deck name (e.g., 'Backend::Auth') from YAML 'deck'.",
    )
    front: str = Field(
        ...,
        max_length=1024,
        description="Question text. Supports Markdown/KaTeX. From YAML 'q'.",
    )
    back: str = Field(
        ...,
        max_length=1024,
        description="Answer text. Supports Markdown/KaTeX. From YAML 'a'.",
    )
    tags: Set[str] = Field(
        default_factory=set,
        description="Unique kebab-case tags merged from deck and card.",
    )
    added_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when card was first added (persists).",
    )
    modified_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of last modification.",
    )
    origin_task: Optional[str] = Field(
        default=None,
        description="Optional originating task ID (e.g., Task Master).",
    )
    media: List[Path] = Field(
        default_factory=list,
        description="Media file paths relative to assets directory.",
    )
    source_yaml_file: Optional[Path] = Field(
        default=None,
        description="Source YAML file path for traceability.",
    )
    internal_note: Optional[str] = Field(
        default=None,
        description="Internal system notes/flags (not user-facing).",
    )
    front_length: Optional[int] = Field(
        default=None,
        ge=0,
        description="Character count of front text (auto-calculated).",
    )
    back_length: Optional[int] = Field(
        default=None,
        ge=0,
        description="Character count of back text (auto-calculated).",
    )
    has_media: Optional[bool] = Field(
        default=None,
        description="Whether card has media (auto-calculated).",
    )
    tag_count: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of tags (auto-calculated).",
    )

    @field_validator("tags")
    @classmethod
    def validate_tags_kebab_case(cls, tags: Set[str]) -> Set[str]:
        """Ensure each tag matches the kebab-case pattern."""
        for tag in tags:
            if not re.match(KEBAB_CASE_REGEX_PATTERN, tag):
                raise ValueError(f"Tag '{tag}' is not in kebab-case.")
        return tags

    def calculate_complexity_metrics(self) -> None:
        """Calculate and set content complexity metrics for analytics."""
        self.front_length = len(self.front) if self.front else 0
        self.back_length = len(self.back) if self.back else 0
        self.has_media = bool(self.media)
        self.tag_count = len(self.tags)


class Review(BaseModel):
    """
    Represents a single review event for a flashcard, including user feedback
    and FSRS scheduling parameters.
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    review_id: Optional[int] = Field(
        default=None,
        description="Auto-incrementing PK from reviews table (None if new).",
    )
    card_uuid: UUID = Field(
        ...,
        description="UUID of reviewed card (links to Card.uuid).",
    )
    session_uuid: Optional[UUID] = Field(
        default=None,
        description="Session UUID (links to Session, nullable).",
    )
    ts: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="The UTC timestamp when the review occurred.",
    )
    rating: int = Field(
        ...,
        ge=1,
        le=4,
        description="User rating (1=Again, 2=Hard, 3=Good, 4=Easy).",
    )
    resp_ms: Optional[int] = Field(
        default=None,
        ge=0,
        description="Response time in ms (nullable if not captured).",
    )
    eval_ms: Optional[int] = Field(
        default=None,
        ge=0,
        description="Evaluation time in ms after seeing answer (nullable).",
    )
    stab_before: Optional[float] = Field(
        default=None,  # Handled by FSRS logic for first reviews
        description="Stability before review (days).",
    )
    stab_after: float = Field(
        ...,
        ge=0.1,  # Positive and non-zero after review
        description="New stability after review (days).",
    )
    diff: float = Field(
        ...,
        description="New difficulty after review.",
    )
    next_due: date = Field(
        ...,
        description="Next review date (calculated by FSRS).",
    )
    elapsed_days_at_review: int = Field(
        ...,
        ge=0,
        description="Days elapsed since last review (crucial for FSRS).",
    )
    scheduled_days_interval: int = Field(
        ...,
        ge=0,  # The interval can be 0 for same-day learning steps.
        description="Interval in days calculated by FSRS.",
    )
    review_type: Optional[str] = Field(
        default="review",
        description="Review type (learn/review/relearn/manual).",
    )

    @field_validator("review_type")
    @classmethod
    def check_review_type_is_allowed(cls, v: str | None) -> str | None:
        """Ensures review_type is allowed or None."""
        ALLOWED_REVIEW_TYPES = {"learn", "review", "relearn", "manual"}
        if v is not None and v not in ALLOWED_REVIEW_TYPES:
            raise ValueError(
                f"Invalid review_type: '{v}'. "
                f"Allowed: {ALLOWED_REVIEW_TYPES} or None."
            )
        return v


class Session(BaseModel):
    """
    Flashcard review session tracking timing and performance.
    Enables fatigue detection and timing analytics.
    """

    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    session_id: Optional[int] = Field(
        default=None,
        description="Auto-incrementing PK from sessions table (None if new).",
    )
    session_uuid: UUID = Field(
        default_factory=uuid.uuid4,
        description="Unique session identifier (links reviews).",
    )
    user_id: Optional[str] = Field(
        default=None,
        description="User identifier (optional, future multi-user).",
    )
    start_ts: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the session started.",
    )
    end_ts: Optional[datetime] = Field(
        default=None,
        description="UTC timestamp when session ended (None if active).",
    )
    total_duration_ms: Optional[int] = Field(
        default=None,
        ge=0,
        description="Total duration in ms (calculated on end).",
    )
    cards_reviewed: int = Field(
        default=0,
        ge=0,
        description="Number of cards reviewed in this session.",
    )
    decks_accessed: Set[str] = Field(
        default_factory=set,
        description="Set of deck names accessed during this session.",
    )
    deck_switches: int = Field(
        default=0,
        ge=0,
        description="Deck switches during session.",
    )
    interruptions: int = Field(
        default=0,
        ge=0,
        description="Interruptions/pauses during session.",
    )
    device_type: Optional[str] = Field(
        default=None,
        description="Device type (desktop/mobile/tablet, auto-detected).",
    )
    platform: Optional[str] = Field(
        default=None,
        description="Platform (web/cli/mobile_app, auto-detected).",
    )

    def calculate_duration(self) -> Optional[int]:
        """Calculate session duration in milliseconds if session has ended."""
        if self.end_ts is None:
            return None
        return int((self.end_ts - self.start_ts).total_seconds() * 1000)

    def end_session(self) -> None:
        """Mark session as ended and calculate duration."""
        if self.end_ts is None:
            self.end_ts = datetime.now(timezone.utc)
            self.total_duration_ms = self.calculate_duration()

    def add_card_review(self, deck_name: str) -> None:
        """Record that a card was reviewed, tracking deck access patterns."""
        previous_deck_count = len(self.decks_accessed)
        self.decks_accessed.add(deck_name)

        # If we added a new deck and it's not the first deck, count as switch
        if (
            len(self.decks_accessed) > previous_deck_count
            and previous_deck_count > 0
        ):
            self.deck_switches += 1

        self.cards_reviewed += 1

    def record_interruption(self) -> None:
        """Record an interruption or pause in the session."""
        self.interruptions += 1

    @property
    def is_active(self) -> bool:
        """Check if session is currently active (not ended)."""
        return self.end_ts is None

    @property
    def cards_per_minute(self) -> Optional[float]:
        """Calculate review rate in cards per minute."""
        if self.total_duration_ms is None or self.total_duration_ms == 0:
            return None
        minutes = self.total_duration_ms / (1000 * 60)
        return self.cards_reviewed / minutes if minutes > 0 else None
