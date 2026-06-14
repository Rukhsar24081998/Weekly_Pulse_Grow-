"""Play Store export parser."""

from __future__ import annotations

import csv
from pathlib import Path

from src.ingest.dates import iso_week_bucket, parse_review_date
from src.ingest.exceptions import EmptyExportError
from src.ingest.models import ReviewRecord
from src.ingest.normalize import make_review_id

RATING_COLUMNS = ("Star Rating", "star_rating", "Rating", "rating")
TEXT_COLUMNS = ("Review Text", "review_text", "Review", "text")
DATE_COLUMNS = ("Review Submit Date", "review_submit_date", "Date", "date")
LOCALE_COLUMNS = ("Reviewer Language", "reviewer_language", "Language", "locale")


def _pick(row: dict[str, str], candidates: tuple[str, ...]) -> str:
    lower = {k.lower(): v for k, v in row.items()}
    for name in candidates:
        val = lower.get(name.lower())
        if val is not None and str(val).strip():
            return str(val).strip()
    return ""


def parse_play_store_row(row: dict[str, str]) -> ReviewRecord | None:
    rating_raw = _pick(row, RATING_COLUMNS)
    text = _pick(row, TEXT_COLUMNS)
    date_raw = _pick(row, DATE_COLUMNS)
    if not rating_raw or not text or not date_raw:
        return None

    review_day = parse_review_date(date_raw)
    if review_day is None:
        return None

    try:
        rating = int(float(rating_raw))
    except ValueError:
        return None
    if rating < 1 or rating > 5:
        return None

    locale = _pick(row, LOCALE_COLUMNS) or "en"
    iso_date = review_day.isoformat()

    return ReviewRecord(
        id=make_review_id("play_store", iso_date, text),
        store="play_store",
        rating=rating,
        title=None,
        text=text,
        review_date=iso_date,
        locale=locale,
        week_bucket=iso_week_bucket(review_day),
    )


def parse_play_store_csv(path: Path) -> list[ReviewRecord]:
    if not path.exists():
        return []

    records: list[ReviewRecord] = []
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames:
            raise EmptyExportError(f"Play Store export is empty or missing header: {path}")
        for row in reader:
            record = parse_play_store_row(row)
            if record:
                records.append(record)

    if path.exists() and path.stat().st_size > 0 and not records:
        raise EmptyExportError(f"No valid Play Store reviews parsed from: {path}")
    return records
