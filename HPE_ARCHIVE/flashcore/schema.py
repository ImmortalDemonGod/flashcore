"""
Defines the database schema for Flashcard-Core using a SQL string constant.
This keeps the schema definition separate from the database connection and
operation logic.
"""

DB_SCHEMA_SQL = """
    CREATE TABLE IF NOT EXISTS cards (
        uuid UUID PRIMARY KEY,
        deck_name VARCHAR NOT NULL,
        front VARCHAR NOT NULL,
        back VARCHAR,
        tags VARCHAR[],
        added_at TIMESTAMP WITH TIME ZONE NOT NULL,
        modified_at TIMESTAMP WITH TIME ZONE NOT NULL,
        last_review_id INTEGER,
        next_due_date DATE,
        state VARCHAR,
        stability DOUBLE,
        difficulty DOUBLE,
        origin_task VARCHAR,
        media_paths VARCHAR[],
        source_yaml_file VARCHAR,
        internal_note VARCHAR,
        front_length INTEGER,
        back_length INTEGER,
        has_media BOOLEAN,
        tag_count INTEGER
    );

    CREATE SEQUENCE IF NOT EXISTS review_seq;
    CREATE SEQUENCE IF NOT EXISTS session_seq;

    CREATE TABLE IF NOT EXISTS reviews (
        review_id INTEGER PRIMARY KEY DEFAULT nextval('review_seq'),
        card_uuid UUID NOT NULL,
        session_uuid UUID,
        ts TIMESTAMP WITH TIME ZONE NOT NULL,
        rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 4),
        resp_ms INTEGER,
        eval_ms INTEGER,
        stab_before DOUBLE,
        stab_after DOUBLE,
        diff DOUBLE,
        next_due DATE,
        elapsed_days_at_review INTEGER,
        scheduled_days_interval INTEGER,
        review_type VARCHAR
    );

    CREATE TABLE IF NOT EXISTS sessions (
        session_id INTEGER PRIMARY KEY DEFAULT nextval('session_seq'),
        session_uuid UUID NOT NULL UNIQUE,
        user_id VARCHAR,
        start_ts TIMESTAMP WITH TIME ZONE NOT NULL,
        end_ts TIMESTAMP WITH TIME ZONE,
        total_duration_ms INTEGER,
        cards_reviewed INTEGER DEFAULT 0,
        decks_accessed VARCHAR[],
        deck_switches INTEGER DEFAULT 0,
        interruptions INTEGER DEFAULT 0,
        device_type VARCHAR,
        platform VARCHAR
    );

    CREATE INDEX IF NOT EXISTS idx_cards_deck_name ON cards (deck_name);
    CREATE INDEX IF NOT EXISTS idx_cards_next_due_date ON cards (next_due_date);
    CREATE INDEX IF NOT EXISTS idx_reviews_card_uuid ON reviews (card_uuid);
    CREATE INDEX IF NOT EXISTS idx_reviews_session_uuid ON reviews (session_uuid);
    CREATE INDEX IF NOT EXISTS idx_reviews_ts ON reviews (ts);
    CREATE INDEX IF NOT EXISTS idx_reviews_next_due ON reviews (next_due);
    CREATE INDEX IF NOT EXISTS idx_sessions_uuid ON sessions (session_uuid);
    CREATE INDEX IF NOT EXISTS idx_sessions_start_ts ON sessions (start_ts);
    CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions (user_id);
"""
