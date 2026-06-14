"""Pulse constraint validation."""

from __future__ import annotations

from dataclasses import dataclass

from src.guardrails.redact import scan_pii_violations
from src.pulse.models import PulseDocument


@dataclass
class ValidationResult:
    passed: bool
    errors: list[str]


def count_words(text: str) -> int:
    return len(text.split())


def validate_pulse(
    pulse: PulseDocument,
    *,
    max_words: int = 250,
    theme_count: int = 3,
    quote_count: int = 3,
    action_count: int = 3,
) -> ValidationResult:
    errors: list[str] = []

    if len(pulse.top_themes) != theme_count:
        errors.append(f"expected {theme_count} themes, got {len(pulse.top_themes)}")
    if len(pulse.quotes) != quote_count:
        errors.append(f"expected {quote_count} quotes, got {len(pulse.quotes)}")
    if len(pulse.action_ideas) != action_count:
        errors.append(f"expected {action_count} actions, got {len(pulse.action_ideas)}")

    word_count = count_words(pulse.markdown)
    if word_count > max_words:
        errors.append(f"word count {word_count} exceeds limit of {max_words}")

    pii_errors = scan_pii_violations(pulse.markdown)
    for issue in pii_errors:
        errors.append(f"PII: {issue}")

    for quote in pulse.quotes:
        for issue in scan_pii_violations(quote.text):
            errors.append(f"PII in quote ({quote.theme_id}): {issue}")

    return ValidationResult(passed=not errors, errors=errors)
