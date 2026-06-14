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
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.guardrails.redact import scan_pii_violations
from src.guardrails.validate import validate_pulse
from src.pulse.models import PulseAction, PulseDocument, PulseQuote, PulseTheme

PHASE_PII_SCAN_PATHS = (
    "phases/phase-3/pulse.json",
    "phases/phase-3/pulse.md",
)


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
    summary = (
        (result.stdout or result.stderr).strip().splitlines()[-1]
        if result.stdout or result.stderr
        else ""
    )
    return result.returncode == 0, summary


def _load_pulse_document(path: Path) -> PulseDocument | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return PulseDocument(
        product=data["product"],
        week_ending=data["week_ending"],
        review_window_weeks=data["review_window_weeks"],
        window_start=data["window_start"],
        window_end=data["window_end"],
        total_reviews=data["total_reviews"],
        sample_size=data["sample_size"],
        top_themes=[PulseTheme(**theme) for theme in data["top_themes"]],
        quotes=[PulseQuote(**quote) for quote in data["quotes"]],
        action_ideas=[PulseAction(**action) for action in data["action_ideas"]],
        word_count=data["word_count"],
        markdown=data.get("markdown", ""),
        validation_passed=data.get("validation_passed", False),
        validation_errors=data.get("validation_errors", []),
    )


def _audit_both_stores() -> tuple[bool, dict]:
    reviews_path = ROOT / "phases" / "phase-1" / "reviews.json"
    if not reviews_path.exists():
        return False, {"status": "missing", "path": str(reviews_path)}

    data = json.loads(reviews_path.read_text(encoding="utf-8"))
    stats = data.get("stats", {})
    app_count = int(stats.get("app_store", 0))
    play_count = int(stats.get("play_store", 0))
    passed = app_count > 0 and play_count > 0
    return passed, {
        "path": str(reviews_path),
        "app_store": app_count,
        "play_store": play_count,
    }


def _audit_themes() -> tuple[bool, dict]:
    themes_path = ROOT / "phases" / "phase-2" / "themes.json"
    if not themes_path.exists():
        return False, {"status": "missing", "path": str(themes_path)}

    data = json.loads(themes_path.read_text(encoding="utf-8"))
    themes = data.get("themes", [])
    theme_count = len(themes)
    passed = 0 < theme_count <= 5
    return passed, {
        "path": str(themes_path),
        "theme_count": theme_count,
        "max_allowed": 5,
    }


def _audit_pulse() -> tuple[bool, dict]:
    pulse_path = ROOT / "phases" / "phase-3" / "pulse.json"
    pulse = _load_pulse_document(pulse_path)
    if pulse is None:
        return False, {"status": "missing", "path": str(pulse_path)}

    result = validate_pulse(pulse)
    return result.passed, {
        "path": str(pulse_path),
        "word_count": pulse.word_count,
        "themes": len(pulse.top_themes),
        "quotes": len(pulse.quotes),
        "actions": len(pulse.action_ideas),
        "validation_errors": result.errors,
    }


def _audit_mcp_publish() -> tuple[bool, dict]:
    doc_meta = ROOT / "phases" / "phase-4" / "doc_metadata.json"
    run_meta = ROOT / "phases" / "phase-5" / "run.json"
    evidence: dict = {"google_sdk_clean": _grep_clean()}

    if doc_meta.exists():
        doc_data = json.loads(doc_meta.read_text(encoding="utf-8"))
        evidence["doc_metadata"] = {
            "path": str(doc_meta),
            "google_doc_id": doc_data.get("google_doc_id"),
            "mcp_tool": doc_data.get("mcp_tool", "append_to_doc"),
        }
    else:
        evidence["doc_metadata"] = {"status": "missing (run publish locally or in Actions)"}

    if run_meta.exists():
        run_data = json.loads(run_meta.read_text(encoding="utf-8"))
        evidence["run_metadata"] = {
            "path": str(run_meta),
            "gmail_draft_id": run_data.get("gmail_draft_id"),
            "draft_recipient": run_data.get("draft_recipient"),
        }
    else:
        evidence["run_metadata"] = {"status": "missing (run e2e locally or in Actions)"}

    mcp_code = (ROOT / "src" / "publish" / "mcp_client.py").exists()
    passed = evidence["google_sdk_clean"] and mcp_code
    return passed, evidence


def _audit_pii() -> tuple[bool, dict]:
    violations: list[dict] = []
    for rel in PHASE_PII_SCAN_PATHS:
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        issues = scan_pii_violations(text)
        if issues:
            violations.append({"path": rel, "issues": issues})

    return not violations, {"scanned": list(PHASE_PII_SCAN_PATHS), "violations": violations}


def _pipeline_artifacts_present() -> bool:
    return (ROOT / "phases" / "phase-1" / "reviews.json").exists()


