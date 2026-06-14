"""Pulse document types."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class PulseTheme:
    rank: int
    theme_id: str
    label: str
    summary: str
    review_count: int
    avg_rating: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PulseQuote:
    theme_id: str
    text: str
    rating: int
    store: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PulseAction:
    theme_id: str
    action: str
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PulseDocument:
    product: str
    week_ending: str
    review_window_weeks: int
    window_start: str
    window_end: str
    total_reviews: int
    sample_size: int
    top_themes: list[PulseTheme]
    quotes: list[PulseQuote]
    action_ideas: list[PulseAction]
    word_count: int
    markdown: str
    validation_passed: bool = False
    validation_errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "product": self.product,
            "week_ending": self.week_ending,
            "review_window_weeks": self.review_window_weeks,
            "window_start": self.window_start,
            "window_end": self.window_end,
            "total_reviews": self.total_reviews,
            "sample_size": self.sample_size,
            "top_themes": [theme.to_dict() for theme in self.top_themes],
            "quotes": [quote.to_dict() for quote in self.quotes],
            "action_ideas": [action.to_dict() for action in self.action_ideas],
            "word_count": self.word_count,
            "validation_passed": self.validation_passed,
            "validation_errors": self.validation_errors,
            "markdown": self.markdown,
        }


@dataclass
class PulsePipelineResult:
    output_md: str
    output_json: str
    word_count: int
    validation_passed: bool
    validation_errors: list[str]
