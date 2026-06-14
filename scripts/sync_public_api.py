#!/usr/bin/env python3
"""Upload local phase artifacts to the public Pulse API (Railway)."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_payload(root: Path) -> dict:
    payload: dict = {}

    reviews = root / "phases/phase-1/reviews.json"
    themes = root / "phases/phase-2/themes.json"
    pulse_json = root / "phases/phase-3/pulse.json"
    pulse_md = root / "phases/phase-3/pulse.md"
    doc_meta = root / "phases/phase-4/doc_metadata.json"
    run_meta = root / "phases/phase-5/run.json"

    if not pulse_json.exists():
        raise FileNotFoundError(f"Missing {pulse_json} — run the pipeline first")

    payload["pulse_json"] = _load_json(pulse_json)
    payload["pulse_md"] = pulse_md.read_text(encoding="utf-8") if pulse_md.exists() else ""

    if reviews.exists():
        payload["reviews"] = _load_json(reviews)
    if themes.exists():
        payload["themes"] = _load_json(themes)
    if doc_meta.exists():
        payload["doc_metadata"] = _load_json(doc_meta)
    if run_meta.exists():
        payload["run_metadata"] = _load_json(run_meta)

    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync phase artifacts to public Pulse API")
    parser.add_argument(
        "--api-url",
        default=os.environ.get("PUBLIC_PULSE_API_URL", "").strip(),
        help="Railway pulse-api base URL",
    )
    parser.add_argument(
        "--secret",
        default=os.environ.get("SYNC_SECRET", "").strip(),
        help="Bearer token (same as SYNC_SECRET on Railway)",
    )
    args = parser.parse_args()

    if not args.api_url:
        print("Set PUBLIC_PULSE_API_URL or pass --api-url", file=sys.stderr)
        return 1
    if not args.secret:
        print("Set SYNC_SECRET or pass --secret", file=sys.stderr)
        return 1

    payload = build_payload(ROOT)
    body = json.dumps(payload).encode("utf-8")
    url = args.api_url.rstrip("/") + "/api/sync/artifacts"
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {args.secret}",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"Sync failed ({exc.code}): {detail}", file=sys.stderr)
        return 1

    print(f"Synced to {url}")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
