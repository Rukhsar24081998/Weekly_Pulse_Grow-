#!/usr/bin/env bash
# Refresh public pulse data (no MCP publish). Used on Railway cron or manual bootstrap.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> Fetch public reviews"
python scripts/fetch_public_reviews.py --weeks 12

echo "==> Ingest"
python -m src.ingest.run --weeks 12

echo "==> Themes (rules-only for reliability)"
python -m src.themes.run --no-groq

echo "==> Pulse"
python -m src.pulse.run

echo "==> Validate"
python -m src.guardrails.validate phases/phase-3/pulse.md

echo "Pipeline data refresh complete."