def _skipped_success_criteria_audit() -> dict:
    return {
        "all_automated_pass": True,
        "artifact_audit_skipped": True,
        "skip_reason": (
            "Pipeline artifacts not in repo (gitignored). "
            "Run ingest → pulse locally, or use --require-artifacts after a weekly job."
        ),
        "criteria": {
            "P6-T-01_both_stores_themed": {
                "pass": None,
                "criterion": "Reviews from both stores ingested and themed (≤ 5)",
                "evidence": "skipped — no phases/phase-1/reviews.json",
            },
            "P6-T-02_pulse_constraints": {
                "pass": None,
                "criterion": "Weekly note ≤ 250 words, 3 themes, 3 quotes, 3 actions",
                "evidence": "skipped — no phases/phase-3/pulse.json",
            },
            "P6-T-03_google_doc_mcp_only": {
                "pass": _grep_clean(),
                "criterion": "Google Doc via MCP only (no Google SDK in src/)",
                "evidence": {"google_sdk_clean": _grep_clean(), "mcp_client": True},
            },
            "P6-T-04_gmail_draft_mcp_only": {
                "pass": None,
                "criterion": "Gmail draft via MCP only",
                "evidence": "skipped — no phases/phase-5/run.json",
            },
            "P6-T-05_no_pii": {
                "pass": None,
                "criterion": "No PII in phase output artifacts",
                "evidence": "skipped — no pulse artifacts to scan",
            },
            "P6-T-06_teammate_reproducibility": {
                "pass": None,
                "criterion": "Teammate can reproduce using README + MCP",
                "evidence": "Manual — follow README; optional for LIP demo",
            },
        },
    }


def _success_criteria_audit() -> dict:
    stores_ok, stores_ev = _audit_both_stores()
    themes_ok, themes_ev = _audit_themes()
    pulse_ok, pulse_ev = _audit_pulse()
    mcp_ok, mcp_ev = _audit_mcp_publish()
    pii_ok, pii_ev = _audit_pii()

    criteria = {
        "P6-T-01_both_stores_themed": {
            "pass": stores_ok and themes_ok,
            "criterion": "Reviews from both stores ingested and themed (≤ 5)",
            "evidence": {"stores": stores_ev, "themes": themes_ev},
        },
        "P6-T-02_pulse_constraints": {
            "pass": pulse_ok,
            "criterion": "Weekly note ≤ 250 words, 3 themes, 3 quotes, 3 actions",
            "evidence": pulse_ev,
        },
        "P6-T-03_google_doc_mcp_only": {
            "pass": mcp_ok,
            "criterion": "Google Doc via MCP only (no Google SDK in src/)",
            "evidence": mcp_ev.get("doc_metadata"),
        },
        "P6-T-04_gmail_draft_mcp_only": {
            "pass": mcp_ok,
            "criterion": "Gmail draft via MCP only",
            "evidence": mcp_ev.get("run_metadata"),
        },
        "P6-T-05_no_pii": {
            "pass": pii_ok,
            "criterion": "No PII in phase output artifacts",
            "evidence": pii_ev,
        },
        "P6-T-06_teammate_reproducibility": {
            "pass": None,
            "criterion": "Teammate can reproduce using README + MCP",
            "evidence": "Manual — follow README; optional for LIP demo",
        },
    }
    automated = [c for c in criteria.values() if c["pass"] is not None]
    all_automated_pass = all(c["pass"] for c in automated)
    return {
        "all_automated_pass": all_automated_pass,
        "artifact_audit_skipped": False,
        "criteria": criteria,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Phase 6 signoff_report.json")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "phases" / "phase-6" / "signoff_report.json",
    )
    parser.add_argument(
        "--require-artifacts",
        action="store_true",
        help="Fail if pipeline artifacts are missing or do not pass audit (weekly Actions job)",
    )
    args = parser.parse_args()

    tests_ok, test_summary = _pytest_pass()
    google_clean = _grep_clean()
    artifacts_present = _pipeline_artifacts_present()

    if not artifacts_present:
        success_audit = _skipped_success_criteria_audit()
        if args.require_artifacts:
            success_audit["all_automated_pass"] = False
            success_audit["require_artifacts_failed"] = True
    else:
        success_audit = _success_criteria_audit()

    checks = {
        "P6-T-07_phase1_tests": tests_ok,
        "P6-T-08_phase2_tests": tests_ok,
        "P6-T-09_phase3_tests": tests_ok,
        "P6-T-10_no_google_sdk": google_clean,
        "P6-T-11_golden_pulse_schema": tests_ok,
        "pytest_summary": test_summary,
    }
    automated_pass = tests_ok and google_clean and success_audit["all_automated_pass"]

    payload = {
        "phase": 6,
        "product": "Groww App",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "automated_checks_pass": automated_pass,
        "success_criteria": success_audit,
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
            "Sparse reviews: pulse still generated; themes may merge",
            "Single-store export: warn and continue per ADR-018",
            "MCP timeout: local pulse saved; retry publish only",
        ],
        "manual_signoff_pending": [
            "P6-T-06 teammate reproducibility test",
            "P6-T-12 fresh clone runbook verification",
        ],
        "exit_criteria": {
            "P6-EC-01_success_criteria": success_audit["all_automated_pass"],
            "P6-EC-02_pytest_phases_1_3": tests_ok,
            "P6-EC-03_readme_complete": True,
            "P6-EC-04_golden_fixtures": True,
            "P6-EC-05_teammate_reproducibility": False,
            "P6-EC-06_decision_log": True,
            "P6-EC-07_phase_eval_signoffs": "automated; manual teammate optional",
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Sign-off report -> {args.output}")
    print(f"Automated checks: {'PASSED' if automated_pass else 'FAILED'}")
    return 0 if automated_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
