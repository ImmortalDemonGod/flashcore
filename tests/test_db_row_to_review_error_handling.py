import pytest
from flashcore.db.db_utils import db_row_to_review
from flashcore.exceptions import MarshallingError
from pydantic import ValidationError

def test_db_row_to_review_missing_validation_error_wrapper():
    # Row dict missing required field 'rating' triggers ValidationError inside Review model
    row = {"id": 1, "content": "test", "user_id": 42}
    with pytest.raises(MarshallingError) as exc:
        db_row_to_review(row)
    # Ensure the underlying cause is a ValidationError
    assert isinstance(exc.value.__cause__, ValidationError)
