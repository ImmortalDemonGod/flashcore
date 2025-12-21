"""
Defines the Pydantic models, dataclasses, and constants for YAML processing.
"""

import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any, List, Optional, Set

from bleach.css_sanitizer import CSSSanitizer
from pydantic import (
    BaseModel as PydanticBaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
)

from cultivation.scripts.flashcore.card import CardState, KEBAB_CASE_REGEX_PATTERN

# --- Configuration Constants ---
RAW_KEBAB_CASE_PATTERN = KEBAB_CASE_REGEX_PATTERN

DEFAULT_ALLOWED_HTML_TAGS = [
    "p", "br", "strong", "em", "b", "i", "u", "s", "strike", "del", "sub", "sup",
    "ul", "ol", "li", "dl", "dt", "dd",
    "blockquote", "pre", "code", "hr",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "table", "thead", "tbody", "tfoot", "tr", "th", "td", "caption",
    "img", "a", "figure", "figcaption",
    "span", "math", "semantics", "mrow", "mi", "mo", "mn", "ms",
    "mtable", "mtr", "mtd", "msup", "msub", "msubsup",
    "mfrac", "msqrt", "mroot", "mstyle", "merror", "mpadded",
    "mphantom", "mfenced", "menclose", "annotation"
]
DEFAULT_ALLOWED_HTML_ATTRIBUTES = {
    "*": ["class", "id", "style"],
    "a": ["href", "title", "target", "rel"],
    "img": ["src", "alt", "title", "width", "height", "style"],
    "table": ["summary", "align", "border", "cellpadding", "cellspacing", "width"],
    "td": ["colspan", "rowspan", "align", "valign", "width", "height"],
    "th": ["colspan", "rowspan", "align", "valign", "scope", "width", "height"],
    "span": ["style", "class", "aria-hidden"],
    "math": ["display", "xmlns"],
    "annotation": ["encoding"],
}
DEFAULT_CSS_SANITIZER = CSSSanitizer()
DEFAULT_SECRET_PATTERNS = [
    re.compile(r"""
        (?:key|token|secret|password|passwd|pwd|auth|credential|cred|api_key|apikey|access_key|secret_key)
        \s*[:=]\s*
        (['"]?)
        (?!\s*ENC\[GPG\])(?!\s*ENC\[AES256\])(?!\s*<placeholder>)(?!\s*<\w+>)(?!\s*\{\{\s*\w+\s*\}\})
        ([A-Za-z0-9_/.+-]{20,})
        \1
    """, re.IGNORECASE | re.VERBOSE),
    re.compile(r"-----BEGIN (?:RSA|OPENSSH|PGP|EC|DSA) PRIVATE KEY-----", re.IGNORECASE),
    re.compile(r"(?:(?:sk|pk)_(?:live|test)_|rk_live_)[0-9a-zA-Z]{20,}", re.IGNORECASE),
    re.compile(r"xox[pbar]-[0-9a-zA-Z]{10,}-[0-9a-zA-Z]{10,}-[0-9a-zA-Z]{10,}-[a-zA-Z0-9]{20,}", re.IGNORECASE),
    re.compile(r"ghp_[0-9a-zA-Z]{36}", re.IGNORECASE),
]

# --- Type Aliases for Pydantic v2 Validation ---
KebabCaseStr = Annotated[str, StringConstraints(pattern=RAW_KEBAB_CASE_PATTERN)]

# --- Internal Pydantic Models for Raw YAML Validation ---
class _RawYAMLCardEntry(PydanticBaseModel):
    id: Optional[str] = Field(default=None)
    uuid: Optional[str] = Field(default=None)
    s: Optional[int] = Field(default=None, ge=0, le=4)
    q: str = Field(..., min_length=1)
    a: str = Field(..., min_length=1)
    state: Optional[CardState] = Field(default=None)
    tags: Optional[List[KebabCaseStr]] = Field(default_factory=lambda: [])
    origin_task: Optional[str] = Field(default=None)
    media: Optional[List[str]] = Field(default_factory=lambda: [])
    internal_note: Optional[str] = Field(default=None)  # Authorable from YAML

    model_config = ConfigDict(extra="forbid")

    @field_validator("state", mode="before")
    @classmethod
    def validate_state_str(cls, v: Any) -> Any:
        """Allow state to be provided as a string name of the enum member."""
        if isinstance(v, str):
            try:
                # Convert state name (e.g., "New") to its integer value (e.g., 0)
                return CardState[v.capitalize()].value
            except KeyError:
                # Let the default enum validation handle the error for invalid strings
                return v
        return v

    @field_validator("tags", mode='before')
    @classmethod
    def normalize_tags(cls, v):
        if isinstance(v, list):
            return [tag.strip().lower() if isinstance(tag, str) else tag for tag in v]
        return v

class _RawYAMLDeckFile(PydanticBaseModel):
    deck: str = Field(..., min_length=1)
    tags: Optional[List[KebabCaseStr]] = Field(default_factory=lambda: [])
    cards: List[_RawYAMLCardEntry] = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")

# --- Custom Error Reporting Dataclass ---
@dataclass
class YAMLProcessingError(Exception):
    file_path: Path
    message: str
    card_index: Optional[int] = None
    card_question_snippet: Optional[str] = None
    field_name: Optional[str] = None
    yaml_path_segment: Optional[str] = None # e.g., "cards[2].q"

    def __str__(self) -> str:
        context_parts = [f"File: {self.file_path.name}"]
        if self.card_index is not None:
            context_parts.append(f"Card Index: {self.card_index}")
        if self.card_question_snippet:
            snippet = (self.card_question_snippet[:47] + '...') if len(self.card_question_snippet) > 50 else self.card_question_snippet
            context_parts.append(f"Q: '{snippet}'")
        if self.field_name:
            context_parts.append(f"Field: '{self.field_name}'")
        if self.yaml_path_segment:
            context_parts.append(f"YAML Path: '{self.yaml_path_segment}'")
        return f"{' | '.join(context_parts)} | Error: {self.message}"


# --- Dataclasses for Processing Context and Data ---

@dataclass
class _CardProcessingContext:
    """Holds contextual data for processing a single card to reduce argument passing."""
    source_file_path: Path
    assets_root_directory: Path
    card_index: int
    card_q_preview: str
    skip_media_validation: bool
    skip_secrets_detection: bool


@dataclass
class _FileProcessingContext:
    """Holds contextual data for processing a single YAML file."""
    file_path: Path
    assets_root_directory: Path
    deck_name: str
    deck_tags: Set[str]
    skip_media_validation: bool
    skip_secrets_detection: bool


@dataclass
class _ProcessedCardData:
    """Holds validated and sanitized data ready for Card model instantiation."""
    uuid: uuid.UUID
    front: str
    back: str
    tags: Set[str]
    media: List[Path]
    raw_card: _RawYAMLCardEntry


@dataclass
class YAMLProcessorConfig:
    """Configuration for the entire YAML processing workflow."""
    source_directory: Path
    assets_root_directory: Path
    fail_fast: bool = False
    skip_media_validation: bool = False
    skip_secrets_detection: bool = False


@dataclass
class _ProcessingConfig:
    """Internal configuration for file-level processing."""
    assets_root_directory: Path
    skip_media_validation: bool
    skip_secrets_detection: bool
    fail_fast: bool
