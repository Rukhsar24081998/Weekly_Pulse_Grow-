"""Tests for pulse and publish formatting."""

from __future__ import annotations

from src.publish.formatting import build_doc_entry, build_plain_email_body
from src.pulse.formatting import format_display_date, format_store
from src.pulse.models import PulseAction, PulseDocument, PulseQuote, PulseTheme


def _sample_pulse() -> PulseDocument:
    return PulseDocument(
        product="Groww App",
        week_ending="2026-06-14",
        review_window_weeks=12,
        window_start="2026-03-22",
        window_end="2026-06-14",
        total_reviews=2269,
        sample_size=1000,
        top_themes=[
            PulseTheme(
                1,
                "performance",
                "App performance, bugs & crashes",
                "Mixed sentiment — recurring friction across user sessions.",
                607,
                3.32,
            ),
        ],
        quotes=[
            PulseQuote(
                "performance",
                "App crashes during market hours.",
                1,
                "play_store",
            ),
        ],
        action_ideas=[
            PulseAction(
                "performance",
                "Investigate app hangs during market hours",
                "High volume of lag reports",
            ),
        ],
        word_count=100,
        markdown=(
            "# Groww App — Weekly Pulse\n\n"
            "**Week ending 14 Jun 2026** · sample metadata\n\n"
            "## Top themes\n\n"
            "Body content here.\n"
        ),
        validation_passed=True,
    )


class TestPulseFormatting:
    def test_format_store(self):
        assert format_store("play_store") == "Play Store"
        assert format_store("app_store") == "App Store"

    def test_format_display_date(self):
        assert format_display_date("2026-06-14") == "14 Jun 2026"


class TestPublishFormatting:
    def test_email_is_plain_text_not_markdown(self):
        body = build_plain_email_body(
            _sample_pulse(),
            doc_url="https://docs.google.com/document/d/abc/edit",
        )
        assert "WEEKLY APP REVIEW PULSE" in body
        assert "TOP THEMES" in body
        assert "Play Store" in body
        assert "## Top themes" not in body
        assert "**Week ending" not in body

    def test_doc_entry_strips_duplicate_title(self):
        content = build_doc_entry("Groww App Weekly Pulse — 2026-06-14", _sample_pulse())
        assert content.count("# Groww App — Weekly Pulse") == 0
        assert "Groww App Weekly Pulse — 2026-06-14" in content
        assert "Body content here." in content
