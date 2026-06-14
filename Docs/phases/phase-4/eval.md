# Phase 4 — Google Docs via MCP: Evaluation

**Reference:** [Phase 4 in phase-wise-implementationplan.md](../../phase-wise-implementationplan.md#phase-4--google-docs-via-mcp)  
**Architecture:** [architecture.md](../../architecture.md) §5

---

## Scope

Publish the validated weekly pulse to Google Docs using MCP tools only. No Google SDK in application code.

---

## Test Plan

### Pre-flight checks

| ID | Test | Command / step | Expected result |
|----|------|----------------|-----------------|
| P4-T-01 | No Google SDK | `grep -r "googleapiclient\|google.oauth2\|googleapis.com" src/` | No matches |
| P4-T-02 | Pulse validated | `python -m src.guardrails.validate phases/phase-3/pulse.md` | Exit 0 |
| P4-T-03 | MCP connected | Agent MCP tool list | Docs tools available |

### MCP integration tests (agent-driven)

| ID | Test | Agent steps | Expected result |
|----|------|-------------|-----------------|
| P4-T-04 | Create document | MCP `createDocument` with title `<Product Name> Weekly Pulse — YYYY-MM-DD` | Returns `documentId` / URL |
| P4-T-05 | Write pulse content | MCP write/append tools with full pulse markdown | Doc body matches local `pulse-<date>.md` |
| P4-T-06 | Content completeness | Open doc in browser | All 3 themes, 3 quotes, 3 actions present |
| P4-T-07 | No PII in doc | Manual scan of Google Doc | No emails, phones, or account IDs |
| P4-T-08 | Run metadata | Check `phases/phase-4/doc_metadata.json` | `google_doc_id` recorded |

### Negative tests

| ID | Test | Steps | Expected result |
|----|------|-------|-----------------|
| P4-T-09 | Invalid pulse blocked | Attempt MCP publish with > 250 word pulse | Agent refuses or validator blocks first |
| P4-T-10 | MCP auth failure | Simulate expired token (if possible) | Clear error; no partial doc left orphaned without log |

### Prompt / documentation tests

| ID | Test | Expected result |
|----|------|-----------------|
| P4-T-11 | `prompts/publish-doc.md` exists | Step-by-step MCP instructions for agent |
| P4-T-12 | README MCP section | Documents Doc naming convention and MCP-only rule |

---

## Exit Criteria

- [ ] **P4-EC-01** Google Doc created exclusively via MCP tools (no direct API code)
- [ ] **P4-EC-02** Doc title follows convention: `<Product Name> Weekly Pulse — YYYY-MM-DD`
- [ ] **P4-EC-03** Doc content matches validated local pulse file
- [ ] **P4-EC-04** `google_doc_id` stored in run metadata JSON
- [ ] **P4-EC-05** Repo contains zero `googleapis` / Google SDK imports in `src/`
- [ ] **P4-EC-06** `prompts/publish-doc.md` committed and usable by agent
- [ ] **P4-EC-07** Reviewer can open doc link and confirm readability

---

## Evidence to Capture

- Screenshot or link to Google Doc (share settings noted in README)
- `phases/phase-4/doc_metadata.json` snippet with `google_doc_id`
- Agent transcript or log showing MCP tool calls (optional)

---

## Sign-off

| Role | Name | Date | Pass/Fail |
|------|------|------|-----------|
| Developer | | | |
| Reviewer | | | |

**Notes:**
