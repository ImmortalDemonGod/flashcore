"""
Centralized configuration management for the Flashcore application.
"""
from pathlib import Path
from typing import Tuple
import uuid

from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Path Configuration ---

def get_default_db_path() -> Path:
    """Returns the default path for the database file, ensuring the directory exists."""
    default_dir = Path.home() / ".cultivation" / "flashcore_data"
    default_dir.mkdir(parents=True, exist_ok=True)
    return default_dir / "flash.db"

class Settings(BaseSettings):
    """
    Defines application settings, loaded from environment variables or .env files.
    """
    # Define model configuration
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # --- Core Paths ---
    # The database path can be overridden by the FLASHCORE_DB_PATH env var.
    db_path: Path = get_default_db_path()
    
    # The source for YAML flashcard files.
    yaml_source_dir: Path = Path("./cultivation/outputs/flashcards/yaml")
    
    # The root directory for flashcard media assets.
    assets_dir: Path = Path("./cultivation/outputs/flashcards/yaml/assets")

    # The default directory for Markdown exports.
    export_dir: Path = Path("./cultivation/outputs/flashcards/md")

    # --- User Configuration ---
    # Default user UUID. Can be overridden by FLASHCORE_USER_UUID env var.
    user_uuid: uuid.UUID = uuid.UUID("00000000-0000-0000-0000-000000000001")

    # --- Testing Configuration ---
    # When True, disables safety checks that prevent data loss during tests.
    # Should NEVER be enabled in production. Can be set via FLASHCORE_TESTING_MODE.
    testing_mode: bool = False

# Create a singleton instance of the settings
settings = Settings()


# --- FSRS Constants ---

# Default FSRS parameters (weights 'w')
# Sourced from: py-fsrs library (specifically fsrs.scheduler.DEFAULT_PARAMETERS)
# These parameters are used by the FSRS algorithm to schedule card reviews.
# Each parameter influences a specific aspect of the memory model.
# For detailed explanations of each parameter, refer to FSRS documentation and the optimizer source.
DEFAULT_PARAMETERS: Tuple[float, ...] = (
    0.2172,  # w[0]
    1.1771,  # w[1]
    3.2602,  # w[2]
    16.1507, # w[3]
    7.0114,  # w[4]
    0.57,    # w[5]
    2.0966,  # w[6]
    0.0069,  # w[7]
    1.5261,  # w[8]
    0.112,   # w[9]
    1.0178,  # w[10]
    1.849,   # w[11]
    0.1133,  # w[12]
    0.3127,  # w[13]
    2.2934,  # w[14]
    0.2191,  # w[15]
    3.0004,  # w[16]
    0.7536,  # w[17]
    0.3332,  # w[18]
    0.1437,  # w[19]
    0.2,     # w[20]
)

# Default desired retention rate if not specified elsewhere.
DEFAULT_DESIRED_RETENTION: float = 0.9

# Sourced from: https://github.com/open-spaced-repetition/py-fsrs/blob/main/fsrs/scheduler.py (DEFAULT_PARAMETERS)

# It's also good practice to define any other scheduler-related constants here.
# For example, default desired retention rate if not specified elsewhere.
