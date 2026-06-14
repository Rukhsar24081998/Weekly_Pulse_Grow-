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
| P6-T-01 | Reviews from both stores ingested and themed (≤ 5) | Run pipeline on real exports; inspect `themes.json` | |
| P6-T-02 | Weekly note ≤ 250 words, 3 themes, 3 quotes, 3 actions | `tests/test_phase3_pulse.py` + manual read | |
| P6-T-03 | Google Doc via MCP only | Code grep + agent log + doc link | |
| P6-T-04 | Gmail draft via MCP only | Code grep + draft in Gmail | |
| P6-T-05 | No PII in any output | PII scanner on all `phases/phase-*` artifacts | |
| P6-T-06 | Teammate reproducibility | Fresh clone + README runbook by second person | |

### Automated test suite

| ID | Test | Command | Expected result |
|----|------|---------|-----------------|
| P6-T-07 | Phase 1 tests | `pytest tests/test_phase1_ingest.py` | All pass |
| P6-T-08 | Phase 2 tests | `pytest tests/test_phase2_themes.py` | All pass |
| P6-T-09 | Phase 3 tests | `pytest tests/test_phase3_pulse.py` | All pass |
| P6-T-10 | No Google SDK | `grep -r "googleapiclient\|google.oauth2" src/` | No matches |
| P6-T-11 | Golden pulse | Compare output to `tests/fixtures/expected-pulse.json` | Structure match |

### Reproducibility test (required)

| ID | Test | Steps | Expected result |
|----|------|-------|-----------------|
| P6-T-12 | Clean machine / teammate | New user follows README only | Full pulse + doc + draft within 2 hours |
| P6-T-13 | MCP setup doc | README MCP section | OAuth steps clear; no secrets in repo |
| P6-T-14 | Known limitations | README limitations section | Sparse data, MCP downtime, export format drift documented |

### Edge cases (spot check)

| ID | Scenario | Expected behavior |
|----|----------|-------------------|
| P6-T-15 | < 50 reviews in window | Pulse still generated; themes may merge |
| P6-T-16 | Single store export only | Warning logged; pipeline continues or aborts per config |
| P6-T-17 | All 1-star reviews | Themes still assigned; actions reflect urgency |
| P6-T-18 | MCP timeout | Local pulse saved; user can retry MCP steps |

---

## Exit Criteria

- [ ] **P6-EC-01** All ProblemStatement success criteria verified (P6-T-01 through P6-T-06)
- [ ] **P6-EC-02** Full `pytest` suite passes for phases 1–3
- [ ] **P6-EC-03** README complete: setup, MCP config, runbook, limitations, product context
- [ ] **P6-EC-04** Golden fixtures committed in `tests/fixtures/`
- [ ] **P6-EC-05** Teammate reproducibility test (P6-T-12) passed
- [ ] **P6-EC-06** `decision.md` reflects any scope changes discovered during build
- [ ] **P6-EC-07** All phase eval sign-offs (0–5) completed or exceptions documented

---

## Final Deliverables Checklist

| # | Deliverable | Location | Done? |
|---|-------------|----------|-------|
| 1 | Review ingestion pipeline | `src/ingest/` | |
| 2 | Theme analysis | `src/themes/` | |
| 3 | Weekly pulse generator | `src/pulse/` | |
| 4 | Google Doc (MCP) | Agent + run metadata | |
| 5 | Gmail draft (MCP) | Agent + run metadata | |
| 6 | README | `README.md` | |
| 7 | Architecture docs | `Docs/` | |
| 8 | Decision log | `Docs/decision.md` | |

---

## Project Sign-off

| Criterion | Met? | Evidence |
|-----------|------|----------|
| Public exports only | | |
| ≤ 5 themes | | |
| ≤ 250 words | | |
| No PII | | |
| MCP-only Google | | |
| Reproducible README | | |

| Role | Name | Date | Pass/Fail |
|------|------|------|-----------|
| Developer | | | |
| Reviewer | | | |

**Notes:**
