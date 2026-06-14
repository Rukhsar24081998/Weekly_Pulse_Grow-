"""Preflight checks before MCP publish."""

from __future__ import annotations

from pathlib import Path

from src.guardrails.validate import validate_pulse
from src.publish.exceptions import PublishValidationError
from src.publish.pulse_loader import load_pulse_json, load_pulse_markdown
from src.pulse.models import PulseDocument


def run_preflight(
    pulse_json_path: Path,
    pulse_md_path: Path,
    *,
    max_words: int = 250,
    theme_count: int = 3,
    quote_count: int = 3,
    action_count: int = 3,
    require_prior_validation: bool = True,
) -> PulseDocument:
    pulse = load_pulse_json(pulse_json_path)
    markdown = load_pulse_markdown(pulse_md_path)
    pulse.markdown = markdown

    if require_prior_validation and not pulse.validation_passed:
        raise PublishValidationError(
            pulse.validation_errors or ["pulse.json validation_passed is false"]
        )

    result = validate_pulse(
        pulse,
        max_words=max_words,
        theme_count=theme_count,
        quote_count=quote_count,
        action_count=action_count,
    )
    if not result.passed:
        raise PublishValidationError(result.errors)

    pulse.validation_passed = True
    pulse.validation_errors = []
    return pulse
