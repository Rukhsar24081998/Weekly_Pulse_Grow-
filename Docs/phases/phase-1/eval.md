# Phase 1 — Review Ingestion: Evaluation

**Reference:** [Phase 1 in phase-wise-implementationplan.md](../../phase-wise-implementationplan.md#phase-1--review-ingestion)  
**Architecture:** [architecture.md](../../architecture.md) §3.1

---

## Scope

Ingest 8–12 weeks of App Store and Play Store public exports into normalized JSON with no reviewer PII.

---

## Test Plan

### Unit tests

| ID | Test | File | Expected result |
|----|------|------|-----------------|
| P1-T-01 | App Store parser | `tests/test_phase1_ingest.py` | Parses fixture CSV → valid review records |
| P1-T-02 | Play Store parser | `tests/test_phase1_ingest.py` | Parses fixture CSV → valid review records |
| P1-T-03 | Schema validation | `tests/test_phase1_ingest.py` | Required fields: `store`, `rating`, `text`, `review_date` |
| P1-T-04 | PII exclusion | `tests/test_phase1_ingest.py` | Output JSON has no `reviewer_name`, `email`, `user_id` keys |
| P1-T-05 | Date window 8 weeks | `tests/test_phase1_ingest.py` | Reviews outside window excluded |
| P1-T-06 | Date window 12 weeks | `tests/test_phase1_ingest.py` | `--weeks 12` includes expected boundary dates |
| P1-T-07 | Empty export handling | `tests/test_phase1_ingest.py` | Empty file → clear error, non-zero exit |
| P1-T-08 | Duplicate reviews | `tests/test_phase1_ingest.py` | Same text+date deduped by `id` hash |

### Integration tests

| ID | Test | Steps | Expected result |
|----|------|-------|-----------------|
| P1-T-09 | Full ingest CLI | `python -m src.ingest.run --weeks 10` | Writes `phases/phase-1/reviews.json` |
| P1-T-10 | Both stores present | Inspect output stats | `app_store` and `play_store` counts > 0 |
| P1-T-11 | Date range report | CLI stdout / run metadata | Start/end dates within 8–12 week window |

### Manual checks

| ID | Test | Expected result |
|----|------|-----------------|
| P1-T-12 | Export format doc | `docs/review-export-formats.md` maps columns for each store |
| P1-T-13 | Spot-check 10 reviews | Ratings and dates match source export |
| P1-T-14 | No login scraping | Code review: no Selenium/Playwright against store UIs |

---

## Exit Criteria

- [ ] **P1-EC-01** App Store and Play Store parsers implemented and tested
- [ ] **P1-EC-02** `phases/phase-1/reviews.json` produced with unified schema
- [ ] **P1-EC-03** Review window configurable 8–12 weeks; default documented
- [ ] **P1-EC-04** Zero reviewer PII fields in normalized output
- [ ] **P1-EC-05** `tests/test_phase1_ingest.py` passes (≥ 8 test cases)
- [ ] **P1-EC-06** Ingestion CLI documented in README or inline `--help`
- [ ] **P1-EC-07** Both stores contribute reviews when exports are provided

---

## Fixture Requirements

Place sample exports (anonymized) in `tests/fixtures/reviews/`:

- `app_store_sample.csv` — ≥ 20 rows spanning multiple weeks
- `play_store_sample.csv` — ≥ 20 rows spanning multiple weeks

---

## Sign-off

| Role | Name | Date | Pass/Fail |
|------|------|------|-----------|
| Developer | | | |
| Reviewer | | | |

**Notes:**
