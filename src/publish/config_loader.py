"""Load Phase 4 publish configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml

from src.env_loader import load_env
from src.paths import ROOT, deliverable


@dataclass
class PublishConfig:
    display_name: str
    mcp_server_url: str
    doc_title_template: str
    email_subject_template: str
    pulse_md_input: Path
    pulse_json_input: Path
    doc_metadata_output: Path
    run_metadata_output: Path
    google_doc_id: str | None
    draft_recipient: str | None


def load_publish_config(config_path: Path | None = None) -> PublishConfig:
    load_env()
    path = config_path or ROOT / "config" / "product.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    product = data["product"]
    publish = data.get("publish", {})

    mcp_url = os.environ.get("MCP_SERVER_URL", publish.get("mcp_server_url", "")).strip()
    doc_id = os.environ.get("PUBLISH_GOOGLE_DOC_ID", publish.get("google_doc_id", "")).strip()
    recipient = os.environ.get("DRAFT_RECIPIENT", publish.get("draft_recipient", "")).strip()

    return PublishConfig(
        display_name=product["display_name"],
        mcp_server_url=mcp_url.rstrip("/"),
        doc_title_template=str(
            publish.get("doc_title_template", "{display_name} Weekly Pulse — {date}")
        ),
        email_subject_template=str(
            publish.get(
                "email_subject_template",
                "Weekly App Review Pulse — {display_name} — {date}",
            )
        ),
        pulse_md_input=deliverable(3, "pulse_md"),
        pulse_json_input=deliverable(3, "pulse_json"),
        doc_metadata_output=deliverable(4, "doc_metadata"),
        run_metadata_output=deliverable(5, "run_metadata"),
        google_doc_id=doc_id or None,
        draft_recipient=recipient or None,
    )
