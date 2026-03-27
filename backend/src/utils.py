"""Application utilities — slug, datetime, text"""
from __future__ import annotations
import re
import unicodedata
from datetime import datetime, timezone


def slugify(text: str) -> str:
    """Convert text to ASCII slug."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[\s_-]+", "_", text).strip("_")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def today_str() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def timestamp_compact() -> str:
    """Like 20260325T154501Z"""
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
