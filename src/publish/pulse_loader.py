"""Load validated pulse artifacts for publish preflight."""

from __future__ import annotations

import json
from pathlib import Path

from src.pulse.models import PulseAction, PulseDocument, PulseQuote, PulseTheme


def load_pulse_json(path: Path) -> PulseDocument:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return PulseDocument(
        product=payload["product"],
        week_ending=payload["week_ending"],
        review_window_weeks=int(payload["review_window_weeks"]),
        window_start=payload["window_start"],
        window_end=payload["window_end"],
        total_reviews=int(payload["total_reviews"]),
        sample_size=int(payload["sample_size"]),
        top_themes=[
            PulseTheme(
                rank=int(theme["rank"]),
                theme_id=theme["theme_id"],
                label=theme["label"],
                summary=theme["summary"],
                review_count=int(theme["review_count"]),
                avg_rating=float(theme["avg_rating"]),
            )
            for theme in payload.get("top_themes", [])
        ],
        quotes=[
            PulseQuote(
                theme_id=quote["theme_id"],
                text=quote["text"],
                rating=int(quote["rating"]),
                store=quote["store"],
            )
            for quote in payload.get("quotes", [])
        ],
        action_ideas=[
            PulseAction(
                theme_id=action["theme_id"],
                action=action["action"],
                rationale=action["rationale"],
            )
            for action in payload.get("action_ideas", [])
        ],
        word_count=int(payload.get("word_count", 0)),
        markdown=payload.get("markdown", ""),
        validation_passed=bool(payload.get("validation_passed", False)),
        validation_errors=list(payload.get("validation_errors", [])),
    )


def load_pulse_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8")
