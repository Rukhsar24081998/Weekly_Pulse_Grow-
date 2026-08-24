#!/usr/bin/env python3
"""Write a small public JSON snapshot for the Vercel dashboard.

Render free instances lose synced files after spin-down. The frontend reads
these committed files from /data/*.json so the site stays populated.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PULSE_JSON = ROOT / "phases" / "phase-3" / "pulse.json"
REVIEWS_JSON = ROOT / "phases" / "phase-1" / "reviews.json"
OUT_DIR = ROOT / "frontend" / "public" / "data"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_pulse_latest(pulse: dict) -> dict:
    return {
        "pulse": pulse,
        "markdown": pulse.get("markdown", ""),
        "paths": {
            "json": "phases/phase-3/pulse.json",
            "markdown": "phases/phase-3/pulse.md",
        },
        "validation": {
            "passed": bool(pulse.get("validation_passed", False)),
            "errors": list(pulse.get("validation_errors", [])),
        },
    }


def build_status(pulse: dict) -> dict:
    reviews: dict = {"total": pulse.get("total_reviews")}
    if REVIEWS_JSON.exists():
        payload = _load(REVIEWS_JSON)
        stats = payload.get("stats", {})
        if stats.get("total") == pulse.get("total_reviews"):
            reviews = {
                "total": stats.get("total"),
                "app_store": stats.get("app_store"),
                "play_store": stats.get("play_store"),
                "window": payload.get("window"),
            }

    return {
        "product": pulse.get("product", "Groww App"),
        "artifacts": {
            "reviews": REVIEWS_JSON.exists(),
            "themes": (ROOT / "phases" / "phase-2" / "themes.json").exists(),
            "pulse_json": True,
            "pulse_md": (ROOT / "phases" / "phase-3" / "pulse.md").exists(),
            "doc_metadata": False,
            "run_metadata": False,
            "signoff": (ROOT / "phases" / "phase-6" / "signoff_report.json").exists(),
        },
        "phases_dir": "phases/phase-3",
        "reviews": reviews,
        "pulse_summary": {
            "week_ending": pulse.get("week_ending"),
            "word_count": pulse.get("word_count"),
            "validation_passed": pulse.get("validation_passed"),
        },
    }


def main() -> int:
    if not PULSE_JSON.exists():
        print(f"Missing {PULSE_JSON} — run python -m src.pulse.run first", file=sys.stderr)
        return 1

    pulse = _load(PULSE_JSON)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "pulse-latest.json").write_text(
        json.dumps(build_pulse_latest(pulse), indent=2) + "\n",
        encoding="utf-8",
    )
    (OUT_DIR / "status.json").write_text(
        json.dumps(build_status(pulse), indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote dashboard snapshot -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
