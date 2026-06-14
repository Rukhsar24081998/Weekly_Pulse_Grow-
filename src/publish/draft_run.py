#!/usr/bin/env python3
"""CLI entry point for Gmail draft publish (Phase 5)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.publish.config_loader import load_publish_config
from src.publish.draft_pipeline import run_draft_publish
from src.publish.exceptions import DraftError, McpError, PublishError, PublishValidationError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create Gmail draft with validated pulse via MCP server (Phase 5).",
        epilog="Output: phases/phase-5/run.json — draft is NOT sent automatically.",
    )
    parser.add_argument(
        "--pulse-md",
        type=Path,
        default=None,
        help="Pulse markdown input (default: phases/phase-3/pulse.md)",
    )
    parser.add_argument(
        "--pulse-json",
        type=Path,
        default=None,
        help="Pulse JSON input (default: phases/phase-3/pulse.json)",
    )
    parser.add_argument(
        "--doc-metadata",
        type=Path,
        default=None,
        help="Phase 4 doc metadata (default: phases/phase-4/doc_metadata.json)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Run metadata output (default: phases/phase-5/run.json)",
    )
    parser.add_argument(
        "--to",
        type=str,
        default=None,
        help="Draft recipient email (overrides DRAFT_RECIPIENT in .env)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and preview without calling MCP",
    )
    parser.add_argument(
        "--no-run-json",
        action="store_true",
        help="Skip writing phases/phase-5/run.json",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_publish_config()

    try:
        result = run_draft_publish(
            config=config,
            pulse_md_path=args.pulse_md,
            pulse_json_path=args.pulse_json,
            doc_metadata_path=args.doc_metadata,
            run_metadata_path=args.output,
            recipient=args.to,
            dry_run=args.dry_run,
            write_run_json=not args.no_run_json and not args.dry_run,
        )
    except PublishValidationError as exc:
        print("VALIDATION FAILED — MCP draft blocked:", file=sys.stderr)
        for error in exc.errors:
            print(f"  - {error}", file=sys.stderr)
        return 2
    except DraftError as exc:
        print(f"DRAFT ERROR: {exc}", file=sys.stderr)
        return 4
    except McpError as exc:
        print(f"MCP ERROR: {exc}", file=sys.stderr)
        return 3
    except PublishError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"Dry run complete -> {result.output_path}")
        print(f"Subject: {result.subject}")
        print(f"To: {result.recipient}")
        return 0

    print(f"Gmail draft created (not sent)")
    print(f"Draft ID: {result.gmail_draft_id}")
    print(f"To: {result.recipient}")
    print(f"Subject: {result.subject}")
    print(f"Run metadata -> {result.output_path}")
    print("Open Gmail → Drafts to review before sending.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
