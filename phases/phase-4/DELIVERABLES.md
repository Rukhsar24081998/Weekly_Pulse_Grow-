# Phase 4 deliverables

| Artifact | Description |
|----------|-------------|
| `doc_metadata.json` | Run metadata with `google_doc_id`, `google_doc_url`, `doc_title` |
| `src/publish/` | MCP HTTP client + publish pipeline (no Google SDK) |
| `prompts/publish-doc.md` | Agent runbook for Docs publish |
| `tests/test_phase4_publish.py` | Phase 4 unit tests |

## Run

```bash
source .venv/bin/activate
python -m src.guardrails.validate phases/phase-3/pulse.md
python -m src.publish.run --doc-id YOUR_GOOGLE_DOC_ID
pytest tests/test_phase4_publish.py
```

See [Docs/mcp-server-integration.md](../../Docs/mcp-server-integration.md) for MCP server setup.
