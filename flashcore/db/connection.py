import duckdb
import logging
from pathlib import Path
from typing import Optional, Union

from ..exceptions import DatabaseConnectionError

logger = logging.getLogger(__name__)


class ConnectionHandler:
    """Manages the lifecycle of a DuckDB database connection."""

    def __init__(self, db_path: Union[str, Path], read_only: bool = False):
        """
        Initialize the ConnectionHandler with a database path and optional read-only mode.
        
        Parameters:
            db_path (Union[str, Path]): Path to the DuckDB database file or the string ":memory:" (case-insensitive) to use an in-memory database. File paths are resolved to an absolute Path.
            read_only (bool): Whether the connection should be opened in read-only mode; stored on the instance.
        
        Attributes set:
            db_path_resolved (Path): Resolved Path or Path(":memory:") for in-memory usage.
            read_only (bool): Same value as the `read_only` parameter.
            _connection (Optional[duckdb.DuckDBPyConnection]): Initialized to None until a connection is created.
            is_new_db (bool): Initialized to False; indicates whether the database is newly created.
        """
        if isinstance(db_path, str) and db_path.lower() == ":memory:":
            self.db_path_resolved = Path(":memory:")
            logger.info("Using in-memory DuckDB database.")
        else:
            self.db_path_resolved = Path(db_path).resolve()
            logger.info(
                f"ConnectionHandler initialized for DB at: {self.db_path_resolved}"  # noqa: E501
            )

        self.read_only: bool = read_only
        self._connection: Optional[duckdb.DuckDBPyConnection] = None
        self.is_new_db: bool = False

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """
        Provide an active DuckDB connection, creating and opening one if none exists.
        
        Sets `self.is_new_db` to True for an in-memory database or when the file-based
        database file does not yet exist. Ensures the database parent directory exists
        for file-based databases.
        
        Returns:
            duckdb.DuckDBPyConnection: Active DuckDB connection; reuses an existing
            open connection if available.
        
        Raises:
            DatabaseConnectionError: If DuckDB fails to establish the connection.
        """
        if self._connection is None:
            try:
                # This logic determines if the schema needs to be initialized.
                if str(self.db_path_resolved) == ":memory:":
                    self.is_new_db = True
                else:
                    # For file-based DBs, it's new if the file doesn't exist
                    # yet.
                    self.is_new_db = not self.db_path_resolved.exists()
                    # Ensure the parent directory exists, mirroring the
                    # original logic.
                    self.db_path_resolved.parent.mkdir(
                        parents=True, exist_ok=True
                    )

                self._connection = duckdb.connect(
                    database=str(self.db_path_resolved),
                    read_only=self.read_only,
                )
                logger.info("Successfully connected to the database.")
            except duckdb.Error as e:
                raise DatabaseConnectionError(
                    f"Failed to connect to database: {e}"
                ) from e
        return self._connection

    def close_connection(self) -> None:
        """Closes the connection if it exists and sets it to None, allowing
        for reconnection."""
        if self._connection:
            try:
                self._connection.close()
                logger.info(
                    f"Database connection to {self.db_path_resolved} closed."
                )
            except duckdb.Error as e:
                logger.error(f"Error closing the database connection: {e}")
            finally:
                # Set connection to None to allow for re-opening.
                self._connection = None

    def __enter__(self) -> duckdb.DuckDBPyConnection:
        """
        Enter a context-managed block and provide the active DuckDB connection.
        
        Returns:
            duckdb.DuckDBPyConnection: The active DuckDB connection managed by this handler.
        """
        return self.get_connection()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Close the managed DuckDB connection when exiting a context.
        
        Closes the current connection and ensures the handler is ready for reconnection; does not suppress exceptions raised inside the context.
        """
        self.close_connection()