import pytest
from flashcore.db.db_utils import db_row_to_review
from flashcore.db.errors import MarshallingError

def test_db_row_to_review_missing_rating_raises_marshalling_error():
    # row missing 'rating' column should raise MarshallingError with column name
    row = {'id': 1, 'title': 'Test', 'content': 'abc'}  # rating missing
    with pytest.raises(MarshallingError) as exc_info:
        db_row_to_review(row)
    assert 'rating' in str(exc_info.value)
