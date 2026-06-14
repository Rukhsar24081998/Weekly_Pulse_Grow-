"""Display formatting helpers for pulse output."""

from __future__ import annotations

from datetime import date

STORE_LABELS = {
    "play_store": "Play Store",
    "app_store": "App Store",
}


def format_store(store: str) -> str:
    return STORE_LABELS.get(store, store.replace("_", " ").title())


def format_avg_rating(avg: float) -> str:
    return f"{avg:.1f}★"


def format_display_date(iso: str) -> str:
    try:
        return date.fromisoformat(iso).strftime("%d %b %Y")
    except ValueError:
        return iso


def format_sentiment(avg_rating: float, negative_pct: float = 0) -> str:
    if negative_pct >= 60:
        return "strong negative sentiment"
    if avg_rating <= 2.5:
        return "low ratings"
    if avg_rating >= 4.0:
        return "mostly positive"
    return "mixed sentiment"
