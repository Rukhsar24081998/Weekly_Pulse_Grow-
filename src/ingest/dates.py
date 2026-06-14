"""Date parsing and window helpers."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone


def parse_review_date(value: str) -> date | None:
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return dt.date()
    except ValueError:
        return None


def iso_week_bucket(d: date) -> str:
    iso = d.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def review_window(weeks: int, reference: date | None = None) -> tuple[date, date]:
    end = reference or datetime.now(timezone.utc).date()
    start = end - timedelta(weeks=weeks)
    return start, end


def in_window(review_day: date, start: date, end: date) -> bool:
    return start <= review_day <= end
