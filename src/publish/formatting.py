"""Plain-text and Google Doc formatting for publish steps."""

from __future__ import annotations

from datetime import datetime, timezone

from src.pulse.formatting import format_avg_rating, format_display_date, format_store
from src.pulse.models import PulseDocument


def strip_leading_markdown_title(markdown: str) -> str:
    """Remove a leading # title line so doc append does not duplicate headings."""
    body = markdown.strip()
    if not body.startswith("# "):
        return body
    _, _, rest = body.partition("\n")
    return rest.strip()


def build_doc_entry(title: str, pulse: PulseDocument) -> str:
    """Formatted section for append_to_doc — one clean block per weekly run."""
    published = datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    separator = "─" * 52
    body = strip_leading_markdown_title(pulse.markdown)
    return (
        f"\n\n{separator}\n"
        f"{title}\n"
        f"Published {published}\n"
        f"{separator}\n\n"
        f"{body}\n"
    )


def build_plain_email_body(pulse: PulseDocument, *, doc_url: str | None = None) -> str:
    """Leadership-ready plain text for Gmail drafts (no raw markdown)."""
    lines = [
        "WEEKLY APP REVIEW PULSE",
        "=" * 24,
        "",
        f"Product:     {pulse.product}",
        f"Week ending: {format_display_date(pulse.week_ending)}",
        (
            f"Window:      {format_display_date(pulse.window_start)} – "
            f"{format_display_date(pulse.window_end)} "
            f"({pulse.review_window_weeks} weeks)"
        ),
        (
            f"Sample:      {pulse.sample_size:,} reviews "
            f"(from {pulse.total_reviews:,} total)"
        ),
        "",
    ]

    if doc_url:
        lines.extend(
            [
                f"Formatted report: {doc_url}",
                "",
                "Summary below — review before forwarding.",
                "",
            ]
        )

    lines.extend(["TOP THEMES", "-" * 10, ""])
    for theme in pulse.top_themes:
        lines.append(f"{theme.rank}. {theme.label}")
        lines.append(
            f"   {theme.review_count:,} reviews · {format_avg_rating(theme.avg_rating)} avg"
        )
        lines.append(f"   {theme.summary}")
        lines.append("")

    lines.extend(["USER QUOTES", "-" * 11, ""])
    for quote in pulse.quotes:
        lines.append(f"• {quote.rating}★ · {format_store(quote.store)}")
        lines.append(f'  "{quote.text}"')
        lines.append("")

    lines.extend(["RECOMMENDED ACTIONS", "-" * 20, ""])
    for index, action in enumerate(pulse.action_ideas, start=1):
        lines.append(f"{index}. {action.action}")
        lines.append(f"   {action.rationale}")

    lines.extend(["", "—", "Draft only. Send manually after review.", ""])
    return "\n".join(lines)
