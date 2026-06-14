"""Content filters for normalized reviews (English, word count, no emoji)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.ingest.models import ReviewRecord

# Emoji and common symbol ranges (covers 😍 🙏 etc.)
_EMOJI = re.compile(
    "["
    "\U0001F1E0-\U0001F1FF"
    "\U0001F300-\U0001F5FF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FAFF"
    "\u2600-\u26FF"
    "\u2700-\u27BF"
    "]+",
    flags=re.UNICODE,
)

# Non-Latin scripts commonly seen in Indian store reviews
_NON_ENGLISH_SCRIPT = re.compile(
    r"[\u0900-\u097F"  # Devanagari
    r"\u0980-\u09FF"  # Bengali
    r"\u0A00-\u0A7F"  # Gurmukhi
    r"\u0A80-\u0AFF"  # Gujarati
    r"\u0B00-\u0B7F"  # Oriya
    r"\u0B80-\u0BFF"  # Tamil
    r"\u0C00-\u0C7F"  # Telugu
    r"\u0C80-\u0CFF"  # Kannada
    r"\u0D00-\u0D7F"  # Malayalam
    r"\u0600-\u06FF"  # Arabic
    r"\u4E00-\u9FFF"  # CJK
    r"]"
)

_ENGLISH_LOCALES = frozenset(
    {"en", "en-us", "en-gb", "en-in", "en-au", "en-ca", "en-sg", "en-ae"}
)


@dataclass
class ContentFilterStats:
    removed_short: int = 0
    removed_emoji: int = 0
    removed_non_english: int = 0

    @property
    def total_removed(self) -> int:
        return self.removed_short + self.removed_emoji + self.removed_non_english


def word_count(text: str) -> int:
    return len(text.split())


def contains_emoji(text: str) -> bool:
    return bool(_EMOJI.search(text))


def is_english_locale(locale: str) -> bool:
    if not locale or not str(locale).strip():
        return True
    return locale.strip().lower().replace("_", "-") in _ENGLISH_LOCALES


def is_english_text(text: str) -> bool:
    if _NON_ENGLISH_SCRIPT.search(text):
        return False
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    ascii_letters = sum(1 for c in letters if ord(c) < 128)
    return ascii_letters / len(letters) >= 0.85


def review_passes_content_filters(
    record: ReviewRecord,
    *,
    min_words: int = 6,
) -> tuple[bool, str | None]:
    """Return (passes, reject_reason). min_words=6 means more than 5 words."""
    combined = record.text
    if record.title:
        combined = f"{record.title} {record.text}"

    if not is_english_locale(record.locale):
        return False, "non_english_locale"

    if not is_english_text(record.text):
        return False, "non_english_text"

    if word_count(record.text) < min_words:
        return False, "short_text"

    if contains_emoji(combined):
        return False, "emoji"

    return True, None


def filter_review_content(
    records: list[ReviewRecord],
    *,
    min_words: int = 6,
) -> tuple[list[ReviewRecord], ContentFilterStats]:
    kept: list[ReviewRecord] = []
    stats = ContentFilterStats()
    for record in records:
        ok, reason = review_passes_content_filters(record, min_words=min_words)
        if ok:
            kept.append(record)
            continue
        if reason == "short_text":
            stats.removed_short += 1
        elif reason == "emoji":
            stats.removed_emoji += 1
        else:
            stats.removed_non_english += 1
    return kept, stats
