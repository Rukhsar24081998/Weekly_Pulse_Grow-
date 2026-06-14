#!/usr/bin/env python3
"""Generate Phase 6 sign-off report (validation & hardening)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _grep_clean() -> bool:
    blocked = ("googleapiclient", "google.oauth2", "googleapis.com")
    for path in (ROOT / "src").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if any(token in text for token in blocked):
            return False
    return True


def _pytest_pass() -> tuple[bool, str]:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
            "-q",
            "--ignore=tests/test_phase6_signoff.py",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    summary = (result.stdout or result.stderr).strip().splitlines()[-1] if result.stdout or result.stderr else ""
    return result.returncode == 0, summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Phase 6 signoff_report.json")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "phases" / "phase-6" / "signoff_report.json",
    )
    args = parser.parse_args()

    tests_ok, test_summary = _pytest_pass()
    google_clean = _grep_clean()

    checks = {
        "P6-T-07_phase1_tests": tests_ok,
        "P6-T-08_phase2_tests": tests_ok,
        "P6-T-09_phase3_tests": tests_ok,
        "P6-T-10_no_google_sdk": google_clean,
        "P6-T-11_golden_pulse_schema": tests_ok,
        "pytest_summary": test_summary,
    }
    automated_pass = tests_ok and google_clean

    payload = {
        "phase": 6,
        "product": "Groww App",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "automated_checks_pass": automated_pass,
        "checks": checks,
        "github_actions": {
            "ci_workflow": ".github/workflows/ci.yml",
            "weekly_workflow": ".github/workflows/weekly-pulse.yml",
            "schedule": "Monday 09:00 IST (cron 30 3 * * 1 UTC)",
        },
        "known_limitations": [
            "App Store RSS capped at ~500 reviews per country (~1-2 weeks)",
            "Groq free tier may rate-limit; weekly Action uses --no-groq by default",
            "Gmail draft is never auto-sent",
            "MCP OAuth lives on Railway server, not in repo",
        ],
        "manual_signoff_pending": [
            "P6-T-06 teammate reproducibility test",
            "P6-T-12 fresh clone runbook verification",
        ],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Sign-off report -> {args.output}")
    print(f"Automated checks: {'PASSED' if automated_pass else 'FAILED'}")
    return 0 if automated_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
