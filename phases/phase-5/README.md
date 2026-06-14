# Phase 5 — Gmail Draft & E2E Orchestration

**Product:** Groww App  
**Status:** Complete  
**Depends on:** Phase 4  
**Eval:** [Docs/phases/phase-5/eval.md](../Docs/phases/phase-5/eval.md)

## Purpose

Create a Gmail **draft** via MCP (not sent automatically) and wire the full weekly workflow into one runbook.

## MCP server

| Item | Value |
|------|-------|
| URL | https://mcp-server-rukhsar.up.railway.app |
| Tool | `POST /create_email_draft` |

## Work in this phase

| Area | Module | Output |
|------|--------|--------|
| Draft pipeline | `src/publish/draft_pipeline.py` | Gmail draft via MCP |
| E2E orchestration | `src/publish/e2e_pipeline.py` | Doc + draft in one run |
| Run metadata | `src/publish/run_metadata.py` | `phases/phase-5/run.json` |
| Draft CLI | `src/publish/draft_run.py` | Create draft only |
| E2E CLI | `src/publish/e2e_run.py` | Phase 4 + 5 together |
| Prompts | `prompts/draft-email.md`, `prompts/weekly-pulse-agent.md` | Operator runbooks |

## Email conventions

| Field | Value |
|-------|-------|
| **Subject** | `Weekly App Review Pulse — Groww App — YYYY-MM-DD` |
| **Recipient** | `DRAFT_RECIPIENT` in `.env` |
| **Body** | Google Doc link + full pulse markdown |
| **Send** | Manual only — draft is never auto-sent |

## Run

```bash
source .venv/bin/activate

# Set in .env
DRAFT_RECIPIENT=your-email@example.com

python -m src.guardrails.validate phases/phase-3/pulse.md
python -m src.publish.draft_run          # Phase 5 only
python -m src.publish.e2e_run            # Phase 4 + 5

pytest tests/test_phase5_draft.py
```

## Prerequisites

- Validated pulse from Phase 3
- Phase 4 doc metadata (recommended — link in email body)
- `DRAFT_RECIPIENT` in `.env`

← [Phase 4](../phase-4/README.md) · → [Phase 6](../phase-6/README.md)
