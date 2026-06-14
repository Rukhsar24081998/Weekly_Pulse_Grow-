# Phase 0 — Foundation & Planning: Deliverables

**Product:** Groww App  
**Repo folder:** [phases/phase-0/](../../phases/phase-0/)  
**Eval:** [eval.md](./eval.md)

## Completed (automated / scaffold)

- [x] Product locked to **Groww App** — README, `config/product.yaml`, ADR-002
- [x] Export approach documented — `Docs/review-export-formats.md`
- [x] Theme taxonomy — `config/themes.yaml` (8 Groww themes)
- [x] Repo scaffold — `src/`, `data/`, `tests/`, `prompts/`, `config/`, `phases/`
- [x] MCP setup guide — `.cursor/mcp.json.example`
- [x] Decision log — ADR-001 through ADR-019
- [x] README with constraints and layout
- [x] **12-week default** — `config/product.yaml` (`default_weeks: 12`)
- [x] **Raw reviews** — Play ~9,830 rows (~12 weeks); App Store partial (see below)
- [x] **Phase 1 prep** — ADR-018/019, ingestion config, test fixtures, `pre_phase1_check.py`
- [x] Phase 0 validation — `phases/phase-0/phase0_report.json`

## Pre-Phase 1 (done)

- [x] Ingestion edge cases decided — warn on missing store / short window (ADR-018, ADR-019)
- [x] Test fixtures — `tests/fixtures/reviews/*.csv` via `scripts/build_test_fixtures.py`
- [x] Pre-Phase 1 check — `python scripts/pre_phase1_check.py`

## Manual (operator)

- [ ] **App Store 12-week export** — replace `data/raw/groww_app_store_reviews.csv` ([APP_STORE_EXPORT_NEEDED.md](../../data/raw/APP_STORE_EXPORT_NEEDED.md))
- [ ] Configure `@a-bonus/google-docs-mcp` in Cursor (P0-EC-03) — before Phase 4
- [ ] MCP OAuth smoke test (P0-EC-04) — before Phase 4
- [ ] Set `publish.draft_recipient` or `DRAFT_RECIPIENT` env — before Phase 5
- [ ] Phase 0 eval sign-off in [eval.md](./eval.md)

## Ready for Phase 1 implementation?

Run `python scripts/pre_phase1_check.py`. **Yes** when Play Store ≥8 weeks and fixtures exist (current state). Full Phase 1 **sign-off** needs both stores ≥8 weeks.
