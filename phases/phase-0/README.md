# Phase 0 — Foundation & Planning

**Product:** Groww App  
**Status:** Complete for Phase 1 start (App Store official export pending for sign-off)  
**Eval:** [Docs/phases/phase-0/eval.md](../Docs/phases/phase-0/eval.md)

## Purpose

Lock product scope, MCP path, theme taxonomy, and repository structure before pipeline code.

## Deliverables

| Item | Location |
|------|----------|
| Product config | `config/product.yaml` |
| Theme taxonomy | `config/themes.yaml` |
| Export format guide | `Docs/review-export-formats.md` |
| Fetch script | `scripts/fetch_public_reviews.py` |
| Validate raw exports | `scripts/validate_raw_exports.py` |
| Pre-Phase 1 check | `scripts/pre_phase1_check.py` |
| Test fixtures builder | `scripts/build_test_fixtures.py` |
| Phase 0 report | `phases/phase-0/phase0_report.json` |
| Fetch metadata | `phases/phase-0/fetch_metadata.json` |
| Play raw (~12 wk) | `data/raw/groww_play_store_reviews.csv` |
| App raw (partial) | `data/raw/groww_app_store_reviews.csv` + [APP_STORE_EXPORT_NEEDED.md](../data/raw/APP_STORE_EXPORT_NEEDED.md) |

## Before Phase 1

```bash
source .venv/bin/activate
python scripts/build_test_fixtures.py
python scripts/pre_phase1_check.py
```

## Manual (later phases)

- [ ] App Store Connect 12-week CSV → `data/raw/groww_app_store_reviews.csv`
- [ ] MCP setup (Phase 4) — `.cursor/mcp.json.example`
- [ ] `publish.draft_recipient` (Phase 5)

## Next phase

→ [Phase 1](../phase-1/README.md) — Review Ingestion
