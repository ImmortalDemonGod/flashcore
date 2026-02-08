from unittest.mock import patch

# Import the logic for the direct call test
from cultivation.scripts.flashcore.cli._review_logic import review_logic
from cultivation.scripts.flashcore.config import settings
# Import the Typer app for direct invocation
from cultivation.scripts.flashcore.cli.main import app
from typer.testing import CliRunner

runner = CliRunner()

def test_review_function_direct_call():
    """Tests the 'review' function's logic by calling it directly."""
    deck_name = "MyTestDeck"
    # db_path is no longer passed directly; FlashcardDatabase handles it.

    # Patch targets now point to the _review_logic module
    with (
        patch('cultivation.scripts.flashcore.cli._review_logic.FlashcardDatabase') as mock_db,
        patch('cultivation.scripts.flashcore.cli._review_logic.FSRS_Scheduler') as mock_scheduler,
        patch('cultivation.scripts.flashcore.cli._review_logic.ReviewSessionManager') as mock_manager,
        patch('cultivation.scripts.flashcore.cli._review_logic.start_review_flow') as mock_start_flow
    ):
        mock_db_instance = mock_db.return_value

        # Call the logic function directly
        review_logic(deck_name=deck_name)

        # Assert that FlashcardDatabase is initialized without arguments
        mock_db.assert_called_once_with()
        mock_db_instance.initialize_schema.assert_called_once()
        mock_manager.assert_called_once_with(
            db_manager=mock_db_instance,
            scheduler=mock_scheduler.return_value,
            user_uuid=settings.user_uuid,
            deck_name=deck_name,
        )
        mock_start_flow.assert_called_once_with(mock_manager.return_value, tags=None)

def test_review_cli_smoke_test_direct_invoke():
    """
    Tests that the 'review' CLI command correctly invokes the underlying logic.
    """
    deck_name = "MyTestDeck"

    # We patch the logic function to isolate the CLI layer for this test.
    # The patch target is '...cli.main.review_logic' because that's where it's
    # imported and used by the Typer app.
    with patch('cultivation.scripts.flashcore.cli.main.review_logic') as mock_review_logic:
        # Invoke the CLI command using the Typer test runner
        result = runner.invoke(
            app,
            [
                "review",
                deck_name,
            ],
        )

        # Assert that the command exited successfully
        assert result.exit_code == 0, f"CLI command failed: {result.stdout}"

        # Assert that the underlying logic function was called correctly
        mock_review_logic.assert_called_once_with(deck_name=deck_name, tags=None)


# def test_review_logic_uses_default_db_path():
#     """OBSOLETE: This test is no longer valid as the db_path logic has been
#     moved into the FlashcardDatabase class itself.
#     """
#     pass


# def test_review_logic_creates_db_directory(tmp_path):
#     """OBSOLETE: This test is no longer valid as the directory creation logic
#     has been moved into the FlashcardDatabase class itself.
#     """
#     pass

