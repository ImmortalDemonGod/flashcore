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
    Represents a single flashcard after parsing and processing from YAML.
    This is the canonical internal representation of a card's content and metadata.

    Media asset paths are always relative to 'cultivation/outputs/flashcards/yaml/assets/'.
    """
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    uuid: UUID = Field(
        default_factory=uuid.uuid4,
        description="Unique UUIDv4 identifier for the card. Auto-generated if not provided in YAML 'id'."
    )
    last_review_id: Optional[int] = Field(default=None, description="The ID of the last review record associated with this card.")
    next_due_date: Optional[date] = Field(default=None, description="The next date the card is scheduled for review.")
    state: CardState = Field(default=CardState.New, description="The current FSRS state of the card.")
    stability: Optional[float] = Field(default=None, description="The stability of the card's memory trace (in days).")
    difficulty: Optional[float] = Field(default=None, description="The difficulty of the card.")

    deck_name: str = Field(
        ...,
        min_length=1,
        description="Fully qualified name of the deck the card belongs to (e.g., 'Backend::Auth'). Derived from YAML 'deck'."
    )
    front: str = Field(
        ...,
        max_length=1024,
        description="The question or prompt text. Supports Markdown and KaTeX. Maps from YAML 'q'."
    )
    back: str = Field(
        ...,
        max_length=1024,
        description="The answer text. Supports Markdown and KaTeX. Maps from YAML 'a'."
    )
    tags: Set[str] = Field(
        default_factory=set,
        description="Set of unique, kebab-case tags. Result of merging deck-level global tags and card-specific tags from YAML."
    )
    added_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp indicating when the card was first added/ingested into the system. This timestamp persists even if the card content is updated later."
    )
    modified_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp indicating when the card was last modified. It is updated upon any change to the card's content."
    )
    origin_task: Optional[str] = Field(
        default=None,
        description="Optional reference to an originating task ID (e.g., from Task Master)."
    )
    media: List[Path] = Field(
        default_factory=list,
        description="Optional list of paths to media files (images, audio, etc.) associated with the card. Paths should be relative to a defined assets root directory (e.g., 'outputs/flashcards/assets/')."
    )
    source_yaml_file: Optional[Path] = Field(
        default=None,
        description="The path to the YAML file from which this card was loaded. Essential for traceability, debugging, and tools that might update YAML files (like 'tm-fc vet' sorting)."
    )
    internal_note: Optional[str] = Field(
        default=None,
        description="A field for internal system notes or flags about the card, not typically exposed to the user (e.g., 'needs_review_for_xss_risk_if_sanitizer_fails', 'generated_by_task_hook')."
    )
    front_length: Optional[int] = Field(
        default=None,
        ge=0,
        description="Character count of the front (question) text. Auto-calculated for content complexity analysis."
    )
    back_length: Optional[int] = Field(
        default=None,
        ge=0,
        description="Character count of the back (answer) text. Auto-calculated for content complexity analysis."
    )
    has_media: Optional[bool] = Field(
        default=None,
        description="Whether this card has associated media files. Auto-calculated for content complexity analysis."
    )
    tag_count: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of tags associated with this card. Auto-calculated for content complexity analysis."
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
        description="The auto-incrementing primary key from the 'reviews' database table. Will be None for new Review objects before they are persisted."
    )
    card_uuid: UUID = Field(
        ...,
        description="The UUID of the card that was reviewed, linking to Card.uuid."
    )
    session_uuid: Optional[UUID] = Field(
        default=None,
        description="The UUID of the session this review belongs to, linking to Session.session_uuid. Nullable for reviews not associated with a session."
    )
    ts: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="The UTC timestamp when the review occurred."
    )
    rating: int = Field(
        ...,
        ge=1,
        le=4,
        description="The user's rating of their recall performance (1=Again, 2=Hard, 3=Good, 4=Easy)."
    )
    resp_ms: Optional[int] = Field(
        default=None,
        ge=0,
        description="The response time in milliseconds taken by the user to recall the answer before revealing it. Nullable if not captured."
    )
    eval_ms: Optional[int] = Field(
        default=None,
        ge=0,
        description="The evaluation time in milliseconds taken by the user to assess their performance and provide a rating after seeing the answer. Nullable if not captured."
    )
    stab_before: Optional[float] = Field(
        default=None,  # Handled by FSRS logic for first reviews
        description="The card's memory stability (in days) *before* this review was incorporated by FSRS. For the very first review of a card, the FSRS scheduler will use a default initial stability."
    )
    stab_after: float = Field(
        ...,
        ge=0.1,  # Stability should generally be positive and non-zero after review
        description="The card's new memory stability (in days) *after* this review and FSRS calculation."
    )
    diff: float = Field(
        ...,
        description="The card's new difficulty rating *after* this review and FSRS calculation."
    )
    next_due: date = Field(
        ...,
        description="The date when this card is next scheduled for review, calculated by FSRS."
    )
    elapsed_days_at_review: int = Field(
        ...,
        ge=0,
        description="The number of days that had actually elapsed between the *previous* review's 'next_due' date (or card's 'added_at' for a new card) and the current review's 'ts'. This is a crucial input for FSRS."
    )
    scheduled_days_interval: int = Field(
        ...,
        ge=0,  # The interval can be 0 for same-day learning steps.
        description="The interval in days (e.g., 'nxt' from fsrs_once) that FSRS calculated for this review. next_due would be 'ts.date() + timedelta(days=scheduled_days_interval)'."
    )
    review_type: Optional[str] = Field(
        default="review",
        description="Type of review, e.g., 'learn', 'review', 'relearn', 'manual'. Useful for advanced FSRS variants or analytics."
    )

    @field_validator("review_type")
    @classmethod
    def check_review_type_is_allowed(cls, v: str | None) -> str | None:
        """Ensures review_type is one of the predefined allowed values or None."""
        ALLOWED_REVIEW_TYPES = {"learn", "review", "relearn", "manual"}
        if v is not None and v not in ALLOWED_REVIEW_TYPES:
            raise ValueError(
                f"Invalid review_type: '{v}'. Allowed types are: {ALLOWED_REVIEW_TYPES} or None."
            )
        return v


class Session(BaseModel):
    """
    Represents a flashcard review session, tracking timing, performance, and context.
    Enables session-level analytics like fatigue detection and optimal timing analysis.
    """
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    session_id: Optional[int] = Field(
        default=None,
        description="The auto-incrementing primary key from the 'sessions' database table. Will be None for new Session objects before they are persisted."
    )
    session_uuid: UUID = Field(
        default_factory=uuid.uuid4,
        description="Unique identifier for this session. Used to link reviews to sessions."
    )
    user_id: Optional[str] = Field(
        default=None,
        description="Identifier for the user (future multi-user support). Currently optional."
    )
    start_ts: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the session started."
    )
    end_ts: Optional[datetime] = Field(
        default=None,
        description="UTC timestamp when the session ended. None for active sessions."
    )
    total_duration_ms: Optional[int] = Field(
        default=None,
        ge=0,
        description="Total session duration in milliseconds. Calculated when session ends."
    )
    cards_reviewed: int = Field(
        default=0,
        ge=0,
        description="Number of cards reviewed in this session."
    )
    decks_accessed: Set[str] = Field(
        default_factory=set,
        description="Set of deck names accessed during this session."
    )
    deck_switches: int = Field(
        default=0,
        ge=0,
        description="Number of times user switched between decks during session."
    )
    interruptions: int = Field(
        default=0,
        ge=0,
        description="Number of interruptions or pauses detected during session."
    )
    device_type: Optional[str] = Field(
        default=None,
        description="Type of device used (desktop, mobile, tablet). Auto-detected when possible."
    )
    platform: Optional[str] = Field(
        default=None,
        description="Platform used (web, cli, mobile_app). Auto-detected when possible."
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
        if len(self.decks_accessed) > previous_deck_count and previous_deck_count > 0:
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
