"""Phase 7 API tests — read-only artifact endpoints."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from src.api.app import create_app
from src.pulse.models import PulseAction, PulseDocument, PulseQuote, PulseTheme


def _sample_pulse_dict() -> dict:
    pulse = PulseDocument(
        product="Groww App",
        week_ending="2026-06-14",
        review_window_weeks=12,
        window_start="2026-03-22",
        window_end="2026-06-14",
        total_reviews=100,
        sample_size=100,
        top_themes=[
            PulseTheme(1, "performance", "Performance", "Bugs reported.", 50, 2.5),
            PulseTheme(2, "discovery", "Discovery", "Search issues.", 30, 3.0),
            PulseTheme(3, "statements", "Statements", "Report problems.", 20, 2.1),
        ],
        quotes=[
            PulseQuote("performance", "App is slow.", 2, "play_store"),
            PulseQuote("discovery", "Hard to find funds.", 2, "play_store"),
            PulseQuote("statements", "Statement download fails.", 1, "play_store"),
        ],
        action_ideas=[
            PulseAction("performance", "Fix crashes", "High volume"),
            PulseAction("discovery", "Improve search", "Search complaints"),
            PulseAction("statements", "Add statement tracker", "Negative reports"),
        ],
        word_count=80,
        markdown="# Groww App — Weekly Pulse\n\nBody",
        validation_passed=True,
    )
    return pulse.to_dict()


@pytest.fixture
def client():
    return TestClient(create_app())


class TestHealthRoutes:
    def test_health_ok(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "ok"
        assert payload["product"] == "Groww App"
        assert "artifacts" in payload

    def test_status_ok(self, client):
        response = client.get("/api/status")
        assert response.status_code == 200
        assert response.json()["product"] == "Groww App"


class TestPulseRoutes:
    def test_pulse_latest_404_when_missing(self, client):
        with patch(
            "src.api.services.artifacts.deliverable",
            return_value=Path("/nonexistent/pulse.json"),
        ):
            response = client.get("/api/pulse/latest")
        assert response.status_code == 404

    def test_pulse_latest_returns_payload(self, client, tmp_path: Path):
        json_path = tmp_path / "pulse.json"
        md_path = tmp_path / "pulse.md"
        json_path.write_text(json.dumps(_sample_pulse_dict()), encoding="utf-8")
        md_path.write_text("# Groww App — Weekly Pulse\n\nBody", encoding="utf-8")

        def fake_deliverable(phase: int, name: str) -> Path:
            if phase == 3 and name == "pulse_json":
                return json_path
            if phase == 3 and name == "pulse_md":
                return md_path
            return tmp_path / f"phase-{phase}-{name}"

        with patch("src.api.services.artifacts.deliverable", side_effect=fake_deliverable):
            response = client.get("/api/pulse/latest")

        assert response.status_code == 200
        payload = response.json()
        assert payload["pulse"]["week_ending"] == "2026-06-14"
        assert payload["validation"]["passed"] is True
        assert "Body" in payload["markdown"]

    def test_themes_latest_404_when_missing(self, client):
        with patch(
            "src.api.services.artifacts.deliverable",
            return_value=Path("/nonexistent/themes.json"),
        ):
            response = client.get("/api/themes/latest")
        assert response.status_code == 404
