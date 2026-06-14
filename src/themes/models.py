"""Theme clustering data types."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from src.ingest.models import ReviewRecord


@dataclass
class ThemeDefinition:
    id: str
    label: str
    priority: int
    keywords: list[str]


@dataclass
class ThemeTaxonomy:
    fallback_theme_id: str
    themes: list[ThemeDefinition]

    def theme_by_id(self) -> dict[str, ThemeDefinition]:
        return {theme.id: theme for theme in self.themes}

    def valid_theme_ids(self) -> set[str]:
        return {theme.id for theme in self.themes}


@dataclass
class ReviewAssignment:
    review: ReviewRecord
    theme_id: str
    method: str
    ambiguous: bool = False
    matched_keywords: list[str] = field(default_factory=list)


@dataclass
class ThemeStats:
    theme_id: str
    label: str
    review_count: int
    avg_rating: float
    negative_pct: float
    rank: int
    summary: str | None = None
    sample_review_ids: list[str] = field(default_factory=list)
    quote_candidate_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GroqUsage:
    requests: int = 0
    tokens_estimated: int = 0
    enabled: bool = False
    model: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ThemePipelineResult:
    output_path: str
    sample_size: int
    sampled_from: int
    total_assignments: int
    theme_count: int
    top_theme_ids: list[str]
    groq_usage: GroqUsage
    warnings: list[str]
