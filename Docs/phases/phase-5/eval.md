# Phase 5 — Gmail Draft & E2E Orchestration: Evaluation

**Reference:** [Phase 5 in phase-wise-implementationplan.md](../../phase-wise-implementationplan.md#phase-5--gmail-draft--e2e-orchestration)  
**Architecture:** [architecture.md](../../architecture.md) §4

---

## Scope

Create a Gmail draft to self/alias via MCP; wire the full weekly workflow into a single agent runbook.

---

## Test Plan

### MCP Gmail tests (agent-driven)

| ID | Test | Agent steps | Expected result |
|----|------|-------------|-----------------|
| P5-T-01 | Create draft | MCP `createDraft` to configured self/alias | Returns `draftId` |
| P5-T-02 | Subject line | Inspect draft | `Weekly App Review Pulse — <Product Name> — YYYY-MM-DD` |
| P5-T-03 | Body content | Open draft in Gmail | Body matches pulse (or includes doc link + summary) |
| P5-T-04 | Recipient | Inspect `To` field | Self email or documented alias only |
| P5-T-05 | Not auto-sent | Check Sent folder | Email remains in Drafts only |
| P5-T-06 | List drafts verify | MCP `listDrafts` / `getDraft` | Draft findable by subject |
| P5-T-07 | Run metadata | `phases/phase-5/run.json` | `gmail_draft_id` populated |

### E2E orchestration tests

| ID | Test | Steps | Expected result |
|----|------|-------|-----------------|
| P5-T-08 | Full agent workflow | Run `prompts/weekly-pulse-agent.md` from raw exports | Ingest → themes → pulse → doc → draft completes |
| P5-T-09 | Constraint preserved E2E | Inspect final artifacts | ≤250 words, no PII, 3/3/3 structure |
| P5-T-10 | Idempotent re-run | Run twice same week with `--force` flag | New doc/draft or documented update behavior |
| P5-T-11 | Failure mid-flow | Remove MCP mid-run (optional) | Local pulse saved; clear recovery instructions |

### Documentation tests

| ID | Test | Expected result |
|----|------|-----------------|
| P5-T-12 | `prompts/draft-email.md` | Gmail MCP steps documented |
| P5-T-13 | `prompts/weekly-pulse-agent.md` | Full E2E sequence documented |
| P5-T-14 | README runbook | Teammate can follow without verbal handoff |

---

## Exit Criteria

- [ ] **P5-EC-01** Gmail draft created via MCP `createDraft` only
- [ ] **P5-EC-02** Draft addressed to self/alias (documented in README)
- [ ] **P5-EC-03** Subject and body match template; pulse content included
- [ ] **P5-EC-04** Draft not sent automatically
- [ ] **P5-EC-05** `gmail_draft_id` in run metadata alongside `google_doc_id`
- [ ] **P5-EC-06** E2E agent prompt runs full pipeline in one documented session
- [ ] **P5-EC-07** No direct Google API code introduced in Phase 5

---

## E2E Checklist (copy for each weekly run)

```
[ ] Exports placed in data/raw/
[ ] python -m src.ingest.run --weeks <8-12>
[ ] python -m src.themes.run
[ ] python -m src.pulse.run
[ ] Validator pass
[ ] MCP: Google Doc created
[ ] MCP: Gmail draft created
[ ] run-<date>.json complete
```

---

## Sign-off

| Role | Name | Date | Pass/Fail |
|------|------|------|-----------|
| Developer | | | |
| Reviewer | | | |

**Notes:**
