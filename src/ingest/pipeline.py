"""Ingestion pipeline orchestration."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path

from src.ingest.app_store import parse_app_store_csv
from src.ingest.config_loader import IngestConfig, load_ingest_config
from src.ingest.exceptions import EmptyExportError, IngestionError
from src.ingest.models import FORBIDDEN_FIELDS, ReviewRecord
from src.ingest.normalize import normalize_reviews
from src.ingest.play_store import parse_play_store_csv


@dataclass
class IngestResult:
    output_path: Path
    review_window_weeks: int
    window_start: str
    window_end: str
    total_reviews: int
    app_store_count: int
    play_store_count: int
    duplicates_removed: int
    outside_window: int
    content_filtered: int
    warnings: list[str] = field(default_factory=list)


def _load_store_records(
    path: Path,
    parser,
    label: str,
    missing_policy: str,
) -> tuple[list[ReviewRecord], list[str]]:
    warnings: list[str] = []
    if not path.exists():
        msg = f"Missing {label} export: {path}"
        if missing_policy == "abort":
            raise IngestionError(msg)
        warnings.append(msg)
        return [], warnings
    return parser(path), warnings


def run_ingestion(
    weeks: int | None = None,
    raw_dir: Path | None = None,
    output_path: Path | None = None,
    reference_date: date | None = None,
    config: IngestConfig | None = None,
) -> IngestResult:
    cfg = config or load_ingest_config()
    window_weeks = weeks if weeks is not None else cfg.default_weeks
    if window_weeks < cfg.min_weeks or window_weeks > cfg.max_weeks:
        raise IngestionError(
            f"weeks must be between {cfg.min_weeks} and {cfg.max_weeks}, got {window_weeks}"
        )

    raw = raw_dir or cfg.raw_dir
    app_path = raw / cfg.app_store_file
    play_path = raw / cfg.play_store_file

    all_warnings: list[str] = []
    app_records, w = _load_store_records(
        app_path, parse_app_store_csv, "App Store", cfg.missing_store
    )
    all_warnings.extend(w)
    play_records, w = _load_store_records(
        play_path, parse_play_store_csv, "Play Store", cfg.missing_store
    )
    all_warnings.extend(w)

    if not app_records and not play_records:
        raise IngestionError("No reviews loaded from either store export")

    combined = app_records + play_records
    apply_filters = cfg.filters.english_only or cfg.filters.no_emojis
    norm = normalize_reviews(
        combined,
        weeks=window_weeks,
        min_weeks=cfg.min_weeks,
        short_window_policy=cfg.short_window,
        reference=reference_date,
        content_min_words=cfg.filters.min_words,
        apply_content_filters=apply_filters,
    )
    all_warnings.extend(norm.warnings)

    reviews = norm.reviews
    app_count = sum(1 for r in reviews if r.store == "app_store")
    play_count = sum(1 for r in reviews if r.store == "play_store")

    if app_count == 0 and play_count == 0:
        raise IngestionError("No reviews remain after filtering")

    start, end = reviews[0].review_date, reviews[0].review_date
    for r in reviews:
        if r.review_date < start:
            start = r.review_date
        if r.review_date > end:
            end = r.review_date

    from src.ingest.dates import review_window

    win_start, win_end = review_window(window_weeks, reference_date)
    filter_stats = norm.content_filter_stats
    payload = {
        "product": cfg.display_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "review_window_weeks": window_weeks,
        "filters": {
            "min_words": cfg.filters.min_words,
            "english_only": cfg.filters.english_only,
            "no_emojis": cfg.filters.no_emojis,
        },
        "window": {
            "start": win_start.isoformat(),
            "end": win_end.isoformat(),
        },
        "stats": {
            "total": len(reviews),
            "app_store": app_count,
            "play_store": play_count,
            "duplicates_removed": norm.duplicates_removed,
            "outside_window": norm.outside_window,
            "content_filtered": filter_stats.total_removed,
            "filtered_short": filter_stats.removed_short,
            "filtered_emoji": filter_stats.removed_emoji,
            "filtered_non_english": filter_stats.removed_non_english,
            "earliest_review": start,
            "latest_review": end,
        },
        "warnings": all_warnings,
        "reviews": [r.to_dict() for r in reviews],
    }

    for review in payload["reviews"]:
        ReviewRecord.validate(review)
        for key in FORBIDDEN_FIELDS:
            if key in review:
                raise IngestionError(f"PII field leaked into output: {key}")

    out = output_path or cfg.reviews_output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    return IngestResult(
        output_path=out,
        review_window_weeks=window_weeks,
        window_start=win_start.isoformat(),
        window_end=win_end.isoformat(),
        total_reviews=len(reviews),
        app_store_count=app_count,
        play_store_count=play_count,
        duplicates_removed=norm.duplicates_removed,
        outside_window=norm.outside_window,
        content_filtered=filter_stats.total_removed,
        warnings=all_warnings,
    )


__all__ = ["run_ingestion", "IngestResult", "EmptyExportError", "IngestionError"]
