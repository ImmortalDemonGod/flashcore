import pytest
from flashcore.db.db_utils import db_row_to_review
from flashcore.errors import MarshallingError
from pydantic import ValidationError

def test_db_row_to_review_missing_validation_error_wrapper():
    """Bug B1: Missing ValidationError wrapper causes raw ValidationError to escape.
    The test expects a MarshallingError, but the current implementation raises ValidationError.
    """
    bad_row = {"rating": "not a number"}  # Assuming Review expects an int rating
    with pytest.raises(MarshallingError):
        db_row_to_review(bad_row)
