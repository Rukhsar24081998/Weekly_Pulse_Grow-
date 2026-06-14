"""Theme aggregation, ranking, and quote selection."""

from __future__ import annotations

from collections import Counter, defaultdict

from src.themes.models import ReviewAssignment, ThemeStats, ThemeTaxonomy


def _word_count(text: str) -> int:
    return len(text.split())


def map_to_display_theme(theme_id: str, top_theme_ids: set[str], fallback: str) -> str:
    if theme_id in top_theme_ids:
        return theme_id
    return fallback


def rank_themes(
    assignments: list[ReviewAssignment],
    taxonomy: ThemeTaxonomy,
    max_themes: int = 5,
) -> tuple[list[str], dict[str, str]]:
    """Return top theme IDs and mapping for tail themes merged into fallback."""
    counts = Counter(a.theme_id for a in assignments)
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))

    if len(ranked) <= max_themes:
        top_ids = [theme_id for theme_id, _ in ranked]
        return top_ids, {}

    top_ids = [theme_id for theme_id, _ in ranked[:max_themes]]
    top_set = set(top_ids)
    merge_map = {
        theme_id: taxonomy.fallback_theme_id
        for theme_id, _ in ranked[max_themes:]
        if theme_id not in top_set
    }
    return top_ids, merge_map


def effective_theme_id(
    assignment: ReviewAssignment,
    merge_map: dict[str, str],
    top_theme_ids: set[str],
    fallback: str,
) -> str:
    theme_id = assignment.theme_id
    if theme_id in merge_map:
        return merge_map[theme_id]
    return map_to_display_theme(theme_id, top_theme_ids, fallback)


def aggregate_theme_stats(
    assignments: list[ReviewAssignment],
    taxonomy: ThemeTaxonomy,
    max_themes: int = 5,
    summaries: dict[str, str] | None = None,
) -> tuple[list[ThemeStats], dict[str, str], set[str]]:
    """Build ranked theme stats with quote candidates."""
    top_ids, merge_map = rank_themes(assignments, taxonomy, max_themes=max_themes)
    top_set = set(top_ids)
    fallback = taxonomy.fallback_theme_id

    ratings: dict[str, list[int]] = defaultdict(list)
    by_display: dict[str, list[ReviewAssignment]] = defaultdict(list)

    for assignment in assignments:
        display_id = effective_theme_id(assignment, merge_map, top_set, fallback)
        ratings[display_id].append(assignment.review.rating)
        by_display[display_id].append(assignment)

    counts = Counter()
    for assignment in assignments:
        display_id = effective_theme_id(assignment, merge_map, top_set, fallback)
        counts[display_id] += 1

    theme_map = taxonomy.theme_by_id()
    stats: list[ThemeStats] = []
    summaries = summaries or {}

    for rank, theme_id in enumerate(
        sorted(counts.keys(), key=lambda tid: (-counts[tid], tid))[:max_themes],
        start=1,
    ):
        theme_ratings = ratings[theme_id]
        negative = sum(1 for rating in theme_ratings if rating <= 2)
        if theme_id in theme_map:
            label = theme_map[theme_id].label
        else:
            label = theme_id

        stats.append(
            ThemeStats(
                theme_id=theme_id,
                label=label,
                review_count=counts[theme_id],
                avg_rating=round(sum(theme_ratings) / len(theme_ratings), 2),
                negative_pct=round(100 * negative / len(theme_ratings), 1),
                rank=rank,
                summary=summaries.get(theme_id),
                sample_review_ids=_select_sample_ids(by_display[theme_id], max_samples=10),
                quote_candidate_ids=_select_quote_ids(by_display[theme_id], max_quotes=5),
            )
        )

    return stats, merge_map, top_set


def _select_sample_ids(assignments: list[ReviewAssignment], max_samples: int) -> list[str]:
    ordered = sorted(
        assignments,
        key=lambda a: (a.review.rating, a.review.review_date),
    )
    return [a.review.id for a in ordered[:max_samples]]


def _select_quote_ids(assignments: list[ReviewAssignment], max_quotes: int) -> list[str]:
    candidates = [
        a
        for a in assignments
        if 6 <= _word_count(a.review.text) <= 40 and a.review.rating <= 3
    ]
    candidates.sort(key=lambda a: (a.review.rating, -_word_count(a.review.text)))
    if not candidates:
        candidates = sorted(assignments, key=lambda a: (a.review.rating, -_word_count(a.review.text)))
    return [a.review.id for a in candidates[:max_quotes]]


def total_quote_candidates(theme_stats: list[ThemeStats]) -> int:
    return sum(len(theme.quote_candidate_ids) for theme in theme_stats)
