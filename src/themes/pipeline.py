"""Theme clustering orchestration (Phase 2)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from src.themes.aggregate import aggregate_theme_stats, effective_theme_id, total_quote_candidates
from src.themes.config_loader import ThemeClusterConfig, load_taxonomy, load_theme_config
from src.themes.exceptions import EmptyCorpusError, GroqError
from src.themes.groq_client import GroqClient
from src.themes.loader import load_reviews_json
from src.themes.models import GroqUsage, ThemePipelineResult, ThemeStats
from src.themes.rules import assign_all_rules
from src.themes.sampler import stratified_subsample


def _chunk(items: list, size: int) -> list[list]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def _build_samples_by_theme(
    assignments,
    theme_stats: list[ThemeStats],
    merge_map,
    top_set,
    fallback,
    max_samples: int,
) -> dict[str, list]:
    from collections import defaultdict

    by_theme = defaultdict(list)
    for assignment in assignments:
        display_id = effective_theme_id(assignment, merge_map, top_set, fallback)
        by_theme[display_id].append(assignment.review)

    samples = {}
    for stat in theme_stats:
        pool = by_theme.get(stat.theme_id, [])
        samples[stat.theme_id] = pool[:max_samples]
    return samples


def run_theme_clustering(
    *,
    config: ThemeClusterConfig | None = None,
    reviews_path: Path | None = None,
    output_path: Path | None = None,
    use_groq: bool | None = None,
    dry_run_groq: bool = False,
) -> ThemePipelineResult:
    cfg = config or load_theme_config()
    in_path = reviews_path or cfg.reviews_input
    out_path = output_path or cfg.themes_output

    all_reviews, ingest_meta = load_reviews_json(in_path)
    if not all_reviews:
        raise EmptyCorpusError(f"No reviews found in {in_path}")

    sampled, sample_meta = stratified_subsample(
        all_reviews,
        max_reviews=cfg.max_reviews,
        seed=cfg.sample_seed,
    )

    taxonomy = load_taxonomy(cfg.themes_yaml)
    assignments = assign_all_rules(sampled, taxonomy)
    warnings: list[str] = []

    groq_client = GroqClient(cfg.groq, dry_run=dry_run_groq)
    if use_groq is False:
        should_use_groq = False
    elif use_groq is True:
        should_use_groq = groq_client.available
    else:
        should_use_groq = groq_client.available

    if not should_use_groq:
        groq_client.usage.enabled = False
        if use_groq is None and not groq_client.api_key:
            warnings.append("Groq disabled or GROQ_API_KEY missing — rules-only path")
        elif use_groq is None and not cfg.groq.enabled:
            warnings.append("Groq disabled in config — rules-only path")

    ambiguous = [a for a in assignments if a.ambiguous]
    if should_use_groq and ambiguous:
        batches = _chunk(ambiguous, cfg.groq.batch_size)
        for batch in batches:
            try:
                labels = groq_client.classify_batch(
                    [item.review for item in batch],
                    taxonomy,
                )
            except GroqError as exc:
                warnings.append(f"Groq classify batch failed: {exc}")
                continue
            for assignment in batch:
                theme_id = labels.get(assignment.review.id)
                if theme_id:
                    assignment.theme_id = theme_id
                    assignment.method = "groq"
                    assignment.ambiguous = False

    summaries: dict[str, str] = {}
    theme_stats, merge_map, top_set = aggregate_theme_stats(
        assignments,
        taxonomy,
        max_themes=cfg.max_themes,
    )

    if should_use_groq and theme_stats:
        samples_by_theme = _build_samples_by_theme(
            assignments,
            theme_stats,
            merge_map,
            top_set,
            taxonomy.fallback_theme_id,
            cfg.groq.max_samples_per_theme,
        )
        try:
            summaries = groq_client.summarize_themes(theme_stats, samples_by_theme, taxonomy)
        except GroqError as exc:
            warnings.append(f"Groq summary failed: {exc}")

        theme_stats, merge_map, top_set = aggregate_theme_stats(
            assignments,
            taxonomy,
            max_themes=cfg.max_themes,
            summaries=summaries,
        )

    top_pulse = theme_stats[: cfg.top_pulse_themes]
    payload = {
        "product": cfg.display_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "reviews_path": str(in_path),
            "ingest_window": ingest_meta.get("window"),
        },
        "sample": sample_meta,
        "taxonomy": {
            "fallback_theme_id": taxonomy.fallback_theme_id,
            "theme_ids": [theme.id for theme in taxonomy.themes],
        },
        "stats": {
            "total_assignments": len(assignments),
            "ambiguous_input": len(ambiguous),
            "themes_in_output": len(theme_stats),
            "quote_candidates": total_quote_candidates(theme_stats),
        },
        "groq_usage": groq_client.usage.to_dict(),
        "warnings": warnings,
        "themes": [theme.to_dict() for theme in theme_stats],
        "top_pulse_themes": [theme.to_dict() for theme in top_pulse],
        "assignments": [
            {
                "review_id": a.review.id,
                "theme_id": effective_theme_id(
                    a,
                    merge_map,
                    top_set,
                    taxonomy.fallback_theme_id,
                ),
                "raw_theme_id": a.theme_id,
                "method": a.method,
                "rating": a.review.rating,
                "review_date": a.review.review_date,
            }
            for a in assignments
        ],
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return ThemePipelineResult(
        output_path=str(out_path),
        sample_size=sample_meta["sample_size"],
        sampled_from=sample_meta["sampled_from"],
        total_assignments=len(assignments),
        theme_count=len(theme_stats),
        top_theme_ids=[theme.theme_id for theme in top_pulse],
        groq_usage=groq_client.usage,
        warnings=warnings,
    )
