"""Pulse generation orchestration."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from src.guardrails.validate import validate_pulse
from src.pulse.config_loader import PulseConfig, load_pulse_config
from src.pulse.exceptions import PulseValidationError
from src.pulse.generator import generate_pulse
from src.pulse.loader import load_reviews_index, load_themes_json
from src.pulse.models import PulsePipelineResult


def run_pulse_generation(
    *,
    config: PulseConfig | None = None,
    themes_path: Path | None = None,
    reviews_path: Path | None = None,
    output_md: Path | None = None,
    output_json: Path | None = None,
    strict: bool = True,
) -> PulsePipelineResult:
    cfg = config or load_pulse_config()
    themes_file = themes_path or cfg.themes_input
    reviews_file = reviews_path or cfg.reviews_input
    md_path = output_md or cfg.pulse_md_output
    json_path = output_json or cfg.pulse_json_output

    themes_payload = load_themes_json(themes_file)
    reviews_index = load_reviews_index(reviews_file)

    pulse = generate_pulse(themes_payload, reviews_index, cfg)
    validation = validate_pulse(
        pulse,
        max_words=cfg.max_words,
        theme_count=cfg.theme_count,
        quote_count=cfg.quote_count,
        action_count=cfg.action_count,
    )

    pulse.validation_passed = validation.passed
    pulse.validation_errors = validation.errors

    if strict and not validation.passed:
        raise PulseValidationError(validation.errors)

    payload = pulse.to_dict()
    payload["generated_at"] = datetime.now(timezone.utc).isoformat()
    payload["source"] = {
        "themes_path": str(themes_file),
        "reviews_path": str(reviews_file),
    }

    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(pulse.markdown, encoding="utf-8")
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return PulsePipelineResult(
        output_md=str(md_path),
        output_json=str(json_path),
        word_count=pulse.word_count,
        validation_passed=pulse.validation_passed,
        validation_errors=pulse.validation_errors,
    )
