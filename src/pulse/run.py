#!/usr/bin/env python3
"""CLI entry point for pulse generation (Phase 3)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.pulse.config_loader import load_pulse_config
from src.pulse.exceptions import PulseError, PulseValidationError
from src.pulse.pipeline import run_pulse_generation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate weekly pulse from theme assignments (Phase 3).",
        epilog="Outputs: phases/phase-3/pulse.md, phases/phase-3/pulse.json",
    )
    parser.add_argument(
        "--themes",
        type=Path,
        default=None,
        help="Themes JSON input (default: phases/phase-2/themes.json)",
    )
    parser.add_argument(
        "--reviews",
        type=Path,
        default=None,
        help="Reviews JSON for quote lookup (default: phases/phase-1/reviews.json)",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=None,
        help="Pulse markdown output path",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=None,
        help="Pulse JSON output path",
    )
    parser.add_argument(
        "--no-strict",
        action="store_true",
        help="Write outputs even if validation fails",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_pulse_config()

    try:
        result = run_pulse_generation(
            config=config,
            themes_path=args.themes,
            reviews_path=args.reviews,
            output_md=args.output_md,
            output_json=args.output_json,
            strict=not args.no_strict,
        )
    except PulseValidationError as exc:
        print("VALIDATION FAILED:", file=sys.stderr)
        for error in exc.errors:
            print(f"  - {error}", file=sys.stderr)
        return 2
    except PulseError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Pulse generated -> {result.output_md}")
    print(f"JSON sidecar -> {result.output_json}")
    print(f"Word count: {result.word_count}")
    print(f"Validation: {'PASSED' if result.validation_passed else 'FAILED'}")
    if result.validation_errors:
        for error in result.validation_errors:
            print(f"WARNING: {error}")
    return 0 if result.validation_passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
