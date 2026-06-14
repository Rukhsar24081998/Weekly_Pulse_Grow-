"""Write synced pipeline artifacts to phase deliverable paths."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.paths import deliverable


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def save_sync_bundle(payload: dict[str, Any]) -> dict[str, str]:
    """Persist a bundle pushed from GitHub Actions or a local sync script."""
    written: dict[str, str] = {}

    if "reviews" in payload:
        path = deliverable(1, "reviews")
        _write_json(path, payload["reviews"])
        written["reviews"] = str(path)

    if "themes" in payload:
        path = deliverable(2, "themes")
        _write_json(path, payload["themes"])
        written["themes"] = str(path)

    if "pulse_json" in payload:
        path = deliverable(3, "pulse_json")
        _write_json(path, payload["pulse_json"])
        written["pulse_json"] = str(path)

    if "pulse_md" in payload:
        path = deliverable(3, "pulse_md")
        _write_text(path, str(payload["pulse_md"]))
        written["pulse_md"] = str(path)

    if "doc_metadata" in payload:
        path = deliverable(4, "doc_metadata")
        _write_json(path, payload["doc_metadata"])
        written["doc_metadata"] = str(path)

    if "run_metadata" in payload:
        path = deliverable(5, "run_metadata")
        _write_json(path, payload["run_metadata"])
        written["run_metadata"] = str(path)

    if "pulse_json" not in payload:
        raise ValueError("pulse_json is required in sync payload")

    return written
