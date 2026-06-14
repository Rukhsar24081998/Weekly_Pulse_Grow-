"""Phase 6 validation, golden pulse schema, and sign-off checks."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

import pytest

from src.guardrails.redact import scan_pii_violations
from src.guardrails.validate import validate_pulse
from src.pulse.config_loader import PulseConfig
from src.pulse.generator import generate_pulse
from src.pulse.loader import load_reviews_index, load_themes_json

FIXTURES = Path(__file__).resolve().parent / "fixtures"
SCHEMA_PATH = FIXTURES / "expected-pulse-schema.json"
THEMES_FIXTURE = FIXTURES / "pulse" / "sample_themes.json"
REVIEWS_FIXTURE = FIXTURES / "themes" / "sample_reviews.json"


def _load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _generate_fixture_pulse():
    config = PulseConfig(
        product_name="Groww",
        display_name="Groww App",
        themes_input=THEMES_FIXTURE,
        reviews_input=REVIEWS_FIXTURE,
        pulse_md_output=Path("pulse.md"),
        pulse_json_output=Path("pulse.json"),
        max_words=250,
        theme_count=3,
        quote_count=3,
        action_count=3,
        max_quote_words=22,
    )
    themes = load_themes_json(THEMES_FIXTURE)
    reviews = load_reviews_index(REVIEWS_FIXTURE)
    return generate_pulse(themes, reviews, config)


class TestGoldenPulseSchema:
    def test_fixture_pulse_matches_schema(self):
        schema = _load_schema()
        pulse = _generate_fixture_pulse()
        payload = pulse.to_dict()

        for key in schema["required_top_level_keys"]:
            assert key in payload, f"missing top-level key: {key}"

        assert len(pulse.top_themes) == schema["theme_count"]
        assert len(pulse.quotes) == schema["quote_count"]
        assert len(pulse.action_ideas) == schema["action_count"]
        assert pulse.word_count <= schema["max_words"]

        for theme in pulse.top_themes:
            theme_dict = theme.to_dict()
            for key in schema["required_theme_keys"]:
                assert key in theme_dict

        for quote in pulse.quotes:
            quote_dict = quote.to_dict()
            for key in schema["required_quote_keys"]:
                assert key in quote_dict

        for action in pulse.action_ideas:
            action_dict = action.to_dict()
            for key in schema["required_action_keys"]:
                assert key in action_dict

    def test_fixture_pulse_passes_validation_and_pii_scan(self):
        pulse = _generate_fixture_pulse()
        result = validate_pulse(pulse)
        assert result.passed
        assert not scan_pii_violations(pulse.markdown)


class TestProblemStatementConstraints:
    def test_theme_cap_in_config(self):
        from src.paths import ROOT
        import yaml

        data = yaml.safe_load((ROOT / "config" / "product.yaml").read_text(encoding="utf-8"))
        assert int(data["theme_clustering"]["max_themes"]) <= 5
        assert int(data["pulse"]["max_words"]) <= 250


class TestNoGoogleSdkInSrc:
    def test_no_google_sdk_imports(self):
        blocked = ("googleapiclient", "google.oauth2", "googleapis.com")
        for path in Path("src").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for token in blocked:
                assert token not in text, f"{token} found in {path}"


class TestPhase6SignoffScript:
    def test_signoff_script_runs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "signoff_report.json"
            result = subprocess.run(
                ["python", "scripts/phase6_signoff.py", "--output", str(out)],
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0, result.stderr or result.stdout
            payload = json.loads(out.read_text(encoding="utf-8"))
            assert payload["phase"] == 6
            assert payload["automated_checks_pass"] is True
