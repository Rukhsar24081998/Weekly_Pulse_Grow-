"""Load phase deliverables for API responses."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.guardrails.validate import validate_pulse
from src.paths import ROOT, deliverable, phase_dir
from src.publish.pulse_loader import load_pulse_json, load_pulse_markdown
from src.pulse.config_loader import load_pulse_config


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8"))


def artifact_availability() -> dict[str, bool]:
    checks = {
        "reviews": deliverable(1, "reviews").exists(),
        "themes": deliverable(2, "themes").exists(),
        "pulse_json": deliverable(3, "pulse_json").exists(),
        "pulse_md": deliverable(3, "pulse_md").exists(),
        "doc_metadata": deliverable(4, "doc_metadata").exists(),
        "run_metadata": deliverable(5, "run_metadata").exists(),
        "signoff": deliverable(6, "signoff").exists(),
    }
    return checks


def _relative_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_latest_pulse() -> dict[str, Any]:
    json_path = deliverable(3, "pulse_json")
    md_path = deliverable(3, "pulse_md")
    if not json_path.exists():
        raise FileNotFoundError(
            f"No pulse found at {json_path}. Run: python -m src.pulse.run"
        )

    pulse = load_pulse_json(json_path)
    markdown = load_pulse_markdown(md_path) if md_path.exists() else pulse.markdown
    validation = validate_pulse(pulse)

    return {
        "pulse": pulse.to_dict(),
        "markdown": markdown,
        "paths": {
            "json": _relative_path(json_path),
            "markdown": _relative_path(md_path) if md_path.exists() else None,
        },
        "validation": {
            "passed": validation.passed,
            "errors": validation.errors,
        },
    }


def load_latest_themes() -> dict[str, Any]:
    path = deliverable(2, "themes")
    if not path.exists():
        raise FileNotFoundError(
            f"No themes found at {path}. Run: python -m src.themes.run"
        )
    payload = _read_json(path)
    return {
        "themes": payload,
        "path": _relative_path(path),
    }


def load_pipeline_status() -> dict[str, Any]:
    config = load_pulse_config()
    status: dict[str, Any] = {
        "product": config.display_name,
        "artifacts": artifact_availability(),
        "phases_dir": str(phase_dir(3).relative_to(ROOT)),
    }

    reviews_path = deliverable(1, "reviews")
    if reviews_path.exists():
        reviews = _read_json(reviews_path)
        stats = reviews.get("stats", {})
        status["reviews"] = {
            "total": stats.get("total"),
            "app_store": stats.get("app_store"),
            "play_store": stats.get("play_store"),
            "window": reviews.get("window"),
        }

    run_path = deliverable(5, "run_metadata")
    if run_path.exists():
        status["last_publish"] = _read_json(run_path)

    doc_path = deliverable(4, "doc_metadata")
    if doc_path.exists():
        status["doc"] = _read_json(doc_path)

    pulse_path = deliverable(3, "pulse_json")
    if pulse_path.exists():
        pulse = _read_json(pulse_path)
        status["pulse_summary"] = {
            "week_ending": pulse.get("week_ending"),
            "word_count": pulse.get("word_count"),
            "validation_passed": pulse.get("validation_passed"),
        }

    return status
