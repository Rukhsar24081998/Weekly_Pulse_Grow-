"""Load theme clustering configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from src.paths import ROOT, deliverable
from src.themes.models import ThemeDefinition, ThemeTaxonomy


@dataclass
class GroqConfig:
    model: str
    batch_size: int
    max_requests_per_minute: int
    min_seconds_between_requests: float
    max_samples_per_theme: int
    max_daily_tokens_abort: int
    enabled: bool


@dataclass
class ThemeClusterConfig:
    product_name: str
    display_name: str
    reviews_input: Path
    themes_output: Path
    themes_yaml: Path
    max_reviews: int
    sample_seed: int
    max_themes: int
    top_pulse_themes: int
    groq: GroqConfig


def load_taxonomy(themes_path: Path | None = None) -> ThemeTaxonomy:
    path = themes_path or ROOT / "config" / "themes.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    themes = [
        ThemeDefinition(
            id=item["id"],
            label=item["label"],
            priority=int(item["priority"]),
            keywords=list(item.get("keywords", [])),
        )
        for item in data.get("themes", [])
    ]
    return ThemeTaxonomy(
        fallback_theme_id=str(data.get("fallback_theme_id", "performance")),
        themes=themes,
    )


def load_theme_config(config_path: Path | None = None) -> ThemeClusterConfig:
    path = config_path or ROOT / "config" / "product.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    product = data["product"]
    tc = data.get("theme_clustering", {})
    groq = tc.get("groq", {})

    return ThemeClusterConfig(
        product_name=product["name"],
        display_name=product["display_name"],
        reviews_input=deliverable(1, "reviews"),
        themes_output=deliverable(2, "themes"),
        themes_yaml=ROOT / "config" / "themes.yaml",
        max_reviews=int(tc.get("max_reviews", 1000)),
        sample_seed=int(tc.get("sample_seed", 42)),
        max_themes=int(tc.get("max_themes", 5)),
        top_pulse_themes=int(tc.get("top_pulse_themes", 3)),
        groq=GroqConfig(
            model=str(groq.get("model", "llama-3.3-70b-versatile")),
            batch_size=int(groq.get("batch_size", 40)),
            max_requests_per_minute=int(groq.get("max_requests_per_minute", 3)),
            min_seconds_between_requests=float(groq.get("min_seconds_between_requests", 21)),
            max_samples_per_theme=int(groq.get("max_samples_per_theme", 10)),
            max_daily_tokens_abort=int(groq.get("max_daily_tokens_abort", 80000)),
            enabled=bool(groq.get("enabled", True)),
        ),
    )
