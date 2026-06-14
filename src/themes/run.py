#!/usr/bin/env python3
"""CLI entry point for theme clustering (Phase 2)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.env_loader import load_env
from src.themes.config_loader import load_theme_config
from src.themes.exceptions import EmptyCorpusError, ThemeError
from src.themes.pipeline import run_theme_clustering


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Cluster reviews into themes (Phase 2).",
        epilog="Output: phases/phase-2/themes.json",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Normalized reviews JSON (default: phases/phase-1/reviews.json)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Theme output JSON (default: phases/phase-2/themes.json)",
    )
    parser.add_argument(
        "--no-groq",
        action="store_true",
        help="Rules-only path (no Groq API calls)",
    )
    parser.add_argument(
        "--max-reviews",
        type=int,
        default=None,
        help="Override max review sample size (default from config)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    load_env()
    args = build_parser().parse_args(argv)
    config = load_theme_config()
    if args.max_reviews is not None:
        config.max_reviews = args.max_reviews

    try:
        result = run_theme_clustering(
            config=config,
            reviews_path=args.input,
            output_path=args.output,
            use_groq=False if args.no_groq else None,
        )
    except EmptyCorpusError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except ThemeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Theme clustering complete -> {result.output_path}")
    print(
        f"Sample: {result.sample_size} reviews (from {result.sampled_from}) "
        f"-> {result.theme_count} themes"
    )
    print(f"Top pulse themes: {', '.join(result.top_theme_ids)}")
    if result.groq_usage.enabled:
        print(
            f"Groq: {result.groq_usage.requests} requests, "
            f"~{result.groq_usage.tokens_estimated} tokens estimated"
        )
    else:
        print("Groq: not used (rules-only)")
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
