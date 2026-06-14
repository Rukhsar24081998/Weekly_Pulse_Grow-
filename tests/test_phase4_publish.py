"""Phase 4 Google Doc publish tests."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.publish.config_loader import PublishConfig
from src.publish.exceptions import PublishValidationError
from src.publish.mcp_client import McpHttpClient, google_doc_url
from src.publish.pipeline import build_doc_content, build_doc_title, run_doc_publish
from src.publish.preflight import run_preflight
from src.pulse.models import PulseAction, PulseDocument, PulseQuote, PulseTheme


def _sample_pulse() -> PulseDocument:
    return PulseDocument(
        product="Groww App",
        week_ending="2026-06-13",
        review_window_weeks=12,
        window_start="2026-03-21",
        window_end="2026-06-13",
        total_reviews=1998,
        sample_size=1000,
        top_themes=[
            PulseTheme(1, "performance", "Performance", "Bugs reported.", 100, 2.5),
            PulseTheme(2, "discovery", "Discovery", "Search issues.", 80, 3.0),
            PulseTheme(3, "statements", "Statements", "Report problems.", 60, 2.1),
        ],
        quotes=[
            PulseQuote("performance", "App crashes often during login flow.", 1, "play_store"),
            PulseQuote("discovery", "Hard to find mutual fund options quickly.", 2, "play_store"),
            PulseQuote("statements", "Tax statement download fails every month.", 1, "play_store"),
        ],
        action_ideas=[
            PulseAction("performance", "Fix crash on login", "High crash volume"),
            PulseAction("discovery", "Improve fund search", "Search complaints"),
            PulseAction("statements", "Add statement status tracker", "Negative reports"),
        ],
        word_count=120,
        markdown="# Groww App — Weekly Pulse\n\nSample body.",
        validation_passed=True,
        validation_errors=[],
    )


def _write_pulse_artifacts(tmp: Path, pulse: PulseDocument) -> tuple[Path, Path]:
    md_path = tmp / "pulse.md"
    json_path = tmp / "pulse.json"
    md_path.write_text(pulse.markdown, encoding="utf-8")
    json_path.write_text(json.dumps(pulse.to_dict(), indent=2), encoding="utf-8")
    return md_path, json_path


class TestPreflight:
    def test_valid_pulse_passes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            md_path, json_path = _write_pulse_artifacts(Path(tmpdir), _sample_pulse())
            pulse = run_preflight(json_path, md_path)
            assert pulse.validation_passed

    def test_invalid_pulse_blocked(self):
        pulse = _sample_pulse()
        pulse.validation_passed = False
        with tempfile.TemporaryDirectory() as tmpdir:
            md_path, json_path = _write_pulse_artifacts(Path(tmpdir), pulse)
            with pytest.raises(PublishValidationError):
                run_preflight(json_path, md_path)


class TestPublishPipeline:
    def test_build_doc_title(self):
        config = PublishConfig(
            display_name="Groww App",
            mcp_server_url="https://example.test",
            doc_title_template="{display_name} Weekly Pulse — {date}",
            email_subject_template="Weekly App Review Pulse — {display_name} — {date}",
            pulse_md_input=Path("pulse.md"),
            pulse_json_input=Path("pulse.json"),
            doc_metadata_output=Path("doc_metadata.json"),
            run_metadata_output=Path("run.json"),
            google_doc_id=None,
            draft_recipient="operator@example.com",
        )
        title = build_doc_title(config, _sample_pulse())
        assert title == "Groww App Weekly Pulse — 2026-06-13"

    def test_build_doc_content_includes_title(self):
        content = build_doc_content("Groww App Weekly Pulse — 2026-06-13", _sample_pulse())
        assert content.startswith("# Groww App Weekly Pulse — 2026-06-13")
        assert "Sample body." in content

    @patch.object(McpHttpClient, "list_tools")
    @patch.object(McpHttpClient, "append_to_doc")
    def test_publish_with_append_to_doc(self, mock_append, mock_tools):
        mock_tools.return_value = [{"name": "append_to_doc"}]
        mock_append.return_value = {
            "status": "success",
            "document_id": "abc123",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            pulse = _sample_pulse()
            md_path, json_path = _write_pulse_artifacts(tmp, pulse)
            metadata_path = tmp / "doc_metadata.json"
            config = PublishConfig(
                display_name="Groww App",
                mcp_server_url="https://example.test",
                doc_title_template="{display_name} Weekly Pulse — {date}",
                email_subject_template="Weekly App Review Pulse — {display_name} — {date}",
                pulse_md_input=md_path,
                pulse_json_input=json_path,
                doc_metadata_output=metadata_path,
                run_metadata_output=tmp / "run.json",
                google_doc_id="abc123",
                draft_recipient="operator@example.com",
            )

            result = run_doc_publish(config=config)
            assert result.google_doc_id == "abc123"
            assert result.mcp_tool == "append_to_doc"
            assert metadata_path.exists()
            payload = json.loads(metadata_path.read_text(encoding="utf-8"))
            assert payload["google_doc_id"] == "abc123"
            mock_append.assert_called_once()

    @patch.object(McpHttpClient, "list_tools")
    @patch.object(McpHttpClient, "create_document")
    def test_publish_with_create_document(self, mock_create, mock_tools):
        mock_tools.return_value = [
            {"name": "create_document"},
            {"name": "append_to_doc"},
        ]
        mock_create.return_value = {
            "status": "success",
            "document_id": "newdoc456",
            "document_url": "https://docs.google.com/document/d/newdoc456/edit",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            pulse = _sample_pulse()
            md_path, json_path = _write_pulse_artifacts(tmp, pulse)
            metadata_path = tmp / "doc_metadata.json"
            config = PublishConfig(
                display_name="Groww App",
                mcp_server_url="https://example.test",
                doc_title_template="{display_name} Weekly Pulse — {date}",
                email_subject_template="Weekly App Review Pulse — {display_name} — {date}",
                pulse_md_input=md_path,
                pulse_json_input=json_path,
                doc_metadata_output=metadata_path,
                run_metadata_output=tmp / "run.json",
                google_doc_id=None,
                draft_recipient="operator@example.com",
            )

            result = run_doc_publish(config=config)
            assert result.google_doc_id == "newdoc456"
            assert result.mcp_tool == "create_document"
            mock_create.assert_called_once()

    def test_dry_run_writes_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            pulse = _sample_pulse()
            md_path, json_path = _write_pulse_artifacts(tmp, pulse)
            metadata_path = tmp / "doc_metadata.json"
            config = PublishConfig(
                display_name="Groww App",
                mcp_server_url="https://example.test",
                doc_title_template="{display_name} Weekly Pulse — {date}",
                email_subject_template="Weekly App Review Pulse — {display_name} — {date}",
                pulse_md_input=md_path,
                pulse_json_input=json_path,
                doc_metadata_output=metadata_path,
                run_metadata_output=tmp / "run.json",
                google_doc_id=None,
                draft_recipient="operator@example.com",
            )

            result = run_doc_publish(config=config, dry_run=True)
            assert result.mcp_tool == "dry_run"
            assert metadata_path.exists()


class TestMcpClient:
    def test_google_doc_url(self):
        assert google_doc_url("abc123") == "https://docs.google.com/document/d/abc123/edit"

    @patch("urllib.request.urlopen")
    def test_list_tools(self, mock_urlopen):
        response = MagicMock()
        response.read.return_value = b'[{"name":"append_to_doc"}]'
        response.__enter__.return_value = response
        mock_urlopen.return_value = response

        client = McpHttpClient("https://example.test")
        tools = client.list_tools()
        assert tools[0]["name"] == "append_to_doc"


class TestNoGoogleSdkInSrc:
    def test_no_google_sdk_imports(self):
        blocked = ("googleapiclient", "google.oauth2", "googleapis.com")
        for path in Path("src").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in blocked:
                assert token not in text, f"{token} found in {path}"
