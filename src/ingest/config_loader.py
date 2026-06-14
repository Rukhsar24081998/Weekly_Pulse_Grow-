"""Load product configuration for ingestion."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from src.paths import deliverable, raw_exports_dir

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class ContentFilterConfig:
    min_words: int = 6
    english_only: bool = True
    no_emojis: bool = True


@dataclass
class IngestConfig:
    product_name: str
    display_name: str
    raw_dir: Path
    reviews_output: Path
    app_store_file: str
    play_store_file: str
    default_weeks: int
    min_weeks: int
    max_weeks: int
    missing_store: str
    short_window: str
    filters: ContentFilterConfig


def load_ingest_config(config_path: Path | None = None) -> IngestConfig:
    path = config_path or ROOT / "config" / "product.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    rw = data["review_window"]
    ing = data.get("ingestion", {})
    storage = data.get("storage", {})
    product = data["product"]
    filt = ing.get("filters", {})

    return IngestConfig(
        product_name=product["name"],
        display_name=product["display_name"],
        raw_dir=raw_exports_dir(),
        reviews_output=deliverable(1, "reviews"),
        app_store_file=storage.get("app_store_file", "groww_app_store_reviews.csv"),
        play_store_file=storage.get("play_store_file", "groww_play_store_reviews.csv"),
        default_weeks=int(rw["default_weeks"]),
        min_weeks=int(rw["min_weeks"]),
        max_weeks=int(rw["max_weeks"]),
        missing_store=str(ing.get("missing_store", "warn")),
        short_window=str(ing.get("short_window", "warn")),
        filters=ContentFilterConfig(
            min_words=int(filt.get("min_words", 6)),
            english_only=bool(filt.get("english_only", True)),
            no_emojis=bool(filt.get("no_emojis", True)),
        ),
    )
