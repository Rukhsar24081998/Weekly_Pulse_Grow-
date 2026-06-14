#!/usr/bin/env bash
set -euo pipefail
exec "$(dirname "$0")/py" -m src.ingest.run "$@"
