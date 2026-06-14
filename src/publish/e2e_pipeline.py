"""Phase 5 end-to-end publish orchestration (Doc + Gmail draft)."""

from __future__ import annotations

from pathlib import Path

from src.publish.config_loader import PublishConfig, load_publish_config
from src.publish.draft_pipeline import run_draft_publish
from src.publish.models import E2ERunResult
from src.publish.pipeline import run_doc_publish


def run_e2e_publish(
    *,
    config: PublishConfig | None = None,
    doc_id: str | None = None,
    recipient: str | None = None,
    dry_run: bool = False,
    skip_doc: bool = False,
    skip_draft: bool = False,
) -> E2ERunResult:
    cfg = config or load_publish_config()

    doc_result = None
    if not skip_doc:
        doc_result = run_doc_publish(config=cfg, doc_id=doc_id, dry_run=dry_run)

    draft_result = None
    if not skip_draft:
        draft_result = run_draft_publish(
            config=cfg,
            recipient=recipient,
            dry_run=dry_run,
            write_run_json=not dry_run,
        )

    if dry_run:
        return E2ERunResult(
            output_path=str(cfg.run_metadata_output),
            google_doc_id=doc_result.google_doc_id if doc_result else "",
            google_doc_url=doc_result.google_doc_url if doc_result else "",
            gmail_draft_id=draft_result.gmail_draft_id if draft_result else "",
            week_ending=draft_result.week_ending if draft_result else "",
            validation_passed=True,
        )

    google_doc_id = doc_result.google_doc_id if doc_result else ""
    google_doc_url = doc_result.google_doc_url if doc_result else ""
    if not google_doc_id and cfg.doc_metadata_output.is_file():
        import json

        meta = json.loads(cfg.doc_metadata_output.read_text(encoding="utf-8"))
        google_doc_id = meta.get("google_doc_id", "")
        google_doc_url = meta.get("google_doc_url", "")

    assert draft_result is not None
    return E2ERunResult(
        output_path=draft_result.output_path,
        google_doc_id=google_doc_id,
        google_doc_url=google_doc_url,
        gmail_draft_id=draft_result.gmail_draft_id,
        week_ending=draft_result.week_ending,
        validation_passed=True,
    )
