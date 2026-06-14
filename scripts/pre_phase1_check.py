#!/usr/bin/env python3
"""Pre-Phase 1 readiness check — run before starting ingestion implementation."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "phases" / "phase-1" / "pre_phase1_report.json"
VALIDATION_JSON = ROOT / "phases" / "phase-0" / "storage_validation.json"

REQUIRED = [
    "config/product.yaml",
    "config/themes.yaml",
    "Docs/review-export-formats.md",
    "data/raw/groww_play_store_reviews.csv",
    "src/ingest/__init__.py",
    "tests/fixtures/reviews/play_store_sample.csv",
    "tests/fixtures/reviews/app_store_sample.csv",
]


def run_validate(weeks: int = 12) -> dict:
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_raw_exports.py"), "--weeks", str(weeks)],
        cwd=ROOT,
        check=False,
    )
    if VALIDATION_JSON.exists():
        return json.loads(VALIDATION_JSON.read_text(encoding="utf-8"))
    return {"valid": False, "issues": ["storage_validation.json not found"]}


def mcp_configured() -> bool:
    for path in (Path.home() / ".cursor" / "mcp.json", ROOT / ".cursor" / "mcp.json"):
        if path.exists() and "google-docs-mcp" in path.read_text(encoding="utf-8"):
            return True
    return False


def main() -> int:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    validation = run_validate()
    play_span = validation.get("play_store", {}).get("span_weeks") or 0
    app_span = validation.get("app_store", {}).get("span_weeks") or 0
    play_ok = play_span >= 8
    app_ok = app_span >= 8

    blockers: list[str] = []
    warnings: list[str] = []

    if missing:
        blockers.append(f"Missing required paths: {', '.join(missing)}")
    if not play_ok:
        blockers.append(
            f"Play Store raw export spans {play_span} weeks (<8). "
            "Re-fetch or download official Play Console export."
        )
    if not app_ok:
        warnings.append(
            "App Store raw export spans <8 weeks — replace groww_app_store_reviews.csv "
            "with a 12-week App Store Connect export before Phase 1 sign-off. "
            "See data/raw/APP_STORE_EXPORT_NEEDED.md"
        )
    if not mcp_configured():
        warnings.append("MCP not configured — OK for Phase 1; required before Phase 4")

    cfg_text = (ROOT / "config" / "product.yaml").read_text(encoding="utf-8")
    if 'draft_recipient: ""' in cfg_text and "DRAFT_RECIPIENT" not in cfg_text:
        warnings.append("Set publish.draft_recipient before Phase 5 (or DRAFT_RECIPIENT env)")

    ready_impl = len(blockers) == 0
    ready_signoff = ready_impl and app_ok

    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "ready_for_phase_1_implementation": ready_impl,
        "ready_for_phase_1_signoff": ready_signoff,
        "blockers": blockers,
        "warnings": warnings,
        "raw_validation": validation,
        "mcp_configured": mcp_configured(),
    }

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\nReport -> {REPORT}")

    if blockers:
        print("\nBLOCKED — fix blockers before Phase 1.", file=sys.stderr)
        return 1
    print("\nReady to implement Phase 1." + (" (see warnings)" if warnings else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
