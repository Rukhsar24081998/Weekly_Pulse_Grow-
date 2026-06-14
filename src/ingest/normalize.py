"""Normalize, dedupe, and filter review records."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import date

from src.ingest.dates import in_window, parse_review_date, review_window
from src.ingest.filters import ContentFilterStats, filter_review_content
from src.ingest.models import ReviewRecord


def make_review_id(store: str, review_date: str, text: str) -> str:
    payload = f"{store}|{review_date}|{text.strip()}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


@dataclass
class NormalizeResult:
    reviews: list[ReviewRecord] = field(default_factory=list)
    duplicates_removed: int = 0
    outside_window: int = 0
    content_filter_stats: ContentFilterStats = field(default_factory=ContentFilterStats)
    warnings: list[str] = field(default_factory=list)


def dedupe_records(records: list[ReviewRecord]) -> tuple[list[ReviewRecord], int]:
    seen: set[str] = set()
    unique: list[ReviewRecord] = []
    removed = 0
    for record in records:
        if record.id in seen:
            removed += 1
            continue
        seen.add(record.id)
        unique.append(record)
    return unique, removed


def filter_by_window(
    records: list[ReviewRecord],
    weeks: int,
    reference: date | None = None,
) -> tuple[list[ReviewRecord], int, date, date]:
    start, end = review_window(weeks, reference)
    kept: list[ReviewRecord] = []
    excluded = 0
    for record in records:
        day = parse_review_date(record.review_date)
        if day is None or not in_window(day, start, end):
            excluded += 1
            continue
        kept.append(record)
    return kept, excluded, start, end


def span_weeks(records: list[ReviewRecord]) -> float | None:
    days = [parse_review_date(r.review_date) for r in records]
    days = [d for d in days if d]
    if len(days) < 2:
        return None
    return round((max(days) - min(days)).days / 7, 1)


def normalize_reviews(
    records: list[ReviewRecord],
    weeks: int,
    min_weeks: int,
    short_window_policy: str = "warn",
    reference: date | None = None,
    store_label: str = "",
    content_min_words: int = 6,
    apply_content_filters: bool = True,
) -> NormalizeResult:
    result = NormalizeResult()
    deduped, dup_count = dedupe_records(records)
    result.duplicates_removed = dup_count

    span = span_weeks(deduped)
    if span is not None and span < min_weeks:
        msg = (
            f"{store_label}: raw span {span} weeks is below minimum {min_weeks} weeks"
            if store_label
            else f"Raw span {span} weeks is below minimum {min_weeks} weeks"
        )
        if short_window_policy == "abort":
            raise ValueError(msg)
        result.warnings.append(msg)

    filtered, outside, start, end = filter_by_window(deduped, weeks, reference)
    result.outside_window = outside

    if apply_content_filters:
        filtered, stats = filter_review_content(filtered, min_words=content_min_words)
        result.content_filter_stats = stats
        if stats.total_removed:
            result.warnings.append(
                "Content filters removed "
                f"{stats.total_removed} reviews "
                f"(short={stats.removed_short}, emoji={stats.removed_emoji}, "
                f"non_english={stats.removed_non_english})"
            )

    result.reviews = filtered
    result.warnings.append(f"Window {start.isoformat()} to {end.isoformat()} ({weeks} weeks)")
    return result
