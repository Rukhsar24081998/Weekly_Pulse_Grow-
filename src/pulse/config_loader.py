"""Load pulse generation configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from src.paths import ROOT, deliverable


@dataclass
class PulseConfig:
    product_name: str
    display_name: str
    themes_input: Path
    reviews_input: Path
    pulse_md_output: Path
    pulse_json_output: Path
    max_words: int
    theme_count: int
    quote_count: int
    action_count: int
    max_quote_words: int


def load_pulse_config(config_path: Path | None = None) -> PulseConfig:
    path = config_path or ROOT / "config" / "product.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    product = data["product"]
    pulse = data.get("pulse", {})

    return PulseConfig(
        product_name=product["name"],
        display_name=product["display_name"],
        themes_input=deliverable(2, "themes"),
        reviews_input=deliverable(1, "reviews"),
        pulse_md_output=deliverable(3, "pulse_md"),
        pulse_json_output=deliverable(3, "pulse_json"),
        max_words=int(pulse.get("max_words", 250)),
        theme_count=int(pulse.get("theme_count", 3)),
        quote_count=int(pulse.get("quote_count", 3)),
        action_count=int(pulse.get("action_count", 3)),
        max_quote_words=int(pulse.get("max_quote_words", 22)),
    )
