"""Rule-based theme assignment (Tier 1)."""

from __future__ import annotations

from src.ingest.models import ReviewRecord
from src.themes.models import ReviewAssignment, ThemeTaxonomy


def _review_text(review: ReviewRecord) -> str:
    parts = [review.text]
    if review.title:
        parts.append(review.title)
    return " ".join(parts).lower()


def find_matching_themes(review: ReviewRecord, taxonomy: ThemeTaxonomy) -> list[tuple[str, str]]:
    """Return list of (theme_id, keyword) matches."""
    combined = _review_text(review)
    matches: list[tuple[str, str]] = []
    for theme in taxonomy.themes:
        for keyword in theme.keywords:
            if keyword.lower() in combined:
                matches.append((theme.id, keyword))
                break
    return matches


def assign_review_rules(review: ReviewRecord, taxonomy: ThemeTaxonomy) -> ReviewAssignment:
    """Assign a theme using keyword rules; mark ambiguous when Groq should decide."""
    raw_matches = find_matching_themes(review, taxonomy)
    if not raw_matches:
        return ReviewAssignment(
            review=review,
            theme_id=taxonomy.fallback_theme_id,
            method="rules_fallback",
            ambiguous=True,
            matched_keywords=[],
        )

    theme_ids = list(dict.fromkeys(theme_id for theme_id, _ in raw_matches))
    keywords = [kw for _, kw in raw_matches]

    if len(theme_ids) == 1:
        return ReviewAssignment(
            review=review,
            theme_id=theme_ids[0],
            method="rules",
            ambiguous=False,
            matched_keywords=keywords,
        )

    theme_map = taxonomy.theme_by_id()
    matched_themes = [theme_map[tid] for tid in theme_ids if tid in theme_map]
    matched_themes.sort(key=lambda t: t.priority)
    best_priority = matched_themes[0].priority
    best = [t for t in matched_themes if t.priority == best_priority]

    if len(best) == 1:
        return ReviewAssignment(
            review=review,
            theme_id=best[0].id,
            method="rules",
            ambiguous=False,
            matched_keywords=keywords,
        )

    return ReviewAssignment(
        review=review,
        theme_id=best[0].id,
        method="rules_tie",
        ambiguous=True,
        matched_keywords=keywords,
    )


def assign_all_rules(
    reviews: list[ReviewRecord],
    taxonomy: ThemeTaxonomy,
) -> list[ReviewAssignment]:
    return [assign_review_rules(review, taxonomy) for review in reviews]
