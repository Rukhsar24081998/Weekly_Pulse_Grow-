"""Phase 5 Gmail draft publish orchestration."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from src.guardrails.validate import count_words
from src.publish.config_loader import PublishConfig, load_publish_config
from src.publish.doc_metadata_loader import load_doc_metadata
from src.publish.exceptions import DraftError, McpError, PublishError
from src.publish.mcp_client import McpHttpClient
from src.publish.models import DraftPublishResult
from src.publish.preflight import run_preflight
from src.publish.run_metadata import write_run_metadata
from src.publish.formatting import build_plain_email_body
from src.pulse.models import PulseDocument

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def build_email_subject(config: PublishConfig, pulse: PulseDocument) -> str:
    return config.email_subject_template.format(
        display_name=config.display_name,
        date=pulse.week_ending,
    )


def build_email_body(pulse: PulseDocument, *, doc_url: str | None = None) -> str:
    return build_plain_email_body(pulse, doc_url=doc_url)


def _resolve_recipient(config: PublishConfig, recipient: str | None) -> str:
    address = (recipient or config.draft_recipient or "").strip()
    if not address:
        raise DraftError(
            "DRAFT_RECIPIENT is not set — add your email to .env or pass --to"
        )
    if not _EMAIL_RE.match(address):
        raise DraftError(f"Invalid recipient email: {address}")
    return address


def _extract_draft_id(result: dict) -> str | None:
    for key in ("draft_id", "gmail_draft_id", "id"):
        value = result.get(key)
        if value:
            return str(value)
    return None


def run_draft_publish(
    *,
    config: PublishConfig | None = None,
    pulse_md_path: Path | None = None,
    pulse_json_path: Path | None = None,
    doc_metadata_path: Path | None = None,
    run_metadata_path: Path | None = None,
    recipient: str | None = None,
    dry_run: bool = False,
    write_run_json: bool = True,
) -> DraftPublishResult:
    cfg = config or load_publish_config()
    md_path = pulse_md_path or cfg.pulse_md_input
    json_path = pulse_json_path or cfg.pulse_json_input
    doc_meta_path = doc_metadata_path or cfg.doc_metadata_output
    run_path = run_metadata_path or cfg.run_metadata_output

    if not cfg.mcp_server_url:
        raise PublishError(
            "MCP_SERVER_URL is not set — add it to .env or config/product.yaml publish.mcp_server_url"
        )

    pulse = run_preflight(json_path, md_path)
    to_address = _resolve_recipient(cfg, recipient)
    subject = build_email_subject(cfg, pulse)
    doc_meta = load_doc_metadata(doc_meta_path)
    doc_url = doc_meta.get("google_doc_url") or None
    body = build_email_body(pulse, doc_url=doc_url)
    word_count = count_words(pulse.markdown)

    if dry_run:
        payload = {
            "phase": 5,
            "dry_run": True,
            "subject": subject,
            "recipient": to_address,
            "week_ending": pulse.week_ending,
            "word_count": word_count,
            "validation_passed": True,
            "mcp_server_url": cfg.mcp_server_url,
        }
        run_path.parent.mkdir(parents=True, exist_ok=True)
        run_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return DraftPublishResult(
            output_path=str(run_path),
            subject=subject,
            recipient=to_address,
            gmail_draft_id="dry-run",
            week_ending=pulse.week_ending,
            word_count=word_count,
            validation_passed=True,
        )

    client = McpHttpClient(cfg.mcp_server_url)
    try:
        result = client.create_email_draft(to=to_address, subject=subject, body=body)
    except McpError:
        raise

    draft_id = _extract_draft_id(result)
    if not draft_id:
        raise DraftError("create_email_draft succeeded but no draft_id returned")

    if write_run_json:
        write_run_metadata(
            run_path,
            pulse=pulse,
            doc_metadata=doc_meta,
            gmail_draft_id=draft_id,
            draft_recipient=to_address,
            email_subject=subject,
            mcp_server_url=cfg.mcp_server_url,
        )

    return DraftPublishResult(
        output_path=str(run_path),
        subject=subject,
        recipient=to_address,
        gmail_draft_id=draft_id,
        week_ending=pulse.week_ending,
        word_count=word_count,
        validation_passed=True,
    )
