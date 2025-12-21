"""
Defines the Deck data structure for holding flashcards.
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from .card import Card


class Deck(BaseModel):
    """
    Represents a collection of flashcards.
    """

    name: str = Field(..., description="The name of the deck.")
    cards: List[Card] = Field(default_factory=list, description="The cards in the deck.")
