#!/usr/bin/env python3
"""Run Phase 0 automated checks and write a summary report."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "phases" / "phase-0" / "phase0_report.json"

REQUIRED_DIRS = [
    "src",
    "src/ingest",
    "src/themes",
    "src/pulse",
    "src/guardrails",
    "data/raw",
    "phases/phase-0",
    "phases/phase-1",
    "tests",
    "tests/fixtures/reviews",
    "prompts",
    "config",
    "phases",
    "Docs/phases",
]

REQUIRED_FILES = [
    "README.md",
    "config/product.yaml",
    "config/themes.yaml",
    "Docs/review-export-formats.md",
    "Docs/decision.md",
    "Docs/architecture.md",
    ".cursor/mcp.json.example",
    "prompts/weekly-pulse-agent.md",
]


def check_path_exists(relative: str) -> bool:
    return (ROOT / relative).exists()


def grep_secrets() -> bool:
    try:
        result = subprocess.run(
            ["git", "grep", "-i", "client_secret"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode != 0
    except FileNotFoundError:
        # Not a git repo — scan tracked-like files manually
        for path in ROOT.rglob("*"):
            if path.is_file() and ".git" not in path.parts:
                if "client_secret" in path.read_text(errors="ignore").lower():
                    if "YOUR_CLIENT_SECRET" not in path.read_text(errors="ignore"):
                        return False
        return True


def themes_ok() -> tuple[bool, int]:
    text = (ROOT / "config" / "themes.yaml").read_text(encoding="utf-8")
    ids = re.findall(r"^\s*- id:\s*(\S+)", text, re.MULTILINE)
    return len(ids) >= 5, len(ids)


def product_ok() -> bool:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    decision = (ROOT / "Docs/decision.md").read_text(encoding="utf-8")
    return "Groww" in text and "ADR-002" in decision and "Groww App" in decision


def readme_constraints_ok() -> bool:
    text = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    needles = ["public", "5 themes", "250", "pii", "mcp"]
    return all(n in text for n in needles)


def reviews_present() -> dict:
    raw = ROOT / "data" / "raw"
    play = raw / "groww_play_store_reviews.csv"
    app = raw / "groww_app_store_reviews.csv"
    meta = raw / "fetch_metadata.json"
    result = {
        "play_store_csv": play.exists(),
        "app_store_csv": app.exists(),
        "metadata": meta.exists(),
    }
    if meta.exists():
        result["fetch_metadata"] = json.loads(meta.read_text(encoding="utf-8"))
    return result


def mcp_configured() -> bool:
    candidates = [
        Path.home() / ".cursor" / "mcp.json",
        ROOT / ".cursor" / "mcp.json",
    ]
    for path in candidates:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if "google-docs-mcp" in text or "a-bonus" in text:
            return True
    return False


def adrs_ok() -> bool:
    text = (ROOT / "Docs/decision.md").read_text(encoding="utf-8")
    for n in range(1, 9):
        if f"ADR-{n:03d}" not in text:
            return False
    return "accepted" in text


def main() -> int:
    theme_ok, theme_count = themes_ok()
    checks = {
        "P0-EC-01_product_locked": product_ok(),
        "P0-EC-02_export_docs": check_path_exists("Docs/review-export-formats.md"),
        "P0-EC-03_mcp_configured": mcp_configured(),
        "P0-EC-05_themes_yaml": theme_ok,
        "P0-EC-06_repo_scaffold": all(check_path_exists(p) for p in REQUIRED_DIRS)
        and all(check_path_exists(p) for p in REQUIRED_FILES),
        "P0-EC-07_decision_log": adrs_ok(),
        "P0-EC-08_readme_constraints": readme_constraints_ok(),
        "P0-T-08_scaffold_dirs": all(check_path_exists(p) for p in REQUIRED_DIRS),
        "P0-T-09_no_secrets": grep_secrets(),
        "P0-T-06_theme_count": theme_count,
        "reviews_fetched": reviews_present(),
    }

    # MCP OAuth must be manual
    checks["P0-EC-04_mcp_oauth_smoke"] = False
    checks["manual_required"] = []
    if not checks["P0-EC-03_mcp_configured"]:
        checks["manual_required"].append(
            "Configure @a-bonus/google-docs-mcp in ~/.cursor/mcp.json (see .cursor/mcp.json.example)"
        )
    checks["manual_required"].append(
        "Complete MCP OAuth smoke test in Cursor (P0-EC-04)"
    )

    automated_pass = all(
        checks[k]
        for k in checks
        if k.startswith(("P0-EC", "P0-T"))
        and k not in ("P0-EC-03_mcp_configured", "P0-EC-04_mcp_oauth_smoke")
    )
    reviews_ok = (
        checks["reviews_fetched"]["play_store_csv"]
        or checks["reviews_fetched"]["app_store_csv"]
    )

    report = {
        "phase": 0,
        "product": "Groww App",
        "run_at": datetime.now(timezone.utc).isoformat(),
        "automated_checks_pass": automated_pass and reviews_ok,
        "ready_for_phase_1": automated_pass
        and reviews_ok
        and checks["P0-EC-03_mcp_configured"],
        "checks": checks,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    print(f"\nReport written to {REPORT_PATH}")

    if not reviews_ok:
        print("\nRun: python scripts/fetch_public_reviews.py")
        return 1
    if not automated_pass:
        return 1
    if not checks["P0-EC-03_mcp_configured"]:
        print("\nPhase 0 scaffold + reviews OK. Configure MCP before Phase 4.")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
