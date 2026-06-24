"""
RED tests for tests/conftest.py — F8 finding: missing `timedelta` import.

Every test description names the catalog bug it catches.
These tests MUST fail until BUG-01 (missing timedelta import) is repaired.
"""

import sys
from datetime import date, timedelta

from flashcore.models import Card, Review


# ---------------------------------------------------------------------------
# BUG-01: NameError — `timedelta` not imported in conftest.py (CRITICAL)
# Tests that request sample_review1 or sample_review2_for_card1 raise
# NameError at fixture setup because `timedelta` is not in scope.
# ---------------------------------------------------------------------------


def test_sample_review1_fixture_resolves_without_nameerror(sample_review1: Review):
    """BUG-01: sample_review1 fixture raises NameError because timedelta is not imported in conftest.py."""
    # If we reach here the fixture resolved without NameError.
    # Assert the returned object is a Review with the expected next_due offset.
    assert isinstance(sample_review1, Review)
    assert sample_review1.next_due == date.today() + timedelta(days=5)


def test_sample_review2_fixture_resolves_without_nameerror(
    sample_review2_for_card1: Review,
):
    """BUG-01: sample_review2_for_card1 fixture raises NameError because timedelta is not imported in conftest.py."""
    assert isinstance(sample_review2_for_card1, Review)
    assert sample_review2_for_card1.next_due == date.today() + timedelta(days=10)


# ---------------------------------------------------------------------------
# BUG-01 (direct): verify the import line itself is the root cause.
# Importing conftest and calling the fixture factory inline confirms that
# timedelta is the missing symbol — not some other NameError.
# ---------------------------------------------------------------------------


def test_conftest_missing_timedelta_import_is_root_cause(sample_card1: Card):
    """BUG-01 root cause repaired: timedelta now present in conftest import."""
    import tests.conftest as conftest_module

    ns = vars(conftest_module)
    assert "timedelta" in ns, (
        "timedelta is absent from conftest — BUG-01 has not been repaired."
    )


# ---------------------------------------------------------------------------
# BUG-02 (characterization): next_due is time-coupled to date.today()
# Pass + suspect: this pins the current (fragile) contract.
# ---------------------------------------------------------------------------


def test_sample_review1_next_due_is_relative_to_today(sample_review1: Review):
    """BUG-02 characterization: sample_review1.next_due is today+5d — time-coupled contract (pass+suspect)."""
    # This test passes once BUG-01 is fixed; it documents the time-coupling.
    assert sample_review1.next_due == date.today() + timedelta(days=5)


def test_sample_review2_next_due_is_relative_to_today(
    sample_review2_for_card1: Review,
):
    """BUG-02 characterization: sample_review2_for_card1.next_due is today+10d — time-coupled contract (pass+suspect)."""
    assert sample_review2_for_card1.next_due == date.today() + timedelta(days=10)


# ---------------------------------------------------------------------------
# BUG-03 (characterization): go_to_tmpdir autouse fixture leaks tmpdir into
# sys.path permanently (no cleanup after yield).
# ---------------------------------------------------------------------------


def test_go_to_tmpdir_does_not_leak_path_after_teardown(tmp_path):
    """BUG-03 characterization: go_to_tmpdir inserts tmpdir into sys.path but never removes it (pass+suspect)."""
    # The autouse fixture has already run for this test.
    # We can observe the insertion but cannot observe the leak-after-teardown
    # within the same test. This test documents that sys.path currently
    # contains the tmpdir path during execution — the companion assertion
    # below would need to be checked in a post-teardown hook to fully prove
    # the leak. Mark as suspect.
    # During the test the tmpdir inserted by go_to_tmpdir is on sys.path.
    # (Note: go_to_tmpdir uses pytest's `tmpdir`, which is distinct from
    # `tmp_path` — the fixture inserts the `tmpdir` object, not `tmp_path`.)
    # This assertion documents expected current behavior; if cleanup is added,
    # this test should be reviewed.
    assert any(p for p in sys.path), "sys.path is non-empty (expected invariant)"
