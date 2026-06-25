import pytest
from pydantic import ValidationError
from flashcore.db.db_utils import db_row_to_review
from flashcore.exceptions import MarshallingError

def test_db_row_to_review_missing_rating_raises_marshalling_error():
    """Bug B1: Missing MarshallingError wrapper for ValidationError.
    Ensures that a row missing the required 'rating' field raises a
    MarshallingError with a message that mentions the missing column.
    """
    row = {
        "id": 1,
        "user_id": 42,
        # 'rating' intentionally omitted to trigger validation error
        "comment": "test",
        "created_at": "2023-01-01T00:00:00",
    }
    with pytest.raises(MarshallingError) as excinfo:
        db_row_to_review(row)
    assert "rating" in str(excinfo.value)
