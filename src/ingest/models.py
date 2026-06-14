"""Review record types for ingestion."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


FORBIDDEN_FIELDS = frozenset(
    {
        "reviewer_name",
        "reviewer_id",
        "user_id",
        "email",
        "device_id",
        "account_number",
        "profile_url",
    }
)


@dataclass
class ReviewRecord:
    id: str
    store: str
    rating: int
    title: str | None
    text: str
    review_date: str
    locale: str
    week_bucket: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def validate(cls, data: dict[str, Any]) -> None:
        required = {"id", "store", "rating", "text", "review_date", "locale", "week_bucket"}
        missing = required - data.keys()
        if missing:
            raise ValueError(f"Missing required fields: {sorted(missing)}")
        if data["store"] not in {"app_store", "play_store"}:
            raise ValueError(f"Invalid store: {data['store']}")
        if not 1 <= int(data["rating"]) <= 5:
            raise ValueError(f"Invalid rating: {data['rating']}")
        for key in FORBIDDEN_FIELDS:
            if key in data:
                raise ValueError(f"PII field must not be present: {key}")
