"""Resolve phase deliverable paths from config/product.yaml."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def _product_config() -> dict:
    return yaml.safe_load((ROOT / "config" / "product.yaml").read_text(encoding="utf-8"))


def phase_dir(phase: int) -> Path:
    key = f"phase_{phase}"
    deliverables = _product_config().get("deliverables", {})
    entry = deliverables.get(key, {})
    return ROOT / entry.get("dir", f"phases/phase-{phase}")


def deliverable(phase: int, name: str) -> Path:
    key = f"phase_{phase}"
    deliverables = _product_config().get("deliverables", {})
    entry = deliverables.get(key, {})
    if name in entry:
        return ROOT / entry[name]
    return phase_dir(phase) / name


def raw_exports_dir() -> Path:
    paths = _product_config().get("paths", {})
    return ROOT / paths.get("raw_exports", "data/raw")
