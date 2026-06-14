"""Tests for public API artifact sync."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from src.api.app import create_app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("SYNC_SECRET", "test-sync-secret")
    return TestClient(create_app())


def _sample_bundle() -> dict:
    return {
        "pulse_json": {
            "product": "Groww App",
            "week_ending": "2026-06-14",
            "review_window_weeks": 12,
            "window_start": "2026-03-22",
            "window_end": "2026-06-14",
            "total_reviews": 100,
            "sample_size": 100,
            "top_themes": [],
            "quotes": [],
            "action_ideas": [],
            "word_count": 50,
            "markdown": "# Pulse",
            "validation_passed": True,
            "validation_errors": [],
        },
        "pulse_md": "# Pulse\n",
        "reviews": {"stats": {"total": 100, "app_store": 10, "play_store": 90}},
    }


class TestSyncArtifacts:
    def test_sync_requires_auth(self, client):
        response = client.post("/api/sync/artifacts", json=_sample_bundle())
        assert response.status_code == 401

    def test_sync_writes_artifacts(self, client, tmp_path, monkeypatch):
        def fake_deliverable(phase: int, name: str):
            mapping = {
                (1, "reviews"): tmp_path / "reviews.json",
                (2, "themes"): tmp_path / "themes.json",
                (3, "pulse_json"): tmp_path / "pulse.json",
                (3, "pulse_md"): tmp_path / "pulse.md",
                (4, "doc_metadata"): tmp_path / "doc.json",
                (5, "run_metadata"): tmp_path / "run.json",
            }
            return mapping.get((phase, name), tmp_path / f"{phase}-{name}")

        with patch("src.api.services.storage.deliverable", side_effect=fake_deliverable):
            response = client.post(
                "/api/sync/artifacts",
                headers={"Authorization": "Bearer test-sync-secret"},
                json=_sample_bundle(),
            )

        assert response.status_code == 200
        assert json.loads((tmp_path / "pulse.json").read_text(encoding="utf-8"))["week_ending"] == "2026-06-14"
