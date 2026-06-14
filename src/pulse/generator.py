"""Template-based weekly pulse generator."""

from __future__ import annotations

from src.guardrails.redact import redact_text
from src.guardrails.validate import count_words
from src.ingest.models import ReviewRecord
from src.pulse.config_loader import PulseConfig
from src.pulse.formatting import (
    format_avg_rating,
    format_display_date,
    format_sentiment,
    format_store,
)
from src.pulse.models import PulseAction, PulseDocument, PulseQuote, PulseTheme

ACTION_TEMPLATES: dict[str, tuple[str, str]] = {
    "performance": (
        "Investigate app hangs and latency during market hours",
        "High volume of lag and crash reports during trading sessions",
    ),
    "discovery": (
        "Fix F&O and options chain order execution issues",
        "Users report broken trading features and chart failures",
    ),
    "statements": (
        "Add in-app tax statement and P&L download status tracker",
        "Portfolio report issues drive strong negative sentiment",
    ),
    "payments": (
        "Improve UPI and SIP payment failure recovery flows",
        "Payment failures block deposits and recurring investments",
    ),
    "kyc": (
        "Add in-app KYC verification status with ETA",
        "Pending verification drives support contacts and drop-off",
    ),
    "login": (
        "Stabilize OTP delivery and login during peak hours",
        "Login and OTP failures block access at critical moments",
    ),
    "withdrawals": (
        "Reduce redemption and payout settlement delays",
        "Users report slow or failed withdrawal credits",
    ),
    "onboarding": (
        "Streamline account opening for first-time investors",
        "New users hit friction during registration and first setup",
    ),
}


def _truncate_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[: max_words - 1]) + "…"


def _default_summary(theme: dict) -> str:
    avg = float(theme["avg_rating"])
    negative = float(theme.get("negative_pct", 0))
    if negative >= 60:
        return "Strong negative sentiment — repeated failures reported in this area."
    if avg <= 2.5:
        return "Low ratings — reliability and correctness concerns dominate feedback."
    if avg >= 4.0:
        return "Mostly positive — isolated issues still worth tracking."
    return "Mixed sentiment — recurring friction across user sessions."


def _theme_summary(theme: dict) -> str:
    summary = theme.get("summary")
    if summary:
        return str(summary)
    return _default_summary(theme)


def _pick_quote(
    theme: dict,
    reviews_index: dict[str, ReviewRecord],
    max_quote_words: int,
) -> PulseQuote | None:
    for review_id in theme.get("quote_candidate_ids", []):
        review = reviews_index.get(review_id)
        if not review:
            continue
        text = _truncate_words(review.text.strip(), max_quote_words)
        return PulseQuote(
            theme_id=theme["theme_id"],
            text=text,
            rating=review.rating,
            store=review.store,
        )
    for review_id in theme.get("sample_review_ids", []):
        review = reviews_index.get(review_id)
        if not review:
            continue
        text = _truncate_words(review.text.strip(), max_quote_words)
        return PulseQuote(
            theme_id=theme["theme_id"],
            text=text,
            rating=review.rating,
            store=review.store,
        )
    return None


def _action_for_theme(theme: dict) -> PulseAction:
    theme_id = theme["theme_id"]
    action, rationale = ACTION_TEMPLATES.get(
        theme_id,
        (
            f"Prioritize fixes for {theme['label'].lower()}",
            f"{theme['review_count']} reviews mention this area",
        ),
    )
    if theme.get("negative_pct", 0) >= 50:
        rationale = f"{int(theme['negative_pct'])}% negative; {rationale.lower()}"
    return PulseAction(theme_id=theme_id, action=action, rationale=rationale)


