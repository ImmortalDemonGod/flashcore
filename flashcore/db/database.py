"""
DuckDB database interactions for flashcore.
Implements the FlashcardDatabase class and supporting exceptions as per the v3.0 technical design.
"""
import duckdb
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Sequence, Union, cast
from ..exceptions import (
    CardOperationError,
    DatabaseConnectionError,
    DatabaseError,
    MarshallingError,
    ReviewOperationError,
    SessionOperationError,
)

from datetime import datetime, date, timezone
import logging
import json
from collections import Counter
from . import db_utils

from ..models import Card, Review, CardState, Session
from .connection import ConnectionHandler
from .schema_manager import SchemaManager

# --- Logging Setup ---
logger = logging.getLogger(__name__)

# --- Helper Functions ---

def _rows_to_dicts(cursor: duckdb.DuckDBPyConnection) -> List[Dict[str, Any]]:
    """Convert cursor results to list of dictionaries using column names."""
    rows = cursor.fetchall()
    if not rows:
        return []
    columns = [desc[0] for desc in cursor.description]
    return [dict(zip(columns, row)) for row in rows]

# --- Custom Exceptions ---



class FlashcardDatabase:
    """
    Acts as a Facade for the database subsystem, providing a simple, high-level
    interface for all flashcard data operations.

    It coordinates the ConnectionHandler, SchemaManager, and data marshalling
    utilities. Intended for use as a context manager.
    """

    def __init__(self, db_path: Union[str, Path], read_only: bool = False):
        """
        Initializes the database by creating a ConnectionHandler.

        Args:
            db_path: Path to the database file (required). Use ':memory:' for
                     an in-memory database. Paths are resolved relative to cwd
                     unless absolute. Must be writable unless read_only=True.
            read_only: If True, opens the database in read-only mode.
        """
        self._handler = ConnectionHandler(db_path=db_path, read_only=read_only)
        self._schema_manager = SchemaManager(self._handler)
        logger.info(f"FlashcardDatabase initialized for DB at: {self._handler.db_path_resolved}")

    @property
    def db_path_resolved(self) -> Path:
        """Returns the resolved path of the database file."""
        return self._handler.db_path_resolved

    @property
    def read_only(self) -> bool:
        """Returns True if the database is in read-only mode."""
        return self._handler.read_only



    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """Delegates connection retrieval to the ConnectionHandler."""
        return self._handler.get_connection()

    def close_connection(self) -> None:
        """Delegates connection closing to the ConnectionHandler."""
        self._handler.close_connection()

    def __enter__(self) -> 'FlashcardDatabase':
        """Establishes a connection and initializes schema if necessary."""
        self.get_connection()
        # If the database was just created, initialize its schema.
        if self._handler.is_new_db and not self._handler.read_only:
            self.initialize_schema()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Ensures the connection is closed on exiting the context."""
        self.close_connection()

    def initialize_schema(self, force_recreate_tables: bool = False) -> None:
        """
        Delegates schema initialization to the SchemaManager.
        """
        self._schema_manager.initialize_schema(force_recreate_tables=force_recreate_tables)



    # --- Card Operations ---
    _UPSERT_CARDS_SQL = """
        INSERT INTO cards (uuid, deck_name, front, back, tags, added_at, modified_at,
                           last_review_id, next_due_date, state, stability, difficulty,
                           origin_task, media_paths, source_yaml_file, internal_note,
                           front_length, back_length, has_media, tag_count)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20)
        ON CONFLICT (uuid) DO UPDATE SET
            deck_name = EXCLUDED.deck_name,
            front = EXCLUDED.front,
            back = EXCLUDED.back,
            tags = EXCLUDED.tags,
            modified_at = EXCLUDED.modified_at,
            -- Preserve review history fields: only update if incoming value is not None/default
            -- This prevents ingestion from destroying learning progress
            last_review_id = CASE
                WHEN EXCLUDED.last_review_id IS NOT NULL THEN EXCLUDED.last_review_id
                ELSE cards.last_review_id
            END,
            next_due_date = CASE
                WHEN EXCLUDED.next_due_date IS NOT NULL THEN EXCLUDED.next_due_date
                ELSE cards.next_due_date
            END,
            state = CASE
                WHEN EXCLUDED.state IS NOT NULL AND EXCLUDED.state != 'New' THEN EXCLUDED.state
                WHEN cards.state IS NOT NULL THEN cards.state
                ELSE 'New'
            END,
            stability = CASE
                WHEN EXCLUDED.stability IS NOT NULL THEN EXCLUDED.stability
                ELSE cards.stability
            END,
            difficulty = CASE
                WHEN EXCLUDED.difficulty IS NOT NULL THEN EXCLUDED.difficulty
                ELSE cards.difficulty
            END,
            -- Always update content and metadata fields
            origin_task = EXCLUDED.origin_task,
            media_paths = EXCLUDED.media_paths,
            source_yaml_file = EXCLUDED.source_yaml_file,
            internal_note = EXCLUDED.internal_note,
            front_length = EXCLUDED.front_length,
            back_length = EXCLUDED.back_length,
            has_media = EXCLUDED.has_media,
            tag_count = EXCLUDED.tag_count;
        """

    def upsert_cards_batch(self, cards: Sequence['Card']) -> int:
        if not cards:
            return 0

        try:
            card_params_list = db_utils.card_to_db_params_list(cards)
        except MarshallingError as e:
            raise CardOperationError("Failed to prepare card data for database operation.") from e

        conn = self.get_connection()
        try:
            return self._execute_upsert_transaction(conn, card_params_list)
        except duckdb.Error as e:
            raise self._handle_upsert_error(conn, e) from e

    def _execute_upsert_transaction(self, conn, card_params_list: List[Tuple]) -> int:
        with conn.cursor() as cursor:
            cursor.begin()
            cursor.executemany(self._UPSERT_CARDS_SQL, card_params_list)
            affected_rows = len(card_params_list)
            cursor.commit()
        logger.info(f"Successfully upserted/processed {affected_rows} out of {len(card_params_list)} cards provided.")
        return affected_rows

    def _handle_upsert_error(self, conn, e: duckdb.Error) -> CardOperationError:
        """Handles errors during the upsert process, ensuring rollback and returning a specific exception."""
        logger.error(f"Error during batch card upsert: {e}")
        if conn and not getattr(conn, 'closed', True):
            try:
                conn.rollback()
                logger.info("Transaction rolled back due to error in batch card upsert.")
            except duckdb.Error as rb_err:
                # Log the rollback error but still raise the original, more informative error.
                logger.error(f"Failed to rollback transaction during upsert error: {rb_err}")

        return CardOperationError(f"Batch card upsert failed: {e}", original_exception=e)

    def get_card_by_uuid(self, card_uuid: uuid.UUID) -> Optional['Card']:
        conn = self.get_connection()
        sql = "SELECT * FROM cards WHERE uuid = $1;"
        try:
            cursor = conn.execute(sql, (card_uuid,))
            rows = _rows_to_dicts(cursor)
            if not rows:
                return None
            row_dict = rows[0]
            logger.info(f"DEBUG: Fetched row for UUID {card_uuid}: {row_dict}")
            try:
                return db_utils.db_row_to_card(cast(Dict[str, Any], row_dict))
            except MarshallingError as e:
                raise CardOperationError(f"Failed to parse card with UUID {card_uuid} from database.", original_exception=e)
        except duckdb.Error as e:
            logger.error(f"Error fetching card by UUID {card_uuid}: {e}")
            raise CardOperationError(f"Failed to fetch card by UUID: {e}", original_exception=e) from e

    def get_all_cards(self, deck_name_filter: Optional[str] = None) -> List['Card']:
        conn = self.get_connection()
        params = []
        sql = "SELECT * FROM cards"
        if deck_name_filter:
            sql += " WHERE deck_name LIKE $1"
            params.append(deck_name_filter)
        sql += " ORDER BY deck_name, front;"
        try:
            cursor = conn.execute(sql, params)
            rows = _rows_to_dicts(cursor)
            if not rows:
                return []
            try:
                return [db_utils.db_row_to_card(cast(Dict[str, Any], row)) for row in rows]
            except MarshallingError as e:
                raise CardOperationError("Failed to parse cards from database.", original_exception=e)
        except duckdb.Error as e:
            logger.error(f"Error fetching all cards (filter: {deck_name_filter}): {e}")
            raise CardOperationError(f"Failed to get all cards: {e}", original_exception=e) from e

    def get_deck_names(self) -> List[str]:
        """
        Retrieves a sorted list of unique deck names from the database.
        """
        conn = self.get_connection()
        sql = "SELECT DISTINCT deck_name FROM cards ORDER BY deck_name;"
        try:
            cursor = conn.execute(sql)
            rows = _rows_to_dicts(cursor)
            if not rows:
                return []
            return [row['deck_name'] for row in rows]
        except duckdb.Error as e:
            logger.error(f"Could not fetch deck names due to a database error: {e}")
            raise CardOperationError("Could not fetch deck names.", original_exception=e) from e

    def get_due_card_count(self, deck_name: str, on_date: date) -> int:
        """
        Counts the number of cards due for review in a specific deck on or before a given date.
        """
        conn = self.get_connection()
        sql = """
            SELECT COUNT(*)
            FROM cards
            WHERE deck_name = ? AND (next_due_date <= ? OR next_due_date IS NULL);
        """
        try:
            # The result of a COUNT query is a single tuple with a single integer
            count_result = conn.execute(sql, (deck_name, on_date)).fetchone()
            return count_result[0] if count_result else 0
        except duckdb.Error as e:
            logger.error(f"Error counting due cards for deck '{deck_name}': {e}")
            raise CardOperationError(f"Failed to count due cards: {e}", original_exception=e) from e

    def get_due_cards(self, deck_name: str, on_date: date, limit: Optional[int] = 20, tags: Optional[List[str]] = None) -> List['Card']:
        """
        Fetches cards from a specific deck due for review on or before a given date.
        A card is considered due if its next_due_date is on or before the specified date,
        or if it has never been reviewed (next_due_date is NULL).

        Args:
            deck_name: Name of the deck to fetch cards from
            on_date: Date to check for due cards
            limit: Maximum number of cards to return
            tags: Optional list of tags to filter cards by
        """
        if limit == 0:
            return []
        conn = self.get_connection()
        sql = """
        SELECT * FROM cards
        WHERE deck_name = $1 AND (next_due_date <= $2 OR next_due_date IS NULL)
        """
        params: List[Any] = [deck_name, on_date]

        # Add tag filtering if tags are provided
        if tags:
            # For each tag, check if it exists in the JSON array
            # DuckDB uses list_contains for JSON arrays
            tag_conditions = []
            for tag in tags:
                tag_conditions.append(f"list_contains(tags, ${len(params) + 1})")
                params.append(tag)
            # Use OR to match any of the specified tags
            sql += " AND (" + " OR ".join(tag_conditions) + ")"

        sql += " ORDER BY next_due_date ASC NULLS FIRST, added_at ASC"

        if limit is not None and limit > 0:
            sql += f" LIMIT ${len(params) + 1}"
            params.append(limit)

        try:
            cursor = conn.execute(sql, params)
            rows = _rows_to_dicts(cursor)
            if not rows:
                return []
            try:
                return [db_utils.db_row_to_card(cast(Dict[str, Any], row_dict)) for row_dict in rows]
            except MarshallingError as e:
                raise CardOperationError(f"Failed to parse due cards for deck '{deck_name}' from database.", original_exception=e)
        except duckdb.Error as e:
            logger.error(f"Error fetching due cards for deck '{deck_name}' on date {on_date}: {e}")
            raise CardOperationError(f"Failed to fetch due cards: {e}", original_exception=e) from e

    def get_database_stats(self) -> Dict[str, Any]:
        """
        Retrieves comprehensive statistics from the database using a single, efficient query.

        Returns:
            A dictionary with statistics like total cards, total reviews,
            deck-specific counts, and counts of cards in different states.
        """
        conn = self.get_connection()
        # This CTE-based query is more efficient as it scans the cards table only once.
        sql = """
        WITH DeckStats AS (
            SELECT
                deck_name,
                COUNT(*) AS card_count,
                COUNT(CASE WHEN next_due_date <= CURRENT_DATE OR next_due_date IS NULL THEN 1 END) AS due_count
            FROM cards
            GROUP BY deck_name
        ), StateStats AS (
            SELECT
                COALESCE(state, 'New') as state,
                COUNT(*) as count
            FROM cards
            GROUP BY COALESCE(state, 'New')
        )
        SELECT
            (SELECT COUNT(*) FROM cards) AS total_cards,
            (SELECT COUNT(*) FROM reviews) AS total_reviews,
            (SELECT json_group_array(json_object('deck_name', deck_name, 'card_count', card_count, 'due_count', due_count)) FROM DeckStats) AS decks,
            (SELECT json_group_object(state, count) FROM StateStats) AS states;
        """
        try:
            result = conn.execute(sql).fetchone()
            if not result or result[0] is None:
                # This case handles an empty database.
                return {
                    'total_cards': 0,
                    'total_reviews': 0,
                    'decks': [],
                    'states': Counter(),
                }

            total_cards, total_reviews, decks_json, states_json = result

            return {
                'total_cards': total_cards or 0,
                'total_reviews': total_reviews or 0,
                'decks': json.loads(decks_json) if decks_json else [],
                'states': Counter(json.loads(states_json)) if states_json else Counter(),
            }
        except (duckdb.Error, IndexError, KeyError, json.JSONDecodeError) as e:
            logger.error(f"Could not retrieve database stats due to an error: {e}")
            raise CardOperationError("Could not retrieve database stats.", original_exception=e) from e

    def delete_cards_by_uuids_batch(self, card_uuids: Sequence[uuid.UUID]) -> int:
        """
        Deletes cards from the database in a batch based on their UUIDs.

        Args:
            card_uuids: A sequence of UUIDs of the cards to be deleted.

        Returns:
            The number of cards successfully deleted.

        Raises:
            CardOperationError: If the database operation fails.
        """
        if self.read_only:
            raise CardOperationError("Cannot delete cards in read-only mode.")

        if not card_uuids:
            return 0

        conn = self.get_connection()
        # Use UNNEST to pass a list of UUIDs to the IN clause, which is efficient in DuckDB.
        sql = "DELETE FROM cards WHERE uuid IN (SELECT * FROM UNNEST(?));"
        # DuckDB expects parameters as a tuple.
        params = (list(card_uuids),)

        try:
            with conn.cursor() as cursor:
                cursor.begin()
                cursor.execute(sql, params)
                affected_rows = cursor.rowcount
                cursor.commit()
                # DuckDB's rowcount returns -1 for no-op deletes, so we normalize to 0.
                normalized_affected_rows = max(0, affected_rows)
                logger.info(f"Successfully deleted {normalized_affected_rows} cards.")
                return normalized_affected_rows
        except duckdb.Error as e:
            logger.error(f"Failed to delete cards: {e}")
            if conn and not getattr(conn, 'closed', True):
                try:
                    conn.rollback()
                    logger.info("Transaction rolled back due to delete error.")
                except duckdb.Error as rb_err:
                    logger.error(f"Failed to rollback transaction: {rb_err}")
            raise CardOperationError(f"Batch card delete failed: {e}", original_exception=e) from e

    def get_all_card_fronts_and_uuids(self) -> Dict[str, uuid.UUID]:
        """
        Retrieves a dictionary mapping all normalized card fronts to their UUIDs.
        This is used for efficient duplicate checking before inserting new cards.
        """
        conn = self.get_connection()
        sql = "SELECT front, uuid FROM cards;"
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                results = cursor.fetchall()

            front_to_uuid: Dict[str, uuid.UUID] = {}
            for front, card_uuid in results:
                normalized_front = " ".join(str(front).lower().split())
                if normalized_front not in front_to_uuid:
                    front_to_uuid[normalized_front] = card_uuid
                else:
                    logger.warning(
                        f"Duplicate normalized front found: '{normalized_front}'. "
                        f"Keeping first UUID seen: {front_to_uuid[normalized_front]}. "
                        f"Discarding new UUID: {card_uuid}."
                    )
            return front_to_uuid
        except duckdb.Error as e:
            logger.error(f"Error fetching all card fronts and UUIDs: {e}")
            raise CardOperationError("Could not fetch card fronts and UUIDs.", original_exception=e) from e

    # --- Review Operations ---
    def _insert_review_and_get_id(self, cursor, review: 'Review') -> int:
        """Inserts a review record and returns its new ID."""
        try:
            review_params_tuple = db_utils.review_to_db_params_tuple(review)
        except MarshallingError as e:
            raise ReviewOperationError("Failed to prepare review data for database operation.") from e
        sql = """
        INSERT INTO reviews (card_uuid, session_uuid, ts, rating, resp_ms, eval_ms, stab_before, stab_after, diff, next_due,
                             elapsed_days_at_review, scheduled_days_interval, review_type)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
        RETURNING review_id;
        """
        cursor.execute(sql, review_params_tuple)
        result = cursor.fetchone()
        if not result:
            raise ReviewOperationError("Failed to retrieve review_id after insertion.")
        return result[0]

    def _update_card_after_review(self, cursor, review: 'Review', new_card_state: 'CardState', new_review_id: int) -> None:
        """Updates the card's state and links it to the new review."""
        sql = """
        UPDATE cards
        SET last_review_id = $1, next_due_date = $2, state = $3, stability = $4, difficulty = $5, modified_at = $6
        WHERE uuid = $7;
        """
        params = (
            new_review_id,
            review.next_due,
            new_card_state.name,
            review.stab_after,
            review.diff,
            datetime.now(timezone.utc), # modified_at
            review.card_uuid
        )
        cursor.execute(sql, params)

    def _execute_review_transaction(self, review: 'Review', new_card_state: 'CardState') -> None:
        """Executes the database transaction to add a review and update a card."""
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.begin()
                new_review_id = self._insert_review_and_get_id(cursor, review)
                self._update_card_after_review(cursor, review, new_card_state, new_review_id)
                cursor.commit()
        except Exception as e:
            logger.error(f"Error during review and card update transaction: {e}")
            if conn and not getattr(conn, 'closed', True):
                try:
                    conn.rollback()
                    logger.info("Transaction rolled back due to review/update error.")
                except duckdb.Error as rb_err:
                    logger.error(f"Failed to rollback transaction: {rb_err}")

            if isinstance(e, DatabaseError):
                raise
            else:
                raise ReviewOperationError(f"Failed to add review and update card: {e}", original_exception=e) from e

    def add_review_and_update_card(self, review: 'Review', new_card_state: 'CardState') -> 'Card':
        """
        Atomically adds a review and updates the corresponding card's state and due date.
        Returns the fully updated card object.
        """
        if self.read_only:
            raise DatabaseConnectionError("Cannot add review in read-only mode.")

        self._execute_review_transaction(review, new_card_state)

        # Fetch and return the updated card. At this point, the card must exist.
        updated_card = self.get_card_by_uuid(review.card_uuid)
        if updated_card is None:
            # This case should not be reachable if the transaction succeeded.
            raise ReviewOperationError(
                f"Failed to retrieve card '{review.card_uuid}' after a successful review update. "
                "This indicates a critical data consistency issue."
            )
        return updated_card

    def get_reviews_for_card(self, card_uuid: uuid.UUID, order_by_ts_desc: bool = True) -> List['Review']:
        conn = self.get_connection()
        order_clause = "ORDER BY ts DESC, review_id DESC" if order_by_ts_desc else "ORDER BY ts ASC, review_id ASC"
        sql = f"SELECT * FROM reviews WHERE card_uuid = $1 {order_clause};"
        try:
            cursor = conn.execute(sql, (card_uuid,))
            rows = _rows_to_dicts(cursor)
            if not rows:
                return []
            try:
                return [db_utils.db_row_to_review(cast(Dict[str, Any], row_dict)) for row_dict in rows]
            except MarshallingError as e:
                raise ReviewOperationError(f"Failed to parse reviews for card {card_uuid} from database.") from e
        except duckdb.Error as e:
            logger.error(f"Error fetching reviews for card UUID {card_uuid}: {e}")
            raise ReviewOperationError(f"Failed to get reviews for card {card_uuid}: {e}", original_exception=e) from e

    def get_latest_review_for_card(self, card_uuid: uuid.UUID) -> Optional['Review']:
        reviews = self.get_reviews_for_card(card_uuid, order_by_ts_desc=True)
        return reviews[0] if reviews else None

    def get_all_reviews(self, start_ts: Optional[datetime] = None, end_ts: Optional[datetime] = None) -> List['Review']:
        conn = self.get_connection()
        sql = "SELECT * FROM reviews"
        params = []
        conditions = []
        if start_ts:
            conditions.append("ts >= $1")
            params.append(start_ts)
        if end_ts:
            conditions.append(f"ts <= ${len(params) + 1}")
            params.append(end_ts)
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY ts ASC, review_id ASC;"
        try:
            cursor = conn.execute(sql, params)
            rows = _rows_to_dicts(cursor)
            if not rows:
                return []
            try:
                return [db_utils.db_row_to_review(cast(Dict[str, Any], row_dict)) for row_dict in rows]
            except MarshallingError as e:
                raise ReviewOperationError("Failed to parse all reviews from database.") from e
        except duckdb.Error as e:
            logger.error(f"Error fetching all reviews (range: {start_ts} to {end_ts}): {e}")
            raise ReviewOperationError(f"Failed to get all reviews: {e}", original_exception=e) from e

    # --- Session Operations ---
    def create_session(self, session: 'Session') -> 'Session':
        """Create a new session in the database and return it with the assigned ID."""
        if self.read_only:
            raise DatabaseConnectionError("Cannot create session in read-only mode.")

        conn = self.get_connection()
        try:
            session_params = db_utils.session_to_db_params_tuple(session)
        except MarshallingError as e:
            raise SessionOperationError("Failed to prepare session data for database operation.") from e
        sql = """
        INSERT INTO sessions (session_uuid, user_id, start_ts, end_ts, total_duration_ms,
                             cards_reviewed, decks_accessed, deck_switches, interruptions,
                             device_type, platform)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        RETURNING session_id;
        """

        try:
            with conn.cursor() as cursor:
                cursor.begin()
                cursor.execute(sql, session_params)
                result = cursor.fetchone()
                if not result:
                    raise CardOperationError("Failed to retrieve session_id after insertion.")
                session_id = result[0]
                cursor.commit()

            # Return session with assigned ID
            session.session_id = session_id
            return session

        except duckdb.Error as e:
            logger.error(f"Error creating session: {e}")
            if conn and not getattr(conn, 'closed', True):
                try:
                    conn.rollback()
                    logger.info("Transaction rolled back due to session creation error.")
                except duckdb.Error as rb_err:
                    logger.error(f"Failed to rollback transaction: {rb_err}")
            raise CardOperationError(f"Failed to create session: {e}", original_exception=e) from e

    def update_session(self, session: 'Session') -> 'Session':
        """Update an existing session in the database."""
        if self.read_only:
            raise DatabaseConnectionError("Cannot update session in read-only mode.")

        if session.session_uuid is None:
            raise ValueError("Session must have a session_uuid to be updated.")

        conn = self.get_connection()
        sql = """
        UPDATE sessions
        SET user_id = $1, start_ts = $2, end_ts = $3, total_duration_ms = $4,
            cards_reviewed = $5, decks_accessed = $6, deck_switches = $7,
            interruptions = $8, device_type = $9, platform = $10
        WHERE session_uuid = $11;
        """

        params = (
            session.user_id,
            session.start_ts,
            session.end_ts,
            session.total_duration_ms,
            session.cards_reviewed,
            list(session.decks_accessed) if session.decks_accessed else None,
            session.deck_switches,
            session.interruptions,
            session.device_type,
            session.platform,
            session.session_uuid
        )

        try:
            with conn.cursor() as cursor:
                cursor.begin()
                cursor.execute(sql, params)
                cursor.commit()
            return session

        except duckdb.Error as e:
            logger.error(f"Error updating session {session.session_uuid}: {e}")
            if conn and not getattr(conn, 'closed', True):
                try:
                    conn.rollback()
                    logger.info("Transaction rolled back due to session update error.")
                except duckdb.Error as rb_err:
                    logger.error(f"Failed to rollback transaction: {rb_err}")
            raise CardOperationError(f"Failed to update session: {e}", original_exception=e) from e

    def get_session_by_uuid(self, session_uuid: uuid.UUID) -> Optional['Session']:
        """Get a session by its UUID."""
        conn = self.get_connection()
        sql = "SELECT * FROM sessions WHERE session_uuid = $1;"

        try:
            cursor = conn.execute(sql, (session_uuid,))
            rows = _rows_to_dicts(cursor)
            if not rows:
                return None
            row_dict = rows[0]
            try:
                return db_utils.db_row_to_session(row_dict)
            except MarshallingError as e:
                raise SessionOperationError(f"Failed to parse session with UUID {session_uuid} from database.") from e
        except duckdb.Error as e:
            logger.error(f"Error fetching session by UUID {session_uuid}: {e}")
            raise CardOperationError(f"Failed to get session by UUID: {e}", original_exception=e) from e

    def get_active_sessions(self, user_id: Optional[str] = None) -> List['Session']:
        """Get all active sessions (end_ts is NULL)."""
        conn = self.get_connection()
        sql = "SELECT * FROM sessions WHERE end_ts IS NULL"
        params = []

        if user_id is not None:
            sql += " AND user_id = $1"
            params.append(user_id)

        sql += " ORDER BY start_ts DESC;"

        try:
            cursor = conn.execute(sql, params)
            rows = _rows_to_dicts(cursor)
            if not rows:
                return []
            try:
                return [db_utils.db_row_to_session(cast(Dict[str, Any], row_dict)) for row_dict in rows]
            except MarshallingError as e:
                raise SessionOperationError("Failed to parse all active sessions from database.") from e
        except duckdb.Error as e:
            logger.error(f"Error fetching active sessions for user {user_id}: {e}")
            raise CardOperationError(f"Failed to get active sessions: {e}", original_exception=e) from e

    def get_recent_sessions(self, limit: int = 10, user_id: Optional[str] = None) -> List['Session']:
        """Get recent sessions, ordered by start time."""
        conn = self.get_connection()
        sql = "SELECT * FROM sessions"
        params: List[Any] = []

        if user_id is not None:
            sql += " WHERE user_id = $1"
            params.append(user_id)

        sql += " ORDER BY start_ts DESC"

        if limit > 0:
            sql += f" LIMIT ${len(params) + 1}"
            params.append(limit)

        try:
            cursor = conn.execute(sql, params)
            rows = _rows_to_dicts(cursor)
            if not rows:
                return []
            try:
                return [db_utils.db_row_to_session(cast(Dict[str, Any], row_dict)) for row_dict in rows]
            except MarshallingError as e:
                raise SessionOperationError("Failed to parse recent sessions from database.") from e
        except duckdb.Error as e:
            logger.error(f"Error fetching recent sessions for user {user_id}: {e}")
            raise CardOperationError(f"Failed to get recent sessions: {e}", original_exception=e) from e

    def get_reviews_for_session(self, session_uuid: uuid.UUID) -> List['Review']:
        """Get all reviews for a specific session."""
        conn = self.get_connection()
        sql = "SELECT * FROM reviews WHERE session_uuid = $1 ORDER BY ts ASC;"

        try:
            cursor = conn.execute(sql, (session_uuid,))
            rows = _rows_to_dicts(cursor)
            if not rows:
                return []
            try:
                return [db_utils.db_row_to_review(cast(Dict[str, Any], row_dict)) for row_dict in rows]
            except MarshallingError as e:
                raise ReviewOperationError(f"Failed to parse reviews for session {session_uuid} from database.") from e
        except duckdb.Error as e:
            logger.error(f"Error fetching reviews for session {session_uuid}: {e}")
            raise ReviewOperationError(f"Failed to get reviews for session: {e}", original_exception=e) from e
