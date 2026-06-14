"""Load normalized reviews from Phase 1 JSON."""

from __future__ import annotations

import json
from pathlib import Path

from src.ingest.models import ReviewRecord


def load_reviews_json(path: Path) -> tuple[list[ReviewRecord], dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    reviews = []
    for item in payload.get("reviews", []):
        ReviewRecord.validate(item)
        reviews.append(
            ReviewRecord(
                id=item["id"],
                store=item["store"],
                rating=int(item["rating"]),
                title=item.get("title"),
                text=item["text"],
                review_date=item["review_date"],
                locale=item["locale"],
                week_bucket=item["week_bucket"],
            )
        )
    meta = {
        "product": payload.get("product"),
        "window": payload.get("window", {}),
        "review_window_weeks": payload.get("review_window_weeks"),
    }
    return reviews, meta
