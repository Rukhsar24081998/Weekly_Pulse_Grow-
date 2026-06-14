#!/usr/bin/env bash
# Full weekly run including MCP publish (requires env secrets on the host).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

bash scripts/run_pipeline_public.sh

if [[ "${RUN_PUBLISH:-true}" == "true" ]]; then
  echo "==> Publish (Google Doc + Gmail draft)"
  python -m src.publish.e2e_run
fi

python scripts/phase6_signoff.py --require-artifacts || true
echo "Weekly full run complete."
