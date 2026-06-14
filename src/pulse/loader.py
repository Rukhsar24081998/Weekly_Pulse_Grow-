"""Load themes and reviews for pulse generation."""

from __future__ import annotations

import json
from pathlib import Path

from src.ingest.models import ReviewRecord


def load_themes_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_reviews_index(path: Path) -> dict[str, ReviewRecord]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    index: dict[str, ReviewRecord] = {}
    for item in payload.get("reviews", []):
        index[item["id"]] = ReviewRecord(
            id=item["id"],
            store=item["store"],
            rating=int(item["rating"]),
            title=item.get("title"),
            text=item["text"],
            review_date=item["review_date"],
            locale=item["locale"],
            week_bucket=item["week_bucket"],
        )
    return index
