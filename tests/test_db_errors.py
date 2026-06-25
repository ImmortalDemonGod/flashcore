import pytest
from flashcore.db.db_utils import db_row_to_review
from flashcore.exceptions import MarshallingError
from pydantic import ValidationError

def test_db_row_to_review_invalid_missing_rating_raises_marshalling_error():
    """Bug B1: Missing ValidationError wrapper causes raw ValidationError.
    The function should raise MarshallingError when required fields are missing.
    This test expects MarshallingError, so it will FAIL until the bug is fixed.
    """
    # Construct a dict missing the required 'rating' field for Review model
    invalid_row = {
        "card_uuid": "123e4567-e89b-12d3-a456-426614174000",
        "session_uuid": "223e4567-e89b-12d3-a456-426614174111",
        "ts": 1700000000,
        # 'rating' omitted intentionally to trigger validation error
        "resp_ms": 100,
        "eval_ms": 200,
        "stab_before": 1.0,
        "stab_after": 1.2,
        "diff": 0,
        "next_due": 1700003600,
        "elapsed_days_at_review": 0,
        "scheduled_days_interval": 1,
        "review_type": "regular",
    }
    with pytest.raises(MarshallingError):
        db_row_to_review(invalid_row)
