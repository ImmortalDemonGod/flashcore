import duckdb
import logging
from .connection import ConnectionHandler
from . import schema
from .exceptions import DatabaseConnectionError, SchemaInitializationError
from . import config as flashcore_config

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
        Initializes the database schema using a transaction. Skips if in read-only mode
        unless it's an in-memory DB. Can force recreation of tables, which will
        delete all existing data.
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
            logger.info(f"Database schema at {self._handler.db_path_resolved} initialized successfully (or already exists).")
        except duckdb.Error as e:
            logger.error(f"Error initializing database schema at {self._handler.db_path_resolved}: {e}")
            # Attempt to rollback on failure
            if conn and not getattr(conn, 'closed', True):
                try:
                    conn.rollback()
                    logger.info("Transaction rolled back due to schema initialization error.")
                except duckdb.Error as rb_err:
                    logger.error(f"Failed to rollback transaction: {rb_err}")
            # Raise the custom exception that tests expect
            raise SchemaInitializationError(f"Failed to initialize schema: {e}", original_exception=e) from e

    def _handle_read_only_initialization(self, force_recreate_tables: bool) -> bool:
        """Handles the logic for schema initialization in read-only mode. Returns True if initialization should be skipped."""
        if self._handler.read_only:
            if force_recreate_tables:
                raise DatabaseConnectionError("Cannot force_recreate_tables in read-only mode.")
            # For a non-memory DB, it's just a warning. For in-memory, we proceed.
            if str(self._handler.db_path_resolved) != ":memory:":
                logger.warning("Attempting to initialize schema in read-only mode. Skipping.")
                return True
        return False

    def _perform_safety_check(self, cursor: duckdb.DuckDBPyConnection) -> None:
        """Checks for existing data before allowing table recreation."""
        if str(self._handler.db_path_resolved) == ":memory:" or flashcore_config.settings.testing_mode:
            return

        try:
            review_result = cursor.execute("SELECT COUNT(*) FROM reviews").fetchone()
            card_result = cursor.execute("SELECT COUNT(*) FROM cards").fetchone()

            review_count = review_result[0] if review_result else 0
            card_count = card_result[0] if card_result else 0

            if review_count > 0 or card_count > 0:
                error_msg = f"CRITICAL: Attempted to drop tables with existing data! Reviews: {review_count}, Cards: {card_count}. This would cause permanent data loss. Use backup/restore instead."
                logger.error(error_msg)
                raise ValueError(error_msg)
        except Exception as e:
            # If we can't check, assume there might be data and refuse
            if "no such table" not in str(e).lower():
                error_msg = f"CRITICAL: Cannot verify if tables contain data before dropping. Refusing to proceed to prevent data loss. Error: {e}"
                logger.error(error_msg)
                raise ValueError(error_msg)

    def _recreate_tables(self, cursor: duckdb.DuckDBPyConnection) -> None:
        """Drops all tables and sequences to force recreation."""
        self._perform_safety_check(cursor)

        logger.warning(f"Forcing table recreation for {self._handler.db_path_resolved}. ALL EXISTING DATA WILL BE LOST.")

        # Drop all known tables using CASCADE to also drop dependent objects like sequences.
        # The order can still matter for complex dependencies, so we drop tables that are
        # likely to be depended upon first.
        cursor.execute("DROP TABLE IF EXISTS reviews CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS sessions CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS cards CASCADE;")

    def _create_schema_from_sql(self, cursor: duckdb.DuckDBPyConnection) -> None:
        """Executes the SQL statements to create the database schema."""
        cursor.execute(schema.DB_SCHEMA_SQL)
