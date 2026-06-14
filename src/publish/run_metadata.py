"""Build and write Phase 5 run metadata JSON."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from src.pulse.models import PulseDocument


def write_run_metadata(
    path: Path,
    *,
    pulse: PulseDocument,
    doc_metadata: dict,
    gmail_draft_id: str,
    draft_recipient: str,
    email_subject: str,
    mcp_server_url: str,
) -> dict:
    themes_used = [theme.theme_id for theme in pulse.top_themes]
    payload = {
        "phase": 5,
        "run_id": datetime.now(timezone.utc).isoformat(),
        "product": pulse.product,
        "week_ending": pulse.week_ending,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "review_window": {
            "start": pulse.window_start,
            "end": pulse.window_end,
            "weeks": pulse.review_window_weeks,
        },
        "stores": {
            "total_reviews": pulse.total_reviews,
            "sample_size": pulse.sample_size,
        },
        "themes_used": themes_used,
        "pulse_word_count": pulse.word_count,
        "validation_passed": True,
        "google_doc_id": doc_metadata.get("google_doc_id", ""),
        "google_doc_url": doc_metadata.get("google_doc_url", ""),
        "doc_title": doc_metadata.get("doc_title", ""),
        "gmail_draft_id": gmail_draft_id,
        "draft_recipient": draft_recipient,
        "email_subject": email_subject,
        "mcp_server_url": mcp_server_url,
        "pii_violations_blocked": 0,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload
