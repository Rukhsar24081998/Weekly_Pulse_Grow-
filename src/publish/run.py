#!/usr/bin/env python3
"""CLI entry point for Google Doc publish (Phase 4)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.publish.config_loader import load_publish_config
from src.publish.exceptions import McpError, PublishError, PublishValidationError
from src.publish.pipeline import run_doc_publish


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Publish validated pulse to Google Doc via MCP HTTP server (Phase 4).",
        epilog="Output: phases/phase-4/doc_metadata.json",
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
        "--output",
        type=Path,
        default=None,
        help="Doc metadata output (default: phases/phase-4/doc_metadata.json)",
    )
    parser.add_argument(
        "--doc-id",
        type=str,
        default=None,
        help="Existing Google Doc ID (overrides PUBLISH_GOOGLE_DOC_ID)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate pulse and write dry-run metadata without calling MCP",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_publish_config()

    try:
        result = run_doc_publish(
            config=config,
            pulse_md_path=args.pulse_md,
            pulse_json_path=args.pulse_json,
            output_path=args.output,
            doc_id=args.doc_id,
            dry_run=args.dry_run,
        )
    except PublishValidationError as exc:
        print("VALIDATION FAILED — MCP publish blocked:", file=sys.stderr)
        for error in exc.errors:
            print(f"  - {error}", file=sys.stderr)
        return 2
    except McpError as exc:
        print(f"MCP ERROR: {exc}", file=sys.stderr)
        return 3
    except PublishError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"Dry run complete -> {result.output_path}")
        print(f"Doc title: {result.doc_title}")
        return 0

    print(f"Published to Google Doc -> {result.google_doc_url}")
    print(f"Doc ID: {result.google_doc_id}")
    print(f"Metadata -> {result.output_path}")
    print(f"MCP tool: {result.mcp_tool}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
