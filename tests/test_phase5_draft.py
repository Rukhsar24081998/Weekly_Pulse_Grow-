"""Phase 5 Gmail draft and E2E publish tests."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.publish.config_loader import PublishConfig
from src.publish.draft_pipeline import (
    build_email_body,
    build_email_subject,
    run_draft_publish,
)
from src.publish.e2e_pipeline import run_e2e_publish
from src.publish.exceptions import DraftError, PublishValidationError
from src.publish.mcp_client import McpHttpClient
from src.publish.run_metadata import write_run_metadata
from tests.test_phase4_publish import _sample_pulse, _write_pulse_artifacts


def _publish_config(tmp: Path, md_path: Path, json_path: Path, **overrides) -> PublishConfig:
    defaults = {
        "display_name": "Groww App",
        "mcp_server_url": "https://example.test",
        "doc_title_template": "{display_name} Weekly Pulse — {date}",
        "email_subject_template": "Weekly App Review Pulse — {display_name} — {date}",
        "pulse_md_input": md_path,
        "pulse_json_input": json_path,
        "doc_metadata_output": tmp / "doc_metadata.json",
        "run_metadata_output": tmp / "run.json",
        "google_doc_id": "abc123",
        "draft_recipient": "operator@example.com",
    }
    defaults.update(overrides)
    return PublishConfig(**defaults)


class TestEmailBuilder:
    def test_subject_template(self):
        config = _publish_config(Path("/tmp"), Path("a"), Path("b"))
        subject = build_email_subject(config, _sample_pulse())
        assert subject == "Weekly App Review Pulse — Groww App — 2026-06-13"

    def test_body_includes_pulse_and_doc_link(self):
        body = build_email_body(_sample_pulse(), doc_url="https://docs.google.com/document/d/abc/edit")
        assert "Google Doc:" in body
        assert "Sample body." in body


class TestDraftPipeline:
    def test_missing_recipient_blocked(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            pulse = _sample_pulse()
            md_path, json_path = _write_pulse_artifacts(tmp, pulse)
            config = _publish_config(tmp, md_path, json_path, draft_recipient=None)
            with pytest.raises(DraftError, match="DRAFT_RECIPIENT"):
                run_draft_publish(config=config, dry_run=True)

    @patch.object(McpHttpClient, "create_email_draft")
    def test_create_draft_via_mcp(self, mock_draft):
        mock_draft.return_value = {"status": "success", "draft_id": "draft789"}

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            pulse = _sample_pulse()
            md_path, json_path = _write_pulse_artifacts(tmp, pulse)
            doc_meta = {
                "google_doc_id": "abc123",
                "google_doc_url": "https://docs.google.com/document/d/abc123/edit",
                "doc_title": "Groww App Weekly Pulse — 2026-06-13",
            }
            (tmp / "doc_metadata.json").write_text(json.dumps(doc_meta), encoding="utf-8")
            config = _publish_config(tmp, md_path, json_path)
            config.doc_metadata_output = tmp / "doc_metadata.json"

            result = run_draft_publish(config=config)
            assert result.gmail_draft_id == "draft789"
            assert (tmp / "run.json").exists()
            payload = json.loads((tmp / "run.json").read_text(encoding="utf-8"))
            assert payload["gmail_draft_id"] == "draft789"
            assert payload["google_doc_id"] == "abc123"
            mock_draft.assert_called_once()

    def test_dry_run(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            pulse = _sample_pulse()
            md_path, json_path = _write_pulse_artifacts(tmp, pulse)
            config = _publish_config(tmp, md_path, json_path)
            result = run_draft_publish(config=config, dry_run=True)
            assert result.gmail_draft_id == "dry-run"


class TestRunMetadata:
    def test_write_run_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "run.json"
            pulse = _sample_pulse()
            write_run_metadata(
                path,
                pulse=pulse,
                doc_metadata={"google_doc_id": "abc", "google_doc_url": "https://example/doc"},
                gmail_draft_id="draft1",
                draft_recipient="me@example.com",
                email_subject="Weekly pulse",
                mcp_server_url="https://example.test",
            )
            payload = json.loads(path.read_text(encoding="utf-8"))
            assert payload["themes_used"] == ["performance", "discovery", "statements"]
            assert payload["gmail_draft_id"] == "draft1"


class TestE2E:
    @patch("src.publish.e2e_pipeline.run_draft_publish")
    @patch("src.publish.e2e_pipeline.run_doc_publish")
    def test_e2e_calls_doc_and_draft(self, mock_doc, mock_draft):
        from src.publish.models import DocPublishResult, DraftPublishResult

        mock_doc.return_value = DocPublishResult(
            output_path="doc.json",
            doc_title="title",
            google_doc_id="doc1",
            google_doc_url="https://example/doc",
            mcp_tool="append_to_doc",
            week_ending="2026-06-13",
            word_count=120,
            validation_passed=True,
        )
        mock_draft.return_value = DraftPublishResult(
            output_path="run.json",
            subject="subj",
            recipient="me@example.com",
            gmail_draft_id="draft1",
            week_ending="2026-06-13",
            word_count=120,
            validation_passed=True,
        )

        result = run_e2e_publish()
        assert result.gmail_draft_id == "draft1"
        assert result.google_doc_id == "doc1"
        mock_doc.assert_called_once()
        mock_draft.assert_called_once()
