import pytest
from flashcore.db.db_utils import db_row_to_review
from flashcore.db.errors import MarshallingError, ReviewOperationError
from flashcore.models import Review


def test_db_row_to_review_missing_validationerror_wrapper():
    # Row missing required field 'rating' will cause pydantic.ValidationError
    row = {"id": 1, "user_id": 2, "comment": "test"}  # missing rating
    with pytest.raises(MarshallingError) as exc:
        db_row_to_review(row)
    # Ensure the error mentions the missing field
    assert "rating" in str(exc.value)
