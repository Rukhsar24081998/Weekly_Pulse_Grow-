# Phase 5 deliverables

| Artifact | Description |
|----------|-------------|
| `run.json` | Full run metadata with `gmail_draft_id`, `google_doc_id`, themes, word count |
| `src/publish/draft_pipeline.py` | Gmail draft via MCP HTTP |
| `src/publish/e2e_pipeline.py` | Phase 4+5 orchestration |
| `prompts/draft-email.md` | Gmail MCP runbook |
| `prompts/weekly-pulse-agent.md` | Full E2E operator checklist |
| `tests/test_phase5_draft.py` | Phase 5 unit tests |

## Run

```bash
source .venv/bin/activate

# .env
DRAFT_RECIPIENT=your-email@example.com

python -m src.guardrails.validate phases/phase-3/pulse.md
python -m src.publish.draft_run
python -m src.publish.e2e_run   # Doc + draft together

pytest tests/test_phase5_draft.py
```

Draft is **not sent automatically** — review in Gmail before sending.
