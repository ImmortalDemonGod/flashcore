from typing import Optional


class DatabaseError(Exception):
    """Base exception for database-related errors."""

    def __init__(
        self, message: str, original_exception: Optional[Exception] = None
    ):
        super().__init__(message)
        self.original_exception = original_exception


class DatabaseConnectionError(DatabaseError):
    """Raised for errors connecting to the database."""

    pass


class SchemaInitializationError(DatabaseError):
    """Raised for errors during schema setup."""

    pass


class CardOperationError(DatabaseError):
    """Raised for errors during card operations (CRUD)."""

    pass


class ReviewOperationError(DatabaseError):
    """Indicates an error during a review-related database operation."""

    pass


class MarshallingError(DatabaseError):
    """Indicates an error during data conversion between application models
    and DB format."""

    pass


class SessionOperationError(DatabaseError):
    """Indicates an error during a session-related database operation."""

    pass


class DeckNotFoundError(DatabaseError):
    """Raised when a specified deck is not found."""

    pass


class FlashcardDatabaseError(DatabaseError):
    """Generic error for flashcard database operations."""

    pass