def _render_markdown(pulse: PulseDocument) -> str:
    window = (
        f"{format_display_date(pulse.window_start)} – "
        f"{format_display_date(pulse.window_end)}"
    )
    lines = [
        f"# {pulse.product} — Weekly Pulse",
        "",
        (
            f"**Week ending {format_display_date(pulse.week_ending)}** · "
            f"{pulse.review_window_weeks}-week window ({window}) · "
            f"**{pulse.sample_size:,}** reviews sampled from **{pulse.total_reviews:,}**"
        ),
        "",
        "## Top themes",
        "",
    ]

    for theme in pulse.top_themes:
        sentiment = format_sentiment(theme.avg_rating)
        lines.extend(
            [
                f"**{theme.rank}. {theme.label}**",
                (
                    f"{theme.review_count:,} reviews · "
                    f"{format_avg_rating(theme.avg_rating)} avg · {sentiment}"
                ),
                theme.summary,
                "",
            ]
        )

    lines.extend(["## User quotes", ""])
    for quote in pulse.quotes:
        lines.extend(
            [
                f"**{quote.rating}★ · {format_store(quote.store)}**",
                f"> {quote.text}",
                "",
            ]
        )

    lines.extend(["## Recommended actions", ""])
    for index, action in enumerate(pulse.action_ideas, start=1):
        lines.append(
            f"{index}. **{action.action}** — {action.rationale}"
        )

    return "\n".join(lines) + "\n"


def generate_pulse(
    themes_payload: dict,
    reviews_index: dict[str, ReviewRecord],
    config: PulseConfig,
) -> PulseDocument:
    top_themes_raw = themes_payload.get("top_pulse_themes") or themes_payload.get("themes", [])[: config.theme_count]
    top_themes_raw = top_themes_raw[: config.theme_count]

    if len(top_themes_raw) < config.theme_count:
        raise ValueError(f"Need at least {config.theme_count} themes in themes.json")

    source = themes_payload.get("source", {})
    ingest_window = source.get("ingest_window", {})
    sample = themes_payload.get("sample", {})

    pulse_themes: list[PulseTheme] = []
    quotes: list[PulseQuote] = []
    actions: list[PulseAction] = []

    for theme in top_themes_raw:
        pulse_themes.append(
            PulseTheme(
                rank=int(theme["rank"]),
                theme_id=theme["theme_id"],
                label=theme["label"],
                summary=_theme_summary(theme),
                review_count=int(theme["review_count"]),
                avg_rating=float(theme["avg_rating"]),
            )
        )
        quote = _pick_quote(theme, reviews_index, config.max_quote_words)
        if quote:
            quotes.append(quote)
        actions.append(_action_for_theme(theme))

    window_end = ingest_window.get("end", "unknown")
    window_start = ingest_window.get("start", "unknown")

    pulse = PulseDocument(
        product=themes_payload.get("product", config.display_name),
        week_ending=window_end,
        review_window_weeks=_infer_window_weeks(window_start, window_end),
        window_start=window_start,
        window_end=window_end,
        total_reviews=int(sample.get("sampled_from", sample.get("sample_size", 0))),
        sample_size=int(sample.get("sample_size", 0)),
        top_themes=pulse_themes,
        quotes=quotes,
        action_ideas=actions[: config.action_count],
        word_count=0,
        markdown="",
    )

    pulse.markdown = _render_markdown(pulse)
    pulse.word_count = count_words(pulse.markdown)

    if pulse.word_count > config.max_words:
        pulse = _shorten_pulse(pulse, config)

    pulse.markdown = redact_text(pulse.markdown)
    for quote in pulse.quotes:
        quote.text = redact_text(quote.text)
    pulse.word_count = count_words(pulse.markdown)
    return pulse


def _infer_window_weeks(start: str, end: str) -> int:
    try:
        from datetime import date

        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end)
        days = (end_date - start_date).days
        return max(1, round(days / 7))
    except ValueError:
        return 12


def _shorten_pulse(pulse: PulseDocument, config: PulseConfig) -> PulseDocument:
    """Trim quotes and summaries until word count fits."""
    for quote in pulse.quotes:
        quote.text = _truncate_words(quote.text, max(8, config.max_quote_words - 6))

    for theme in pulse.top_themes:
        theme.summary = _truncate_words(theme.summary, 12)

    for action in pulse.action_ideas:
        action.rationale = _truncate_words(action.rationale, 10)

    pulse.markdown = _render_markdown(pulse)
    pulse.word_count = count_words(pulse.markdown)

    if pulse.word_count > config.max_words:
        pulse.markdown = _truncate_words(pulse.markdown, config.max_words)
        pulse.word_count = count_words(pulse.markdown)

    return pulse
