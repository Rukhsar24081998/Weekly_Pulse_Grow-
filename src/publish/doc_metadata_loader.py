"""Load Phase 4 doc metadata for draft body."""

from __future__ import annotations

import json
from pathlib import Path


def load_doc_metadata(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
