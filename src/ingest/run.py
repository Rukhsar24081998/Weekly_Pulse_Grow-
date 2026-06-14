#!/usr/bin/env python3
"""CLI entry point for review ingestion (Phase 1)."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from src.ingest.exceptions import EmptyExportError, IngestionError
from src.ingest.pipeline import run_ingestion


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ingest App Store and Play Store review exports into normalized JSON.",
        epilog="Default window: 12 weeks (config/product.yaml). Output: phases/phase-1/reviews.json",
    )
    parser.add_argument(
        "--weeks",
        type=int,
        default=None,
        help="Review window in weeks (8–12). Default from config.",
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=None,
        help="Directory containing raw CSV exports (default: data/raw)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSON path (default: phases/phase-1/reviews.json)",
    )
    parser.add_argument(
        "--reference-date",
        type=str,
        default=None,
        help="Reference end date YYYY-MM-DD (default: today UTC)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    reference = date.fromisoformat(args.reference_date) if args.reference_date else None

    try:
        result = run_ingestion(
            weeks=args.weeks,
            raw_dir=args.raw_dir,
            output_path=args.output,
            reference_date=reference,
        )
    except EmptyExportError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except IngestionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Ingestion complete -> {result.output_path}")
    print(
        f"Window: {result.window_start} to {result.window_end} ({result.review_window_weeks} weeks)"
    )
    print(
        f"Reviews: {result.total_reviews} total "
        f"(app_store={result.app_store_count}, play_store={result.play_store_count})"
    )
    if result.duplicates_removed:
        print(f"Deduplicated: {result.duplicates_removed} duplicate rows removed")
    if result.content_filtered:
        print(f"Content filtered: {result.content_filtered} reviews removed (short / emoji / non-English)")
    if result.outside_window:
        print(f"Filtered: {result.outside_window} reviews outside window")
    for warning in result.warnings:
        if not warning.startswith("Window"):
            print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
