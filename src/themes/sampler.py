"""Stratified subsample for Phase 2 Groq budget."""

from __future__ import annotations

from collections import defaultdict

from src.ingest.models import ReviewRecord


def stratified_subsample(
    reviews: list[ReviewRecord],
    max_reviews: int,
    seed: int,
) -> tuple[list[ReviewRecord], dict]:
    """Sample up to max_reviews, stratified by rating with recent-first tie-break."""
    if len(reviews) <= max_reviews:
        return list(reviews), {
            "sampled_from": len(reviews),
            "sample_size": len(reviews),
            "sample_seed": seed,
            "stratified_by": "rating",
        }

    by_rating: dict[int, list[ReviewRecord]] = defaultdict(list)
    for review in reviews:
        by_rating[review.rating].append(review)

    for pool in by_rating.values():
        pool.sort(key=lambda r: r.review_date, reverse=True)

    total = len(reviews)
    allocations: dict[int, int] = {}
    allocated = 0
    ratings = sorted(by_rating.keys())

    for rating in ratings:
        pool_size = len(by_rating[rating])
        count = int(max_reviews * pool_size / total)
        allocations[rating] = min(count, pool_size)
        allocated += allocations[rating]

    remainder = max_reviews - allocated
    for rating in sorted(ratings, key=lambda r: len(by_rating[r]), reverse=True):
        if remainder <= 0:
            break
        capacity = len(by_rating[rating]) - allocations[rating]
        extra = min(remainder, capacity)
        allocations[rating] += extra
        remainder -= extra

    selected: list[ReviewRecord] = []
    for rating, count in allocations.items():
        selected.extend(by_rating[rating][:count])

    selected.sort(key=lambda r: r.review_date, reverse=True)
    return selected, {
        "sampled_from": len(reviews),
        "sample_size": len(selected),
        "sample_seed": seed,
        "stratified_by": "rating",
    }
