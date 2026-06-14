"""App Store export parser."""

from __future__ import annotations

import csv
from pathlib import Path

from src.ingest.dates import iso_week_bucket, parse_review_date
from src.ingest.exceptions import EmptyExportError
from src.ingest.models import ReviewRecord
from src.ingest.normalize import make_review_id

RATING_COLUMNS = ("Rating", "rating", "Star Rating")
TITLE_COLUMNS = ("Title", "title")
TEXT_COLUMNS = ("Review", "review", "Review Text", "text")
DATE_COLUMNS = ("Date", "date", "Review Date", "review_date")
_LOCALE_COLUMNS = ("Territory", "territory", "Country", "locale", "Reviewer Language")

_TERRITORY_TO_LOCALE = {
    "IN": "en-IN",
    "US": "en-US",
    "GB": "en-GB",
    "CA": "en-CA",
    "AU": "en-AU",
    "SG": "en-SG",
    "AE": "en-AE",
}


def normalize_app_store_locale(raw: str) -> str:
    text = raw.strip()
    if not text:
        return "en-IN"
    upper = text.upper()
    if upper in _TERRITORY_TO_LOCALE:
        return _TERRITORY_TO_LOCALE[upper]
    lowered = text.lower().replace("_", "-")
    if lowered.startswith("en"):
        return lowered
    return "en-IN"


def _pick(row: dict[str, str], candidates: tuple[str, ...]) -> str:
    lower = {k.lower(): v for k, v in row.items()}
    for name in candidates:
        val = lower.get(name.lower())
        if val is not None and str(val).strip():
            return str(val).strip()
    return ""


def parse_app_store_row(row: dict[str, str]) -> ReviewRecord | None:
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

    title = _pick(row, TITLE_COLUMNS) or None
    locale = normalize_app_store_locale(_pick(row, _LOCALE_COLUMNS))
    iso_date = review_day.isoformat()

    return ReviewRecord(
        id=make_review_id("app_store", iso_date, text),
        store="app_store",
        rating=rating,
        title=title,
        text=text,
        review_date=iso_date,
        locale=locale,
        week_bucket=iso_week_bucket(review_day),
    )


def parse_app_store_csv(path: Path) -> list[ReviewRecord]:
    if not path.exists():
        return []

    records: list[ReviewRecord] = []
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames:
            raise EmptyExportError(f"App Store export is empty or missing header: {path}")
        for row in reader:
            record = parse_app_store_row(row)
            if record:
                records.append(record)

    if path.exists() and path.stat().st_size > 0 and not records:
        raise EmptyExportError(f"No valid App Store reviews parsed from: {path}")
    return records
