# Phase 4 — Google Docs via MCP

**Product:** Groww App  
**Status:** Complete (HTTP MCP client + publish CLI)  
**Depends on:** Phase 3  
**Eval:** [Docs/phases/phase-4/eval.md](../Docs/phases/phase-4/eval.md)

## Purpose

Publish the validated pulse to Google Docs using the **Railway MCP server** — no Google SDK in `src/`.

## MCP server

| Item | Value |
|------|-------|
| URL | https://mcp-server-rukhsar.up.railway.app |
| Repo | https://github.com/Rukhsar24081998/MCP-SERVER |
| Tools | `append_to_doc`, `create_email_draft` (+ optional `create_document`) |

## Work in this phase

| Area | Module | Output |
|------|--------|--------|
| Preflight | `src/publish/preflight.py` | Blocks invalid pulse before MCP |
| MCP client | `src/publish/mcp_client.py` | HTTP calls to Railway server |
| Publish CLI | `src/publish/run.py` | `phases/phase-4/doc_metadata.json` |
| Agent prompt | `prompts/publish-doc.md` | Docs publish runbook |
| Tests | `tests/test_phase4_publish.py` | 10 tests |

## Run

```bash
source .venv/bin/activate

# Validate pulse first (mandatory gate)
python -m src.guardrails.validate phases/phase-3/pulse.md

# Publish — set PUBLISH_GOOGLE_DOC_ID in .env or pass --doc-id
python -m src.publish.run --doc-id YOUR_GOOGLE_DOC_ID

pytest tests/test_phase4_publish.py
```

## Doc naming

`Groww App Weekly Pulse — YYYY-MM-DD`

## Prerequisites

- Validated pulse from Phase 3
- `MCP_SERVER_URL` in `.env` (defaults to Railway URL in `config/product.yaml`)
- `PUBLISH_GOOGLE_DOC_ID` for append mode, **or** deploy `create_document` on MCP server

Integration guide: [Docs/mcp-server-integration.md](../Docs/mcp-server-integration.md)

← [Phase 3](../phase-3/README.md) · → [Phase 5](../phase-5/README.md)
