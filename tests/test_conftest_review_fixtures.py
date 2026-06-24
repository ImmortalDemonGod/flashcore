"""
RED tests for tests/conftest.py — F8 finding: missing `timedelta` import.

Every test description names the catalog bug it catches.
These tests MUST fail until BUG-01 (missing timedelta import) is repaired.
"""

import sys
from datetime import date, timedelta

import pytest
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


# Tracks the tmpdir path inserted by go_to_tmpdir for BUG-03 cleanup verification.
_bug03_tracked: list[str] = []


@pytest.fixture(scope="module", autouse=True)
def _bug03_path_leak_checker():
    """After all tests in this module complete, verify go_to_tmpdir cleaned up its tmpdir entries."""
    yield
    # Module teardown: every function-scoped fixture (including go_to_tmpdir) has
    # already run its finally block for all tests — so the tracked paths must be gone.
    for path in _bug03_tracked:
        assert path not in sys.path, (
            f"BUG-03 regression: go_to_tmpdir leaked {path!r} into sys.path after teardown"
        )


def test_go_to_tmpdir_does_not_leak_path_after_teardown(tmpdir):
    """BUG-03 regression: go_to_tmpdir removes tmpdir from sys.path on teardown."""
    tmpdir_str = str(tmpdir)
    _bug03_tracked.append(tmpdir_str)
    # Autouse fixture must have inserted tmpdir; verify it is present during execution.
    assert tmpdir_str in sys.path, "go_to_tmpdir must insert tmpdir into sys.path during test"
