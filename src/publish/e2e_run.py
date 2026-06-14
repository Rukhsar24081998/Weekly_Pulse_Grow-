#!/usr/bin/env python3
"""CLI entry point for Phase 4+5 E2E publish."""

from __future__ import annotations

import argparse
import sys

from src.publish.config_loader import load_publish_config
from src.publish.e2e_pipeline import run_e2e_publish
from src.publish.exceptions import DraftError, McpError, PublishError, PublishValidationError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Publish pulse to Google Doc and Gmail draft (Phases 4+5).",
        epilog="Outputs: phases/phase-4/doc_metadata.json, phases/phase-5/run.json",
    )
    parser.add_argument("--doc-id", type=str, default=None, help="Google Doc ID override")
    parser.add_argument("--to", type=str, default=None, help="Draft recipient email override")
    parser.add_argument("--dry-run", action="store_true", help="Validate only; no MCP calls")
    parser.add_argument("--skip-doc", action="store_true", help="Skip Phase 4 doc publish")
    parser.add_argument("--skip-draft", action="store_true", help="Skip Phase 5 draft")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_publish_config()

    try:
        result = run_e2e_publish(
            config=config,
            doc_id=args.doc_id,
            recipient=args.to,
            dry_run=args.dry_run,
            skip_doc=args.skip_doc,
            skip_draft=args.skip_draft,
        )
    except PublishValidationError as exc:
        print("VALIDATION FAILED:", file=sys.stderr)
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
        print("E2E dry run complete.")
        return 0

    print(f"E2E publish complete -> {result.output_path}")
    if result.google_doc_url:
        print(f"Google Doc: {result.google_doc_url}")
    print(f"Gmail draft ID: {result.gmail_draft_id}")
    print("Draft not sent — review in Gmail before sending.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
