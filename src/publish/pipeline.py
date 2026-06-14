"""Phase 4 Google Doc publish orchestration."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from src.guardrails.validate import count_words
from src.publish.config_loader import PublishConfig, load_publish_config
from src.publish.exceptions import McpError, PublishError, PublishValidationError
from src.publish.mcp_client import McpHttpClient, google_doc_url
from src.publish.models import DocPublishResult
from src.publish.preflight import run_preflight
from src.publish.formatting import build_doc_entry
from src.pulse.models import PulseDocument


def build_doc_title(config: PublishConfig, pulse: PulseDocument) -> str:
    return config.doc_title_template.format(
        display_name=config.display_name,
        date=pulse.week_ending,
    )


def build_doc_content(title: str, pulse: PulseDocument) -> str:
    return build_doc_entry(title, pulse)


def _extract_doc_id(result: dict) -> str | None:
    for key in ("document_id", "doc_id", "google_doc_id"):
        value = result.get(key)
        if value:
            return str(value)
    return None


def run_doc_publish(
    *,
    config: PublishConfig | None = None,
    pulse_md_path: Path | None = None,
    pulse_json_path: Path | None = None,
    output_path: Path | None = None,
    doc_id: str | None = None,
    dry_run: bool = False,
) -> DocPublishResult:
    cfg = config or load_publish_config()
    md_path = pulse_md_path or cfg.pulse_md_input
    json_path = pulse_json_path or cfg.pulse_json_input
    metadata_path = output_path or cfg.doc_metadata_output

    if not cfg.mcp_server_url:
        raise PublishError(
            "MCP_SERVER_URL is not set — add it to .env or config/product.yaml publish.mcp_server_url"
        )

    pulse = run_preflight(json_path, md_path)
    title = build_doc_title(cfg, pulse)
    content = build_doc_content(title, pulse)
    word_count = count_words(pulse.markdown)

    if dry_run:
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "phase": 4,
            "dry_run": True,
            "doc_title": title,
            "week_ending": pulse.week_ending,
            "word_count": word_count,
            "validation_passed": True,
            "mcp_server_url": cfg.mcp_server_url,
        }
        metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return DocPublishResult(
            output_path=str(metadata_path),
            doc_title=title,
            google_doc_id="dry-run",
            google_doc_url="",
            mcp_tool="dry_run",
            week_ending=pulse.week_ending,
            word_count=word_count,
            validation_passed=True,
        )

    client = McpHttpClient(cfg.mcp_server_url)
    target_doc_id = doc_id or cfg.google_doc_id
    mcp_tool = "append_to_doc"
    doc_url = ""

    try:
        if client.has_tool("create_document"):
            create_result = client.create_document(title=title, content=content)
            created_id = _extract_doc_id(create_result)
            if created_id:
                target_doc_id = created_id
                mcp_tool = "create_document"
                doc_url = str(create_result.get("document_url") or google_doc_url(created_id))
            elif not target_doc_id:
                raise McpError("create_document succeeded but no document_id returned")

        if not target_doc_id:
            raise PublishError(
                "No google_doc_id available. Set PUBLISH_GOOGLE_DOC_ID in .env, pass --doc-id, "
                "or deploy create_document on your MCP server "
                "(see Docs/mcp-server-integration.md)."
            )

        if mcp_tool != "create_document":
            append_result = client.append_to_doc(doc_id=target_doc_id, content=content)
            returned_id = _extract_doc_id(append_result) or target_doc_id
            target_doc_id = returned_id
            doc_url = str(append_result.get("document_url") or google_doc_url(target_doc_id))
    except McpError:
        raise
    except PublishError:
        raise
    except Exception as exc:
        raise PublishError(f"Unexpected publish failure: {exc}") from exc

    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "phase": 4,
        "product": pulse.product,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "week_ending": pulse.week_ending,
        "doc_title": title,
        "google_doc_id": target_doc_id,
        "google_doc_url": doc_url,
        "mcp_server_url": cfg.mcp_server_url,
        "mcp_tool": mcp_tool,
        "pulse_word_count": word_count,
        "validation_passed": True,
        "review_window": {
            "start": pulse.window_start,
            "end": pulse.window_end,
            "weeks": pulse.review_window_weeks,
        },
    }
    metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return DocPublishResult(
        output_path=str(metadata_path),
        doc_title=title,
        google_doc_id=target_doc_id,
        google_doc_url=doc_url,
        mcp_tool=mcp_tool,
        week_ending=pulse.week_ending,
        word_count=word_count,
        validation_passed=True,
    )
