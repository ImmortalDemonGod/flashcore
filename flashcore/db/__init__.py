"""Database package for flashcore.

This package provides the database layer with dependency injection support.
Only FlashcardDatabase is exported as the public API.
"""

from .database import FlashcardDatabase

__all__ = ["FlashcardDatabase"]
