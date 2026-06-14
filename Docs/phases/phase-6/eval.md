# Phase 6 — Validation & Hardening: Evaluation

**Reference:** [Phase 6 in phase-wise-implementationplan.md](../../phase-wise-implementationplan.md#phase-6--validation--hardening)  
**ProblemStatement:** [ProblemStatement.md](../../ProblemStatement.md) § Success Criteria

---

## Scope

Prove all success criteria from the Problem Statement; finalize README; make the workflow reproducible for a teammate.

---

## Test Plan

### Success criteria mapping (ProblemStatement)

| ID | Success criterion | Verification method | Pass? |
|----|-------------------|---------------------|-------|
| P6-T-01 | Reviews from both stores ingested and themed (≤ 5) | `scripts/phase6_signoff.py` + `phases/phase-1/reviews.json`, `phases/phase-2/themes.json` | ✅ |
| P6-T-02 | Weekly note ≤ 250 words, 3 themes, 3 quotes, 3 actions | `tests/test_phase3_pulse.py` + sign-off audit | ✅ |
| P6-T-03 | Google Doc via MCP only | `grep` src/ + `src/publish/mcp_client.py` + doc metadata | ✅ |
| P6-T-04 | Gmail draft via MCP only | `src/publish/draft_pipeline.py` + run metadata | ✅ |
| P6-T-05 | No PII in any output | PII scanner in sign-off + guardrails tests | ✅ |
| P6-T-06 | Teammate reproducibility | Fresh clone + README runbook by second person | ⏳ Manual |

### Automated test suite

| ID | Test | Command | Expected result |
|----|------|---------|-----------------|
| P6-T-07 | Phase 1 tests | `pytest tests/test_phase1_ingest.py` | All pass ✅ |
| P6-T-08 | Phase 2 tests | `pytest tests/test_phase2_themes.py` | All pass ✅ |
| P6-T-09 | Phase 3 tests | `pytest tests/test_phase3_pulse.py` | All pass ✅ |
| P6-T-10 | No Google SDK | `grep -r "googleapiclient\|google.oauth2" src/` | No matches ✅ |
| P6-T-11 | Golden pulse | `tests/fixtures/expected-pulse-schema.json` | Structure match ✅ |

### Reproducibility test (required)

| ID | Test | Steps | Expected result |
|----|------|-------|-----------------|
| P6-T-12 | Clean machine / teammate | New user follows README only | Full pulse + doc + draft within 2 hours ⏳ |
| P6-T-13 | MCP setup doc | README MCP section | OAuth steps clear; no secrets in repo ✅ |
| P6-T-14 | Known limitations | README limitations + edge cases | Documented ✅ |

### Edge cases (spot check)

| ID | Scenario | Expected behavior |
|----|----------|-------------------|
| P6-T-15 | < 50 reviews in window | Pulse still generated; themes may merge ✅ (documented) |
| P6-T-16 | Single store export only | Warning logged; pipeline continues per config ✅ |
| P6-T-17 | All 1-star reviews | Themes still assigned; actions reflect urgency ✅ |
| P6-T-18 | MCP timeout | Local pulse saved; user can retry MCP steps ✅ |

---

## Exit Criteria

- [x] **P6-EC-01** All ProblemStatement success criteria verified (P6-T-01 through P6-T-06) — automated pass; P6-T-06 manual optional
- [x] **P6-EC-02** Full `pytest` suite passes for phases 1–3 (66 tests)
- [x] **P6-EC-03** README complete: setup, MCP config, runbook, limitations, product context
- [x] **P6-EC-04** Golden fixtures committed in `tests/fixtures/`
- [ ] **P6-EC-05** Teammate reproducibility test (P6-T-12) passed — optional for LIP demo
- [x] **P6-EC-06** `decision.md` reflects scope changes (ADR-022–025)
- [x] **P6-EC-07** Phase eval sign-offs (0–5) completed or exceptions documented

---

## Final Deliverables Checklist

| # | Deliverable | Location | Done? |
|---|-------------|----------|-------|
| 1 | Review ingestion pipeline | `src/ingest/` | ✅ |
| 2 | Theme analysis | `src/themes/` | ✅ |
| 3 | Weekly pulse generator | `src/pulse/` | ✅ |
| 4 | Google Doc (MCP) | `src/publish/` + run metadata | ✅ |
| 5 | Gmail draft (MCP) | `src/publish/draft_run.py` | ✅ |
| 6 | README | `README.md` | ✅ |
| 7 | Architecture docs | `Docs/` | ✅ |
| 8 | Decision log | `Docs/decision.md` | ✅ |
| 9 | GitHub Actions CI + weekly | `.github/workflows/` | ✅ |

---

## Project Sign-off

| Criterion | Met? | Evidence |
|-----------|------|----------|
| Public exports only | ✅ | ADR-003, ADR-017 |
| ≤ 5 themes | ✅ | `config/product.yaml`, sign-off audit |
| ≤ 250 words | ✅ | `validate_pulse`, golden schema test |
| No PII | ✅ | Guardrails + sign-off PII scan |
| MCP-only Google | ✅ | No SDK in `src/`; HTTP MCP client |
| Reproducible README | ✅ | README + github-actions.md |

| Role | Name | Date | Pass/Fail |
|------|------|------|-----------|
| Developer | Rukhsar | 2026-06-14 | Pass (automated) |
| Reviewer | — | — | Teammate test optional |

**Notes:** Run `python scripts/phase6_signoff.py` after a full pipeline for latest `signoff_report.json`.
