import duckdb
import logging
from .connection import ConnectionHandler
from . import schema
from ..exceptions import DatabaseConnectionError, SchemaInitializationError

logger = logging.getLogger(__name__)


class SchemaManager:
    """Manages the database schema initialization and maintenance."""

    def __init__(self, handler: ConnectionHandler):
        """
        Initializes the SchemaManager with a connection handler.

        Args:
            handler: The ConnectionHandler instance for the database.
        """
        self._handler = handler

    def initialize_schema(self, force_recreate_tables: bool = False) -> None:
        """
        Initialize the database schema in a transaction.

        If the connection handler is in read-only mode for a persistent database, initialization is skipped; in-memory databases are initialized even in read-only mode. If `force_recreate_tables` is true, existing tables will be dropped and recreated (all existing data will be lost). On underlying database errors this method raises a SchemaInitializationError.  # noqa: E501

        Parameters:
                force_recreate_tables (bool): If true, drop and recreate tables, which will delete existing data.  # noqa: E501

        Raises:
                SchemaInitializationError: If an error occurs while creating or applying the schema.  # noqa: E501
        """
        if self._handle_read_only_initialization(force_recreate_tables):
            return

        conn = self._handler.get_connection()
        try:
            # Use a transaction to ensure atomicity
            with conn.cursor() as cursor:
                cursor.begin()
                if force_recreate_tables:
                    self._recreate_tables(cursor)
                self._create_schema_from_sql(cursor)
                cursor.commit()
            logger.info(
                f"Database schema at {self._handler.db_path_resolved} initialized successfully (or already exists)."  # noqa: E501
            )
        except duckdb.Error as e:
            logger.error(
                f"Error initializing database schema at {self._handler.db_path_resolved}: {e}"  # noqa: E501
            )
            # Attempt to rollback on failure
            if conn and not getattr(conn, "closed", True):
                try:
                    conn.rollback()
                    logger.info(
                        "Transaction rolled back due to schema initialization error."  # noqa: E501
                    )
                except duckdb.Error as rb_err:
                    logger.error(f"Failed to rollback transaction: {rb_err}")
            # Raise the custom exception that tests expect
            raise SchemaInitializationError(
                f"Failed to initialize schema: {e}", original_exception=e
            ) from e

    def _handle_read_only_initialization(
        self, force_recreate_tables: bool
    ) -> bool:
        """
        Decide whether schema initialization should be skipped when the connection is read-only.  # noqa: E501

        If the connection handler is read-only and `force_recreate_tables` is True, this will raise a DatabaseConnectionError. If the connection handler is read-only and the database is not in-memory, the function returns True to indicate initialization should be skipped; otherwise it returns False.  # noqa: E501

        Parameters:
            force_recreate_tables (bool): Whether the caller requests dropping and recreating tables.  # noqa: E501

        Returns:
            bool: True if initialization should be skipped, False otherwise.

        Raises:
            DatabaseConnectionError: If `force_recreate_tables` is requested while in read-only mode.  # noqa: E501
        """
        if self._handler.read_only:
            if force_recreate_tables:
                raise DatabaseConnectionError(
                    "Cannot force_recreate_tables in read-only mode."
                )
            # For a non-memory DB, it's just a warning. For in-memory, we
            # proceed.
            if str(self._handler.db_path_resolved) != ":memory:":
                logger.warning(
                    "Attempting to initialize schema in read-only mode. Skipping."  # noqa: E501
                )
                return True
        return False

    def _perform_safety_check(self, cursor: duckdb.DuckDBPyConnection) -> None:
        """
        Verify the database is empty before destructive table recreation.

        If the resolved database path is in-memory, no check is performed. Uses the provided cursor to confirm that the "reviews" and "cards" tables contain zero rows; if either table contains rows, raises ValueError to refuse destructive operations. If the existence/count check fails for any reason other than a missing table, raises ValueError to refuse proceeding and prevent possible data loss.  # noqa: E501

        Parameters:
            cursor (duckdb.DuckDBPyConnection): Cursor/connection used to execute verification queries.  # noqa: E501

        Raises:
            ValueError: If either table contains rows, or if verification cannot be completed (except when a table is missing).  # noqa: E501
        """
        if str(self._handler.db_path_resolved) == ":memory:":
            return

        try:
            review_result = cursor.execute(
                "SELECT COUNT(*) FROM reviews"
            ).fetchone()
            card_result = cursor.execute(
                "SELECT COUNT(*) FROM cards"
            ).fetchone()

            review_count = review_result[0] if review_result else 0
            card_count = card_result[0] if card_result else 0

            if review_count > 0 or card_count > 0:
                error_msg = f"CRITICAL: Attempted to drop tables with existing data! Reviews: {review_count}, Cards: {card_count}. This would cause permanent data loss. Use backup/restore instead."  # noqa: E501
                logger.error(error_msg)
                raise ValueError(error_msg)
        except Exception as e:
            # If we can't check, assume there might be data and refuse
            if "no such table" not in str(e).lower():
                error_msg = f"CRITICAL: Cannot verify if tables contain data before dropping. Refusing to proceed to prevent data loss. Error: {e}"  # noqa: E501
                logger.error(error_msg)
                raise ValueError(error_msg)

    def _recreate_tables(self, cursor: duckdb.DuckDBPyConnection) -> None:
        """
        Forcefully drop existing schema objects to allow fresh schema creation.

        Performs a safety check to refuse operation if persistent data would be lost, logs a warning about irreversible data loss, and then drops the known tables (reviews, sessions, cards) and their dependent objects.  # noqa: E501

        Parameters:
                cursor (duckdb.DuckDBPyConnection): Active DuckDB cursor/connection used to execute the DROP statements.  # noqa: E501
        """
        self._perform_safety_check(cursor)

        logger.warning(
            f"Forcing table recreation for {self._handler.db_path_resolved}. ALL EXISTING DATA WILL BE LOST."  # noqa: E501
        )

        # Drop all known tables using CASCADE to also drop dependent objects like sequences.  # noqa: E501
        # CASCADE handles foreign key dependencies automatically.
        cursor.execute("DROP TABLE IF EXISTS reviews CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS sessions CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS cards CASCADE;")

    def _create_schema_from_sql(
        self, cursor: duckdb.DuckDBPyConnection
    ) -> None:
        """
        Create the database schema by executing the module's predefined SQL.

        Parameters:
            cursor (duckdb.DuckDBPyConnection): Database cursor used to execute the schema SQL stored in schema.DB_SCHEMA_SQL.  # noqa: E501
        """
        cursor.execute(schema.DB_SCHEMA_SQL)
