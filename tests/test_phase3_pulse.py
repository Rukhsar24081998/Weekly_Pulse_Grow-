"""Phase 3 pulse generation and guardrail tests."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from src.guardrails.redact import redact_text, scan_pii_violations
from src.guardrails.validate import count_words, validate_pulse
from src.pulse.config_loader import PulseConfig
from src.pulse.exceptions import PulseValidationError
from src.pulse.generator import generate_pulse
from src.pulse.loader import load_reviews_index, load_themes_json
from src.pulse.pipeline import run_pulse_generation

FIXTURES = Path(__file__).resolve().parent / "fixtures"
THEMES_FIXTURE = FIXTURES / "pulse" / "sample_themes.json"
REVIEWS_FIXTURE = FIXTURES / "themes" / "sample_reviews.json"


def _test_config(tmp: Path) -> PulseConfig:
    return PulseConfig(
        product_name="Groww",
        display_name="Groww App",
        themes_input=THEMES_FIXTURE,
        reviews_input=REVIEWS_FIXTURE,
        pulse_md_output=tmp / "pulse.md",
        pulse_json_output=tmp / "pulse.json",
        max_words=250,
        theme_count=3,
        quote_count=3,
        action_count=3,
        max_quote_words=22,
    )


class TestPIIRedactor:
    def test_email_redaction(self):
        assert "[email redacted]" in redact_text("contact me at user@example.com please")

    def test_phone_redaction(self):
        assert "[phone redacted]" in redact_text("call 9876543210 for help")

    def test_pan_redaction(self):
        assert "[id redacted]" in redact_text("PAN ABCDE1234F submitted")

    def test_handle_redaction(self):
        result = redact_text("@username said the app is slow")
        assert "@username" not in result
        assert "[handle redacted]" in result


class TestValidator:
    def _build_pulse(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = _test_config(Path(tmp))
            themes = load_themes_json(THEMES_FIXTURE)
            reviews = load_reviews_index(REVIEWS_FIXTURE)
            return generate_pulse(themes, reviews, config)

    def test_valid_pulse_passes(self):
        pulse = self._build_pulse()
        result = validate_pulse(pulse)
        assert result.passed
        assert pulse.word_count <= 250

    def test_block_over_word_limit(self):
        pulse = self._build_pulse()
        pulse.markdown = "word " * 260
        pulse.word_count = count_words(pulse.markdown)
        result = validate_pulse(pulse)
        assert not result.passed
        assert any("word count" in err for err in result.errors)

    def test_block_missing_quotes(self):
        pulse = self._build_pulse()
        pulse.quotes = pulse.quotes[:2]
        result = validate_pulse(pulse)
        assert not result.passed
        assert any("quotes" in err for err in result.errors)

    def test_block_pii_in_output(self):
        pulse = self._build_pulse()
        pulse.markdown += "\nEmail me at leak@example.com"
        result = validate_pulse(pulse)
        assert not result.passed
        assert any("PII" in err for err in result.errors)


class TestPulseGenerator:
    def test_pulse_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = _test_config(Path(tmp))
            themes = load_themes_json(THEMES_FIXTURE)
            reviews = load_reviews_index(REVIEWS_FIXTURE)
            pulse = generate_pulse(themes, reviews, config)

            assert len(pulse.top_themes) == 3
            assert len(pulse.quotes) == 3
            assert len(pulse.action_ideas) == 3
            assert "## Top themes" in pulse.markdown
            assert "## User quotes" in pulse.markdown
            assert "## Recommended actions" in pulse.markdown
            assert "Play Store" in pulse.markdown or "App Store" in pulse.markdown

    def test_word_count_under_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = _test_config(Path(tmp))
            themes = load_themes_json(THEMES_FIXTURE)
            reviews = load_reviews_index(REVIEWS_FIXTURE)
            pulse = generate_pulse(themes, reviews, config)
            assert pulse.word_count <= 250

    def test_pii_redacted_in_quotes(self):
        themes = load_themes_json(THEMES_FIXTURE)
        reviews = load_reviews_index(REVIEWS_FIXTURE)
        reviews["rev-login-001"].text = "OTP not received, email me at a@b.com please"
        with tempfile.TemporaryDirectory() as tmp:
            pulse = generate_pulse(themes, reviews, _test_config(Path(tmp)))
            assert not scan_pii_violations(pulse.markdown)


class TestPipeline:
    def test_cli_writes_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = run_pulse_generation(
                config=_test_config(tmp_path),
                themes_path=THEMES_FIXTURE,
                reviews_path=REVIEWS_FIXTURE,
                output_md=tmp_path / "pulse.md",
                output_json=tmp_path / "pulse.json",
            )
            assert Path(result.output_md).exists()
            assert Path(result.output_json).exists()
            payload = json.loads((tmp_path / "pulse.json").read_text())
            assert payload["validation_passed"] is True
            assert len(payload["top_themes"]) == 3
            assert len(payload["quotes"]) == 3
            assert payload["word_count"] <= 250

    def test_strict_mode_raises_on_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            broken_themes = tmp_path / "broken_themes.json"
            payload = json.loads(THEMES_FIXTURE.read_text())
            payload["top_pulse_themes"] = payload["top_pulse_themes"][:2]
            broken_themes.write_text(json.dumps(payload), encoding="utf-8")

            config = _test_config(tmp_path)
            with pytest.raises((PulseValidationError, ValueError)):
                run_pulse_generation(
                    config=config,
                    themes_path=broken_themes,
                    reviews_path=REVIEWS_FIXTURE,
                    output_md=tmp_path / "pulse.md",
                    output_json=tmp_path / "pulse.json",
                    strict=True,
                )
