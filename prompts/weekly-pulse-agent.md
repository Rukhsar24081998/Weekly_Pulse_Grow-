# Weekly pulse — end-to-end agent workflow (Phase 5)

Orchestrates the full weekly run for **Groww App** using the Railway MCP server.

**MCP:** https://mcp-server-rukhsar.up.railway.app

---

## Constraints (non-negotiable)

- Public store exports only
- ≤ 5 themes, ≤ 250 words, 3/3/3 pulse structure
- No PII in any artifact
- MCP-only Google (no Google SDK in repo)
- Gmail **draft only** — never auto-send

---

## Operator checklist

```
[ ] Play Store export in data/raw/groww_play_store_reviews.csv
[ ] .env: GROQ_API_KEY, MCP_SERVER_URL, PUBLISH_GOOGLE_DOC_ID, DRAFT_RECIPIENT
[ ] python -m src.ingest.run --weeks 12
[ ] python -m src.themes.run
[ ] python -m src.pulse.run
[ ] python -m src.guardrails.validate phases/phase-3/pulse.md
[ ] python -m src.publish.e2e_run
[ ] Open Google Doc — verify pulse content
[ ] Open Gmail Drafts — verify draft; send manually if ready
[ ] Confirm phases/phase-5/run.json complete
```

---

## Step-by-step

### 1. Pipeline (Phases 1–3)

```bash
source .venv/bin/activate
python -m src.ingest.run --weeks 12
python -m src.themes.run
python -m src.pulse.run
```

Outputs: `phases/phase-1/reviews.json`, `phases/phase-2/themes.json`, `phases/phase-3/pulse.md`

### 2. Validate (mandatory gate)

```bash
python -m src.guardrails.validate phases/phase-3/pulse.md
```

If validation fails, fix pulse locally. **Do not publish.**

### 3. Publish (Phases 4 + 5)

```bash
python -m src.publish.e2e_run
```

This runs:

1. Google Doc publish → `phases/phase-4/doc_metadata.json`
2. Gmail draft → `phases/phase-5/run.json`

Or run separately:

```bash
python -m src.publish.run
python -m src.publish.draft_run
```

### 4. Operator review

- **Google Doc:** [link in doc_metadata.json]
- **Gmail:** Drafts folder — review recipient, subject, body
- **Send manually** when ready

---

## Recovery

| Failure | Action |
|---------|--------|
| Pipeline fails | Fix data; re-run from failed stage. No MCP calls. |
| Doc OK, draft fails | `python -m src.publish.draft_run` only |
| Draft OK, doc missing | `python -m src.publish.run` only |
| MCP auth error | Refresh Railway `GOOGLE_TOKEN_JSON`; retry |

---

## Re-run same week

- **Google Doc:** appends a new dated section to the same doc
- **Gmail:** creates a new draft each run
- Operator may archive/delete old drafts

---

## Prompts

- Docs only: [publish-doc.md](./publish-doc.md)
- Draft only: [draft-email.md](./draft-email.md)

Plan: [Docs/phase-wise-implementationplan.md](../Docs/phase-wise-implementationplan.md)
