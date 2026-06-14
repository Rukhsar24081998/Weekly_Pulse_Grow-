# Phase 0 — Foundation & Planning: Evaluation

**Reference:** [Phase 0 in phase-wise-implementationplan.md](../../phase-wise-implementationplan.md#phase-0--foundation--planning)  
**Architecture:** [architecture.md](../../architecture.md)

---

## Scope

Lock product, MCP configuration, theme taxonomy, repo scaffold, and initial decisions before any pipeline code.

---

## Test Plan

### Manual tests

| ID | Test | Steps | Expected result |
|----|------|-------|-----------------|
| P0-T-01 | MCP server configured | Open Cursor MCP settings; confirm `google-docs` entry | `@a-bonus/google-docs-mcp` listed and enabled |
| P0-T-02 | MCP OAuth | Ask agent to call a lightweight MCP tool (e.g. `listLabels`) | OAuth completes; tool returns without auth error |
| P0-T-03 | Docs tool available | Inspect MCP tool list for document tools | `createDocument` (or equivalent) present |
| P0-T-04 | Gmail tool available | Inspect MCP tool list for Gmail tools | `createDraft` present |
| P0-T-05 | Product documented | Read README stub + `decision.md` ADR-002 | Target app named (not TBD); ADR-002 status `accepted` |
| P0-T-06 | Theme taxonomy | Open `config/themes.yaml` | ≥ 5 candidate themes with IDs and keywords |
| P0-T-07 | Decision log | Open `decision.md` | ADR-001 through ADR-008 recorded as accepted |

### Automated / structural checks

| ID | Test | Command / check | Expected result |
|----|------|-----------------|-----------------|
| P0-T-08 | Repo scaffold | Directory exists | `src/`, `data/raw`, `phases/phase-0` … `phase-6`, `tests/`, `prompts/` |
| P0-T-09 | No secrets in repo | `git grep -i "client_secret"` | No matches in tracked files |
| P0-T-10 | Docs cross-links | All phase eval paths resolve | Links in implementation plan open correctly |

---

## Exit Criteria

All items must pass before starting Phase 1.

- [ ] **P0-EC-01** Product locked to Milestone 1 mobile app; name recorded in README and `decision.md` ADR-002
- [ ] **P0-EC-02** App Store + Play Store export approach documented (paths, format notes)
- [ ] **P0-EC-03** `@a-bonus/google-docs-mcp` configured in Cursor MCP settings
- [ ] **P0-EC-04** MCP OAuth smoke test passed (at least one Gmail or Docs tool succeeds)
- [ ] **P0-EC-05** `config/themes.yaml` exists with labeled theme IDs
- [ ] **P0-EC-06** Repo scaffold matches architecture directory layout
- [ ] **P0-EC-07** `decision.md` contains accepted ADRs for MCP-only Google, PII, and theme caps
- [ ] **P0-EC-08** README skeleton states: public exports only, ≤5 themes, ≤250 words, no PII, MCP-only Google

---

## Sign-off

| Role | Name | Date | Pass/Fail |
|------|------|------|-----------|
| Developer | | | |
| Reviewer | | | |

**Notes:**
