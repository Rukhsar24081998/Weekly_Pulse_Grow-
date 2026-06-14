#!/usr/bin/env python3
"""CLI for pulse validation (Phase 3 guardrails)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.paths import deliverable
from src.publish.exceptions import PublishValidationError
from src.publish.preflight import run_preflight


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate pulse markdown/json before publish.")
    parser.add_argument(
        "pulse_md",
        nargs="?",
        type=Path,
        default=None,
        help="Pulse markdown path (default: phases/phase-3/pulse.md)",
    )
    parser.add_argument(
        "--pulse-json",
        type=Path,
        default=None,
        help="Pulse JSON path (default: phases/phase-3/pulse.json)",
    )
    parser.add_argument(
        "--no-require-prior-validation",
        action="store_true",
        help="Re-run validator even if pulse.json validation_passed is false",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    md_path = args.pulse_md or deliverable(3, "pulse_md")
    json_path = args.pulse_json or deliverable(3, "pulse_json")

    try:
        pulse = run_preflight(
            json_path,
            md_path,
            require_prior_validation=not args.no_require_prior_validation,
        )
    except PublishValidationError as exc:
        for error in exc.errors:
            print(error, file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Validation PASSED — {pulse.word_count} words, week ending {pulse.week_ending}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
