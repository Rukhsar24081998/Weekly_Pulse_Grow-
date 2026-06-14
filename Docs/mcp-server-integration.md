# MCP Server Integration (Phase 4–5)

This project publishes to Google Workspace through a **deployed HTTP MCP server** — not through Google SDK code in `src/`.

| Item | Value |
|------|-------|
| Deployed server | https://mcp-server-rukhsar.up.railway.app |
| Source repo | https://github.com/Rukhsar24081998/MCP-SERVER |
| LIP-4-4 client | `src/publish/mcp_client.py` |

---

## Current server tools

```bash
curl https://mcp-server-rukhsar.up.railway.app/tools
```

Returns:

| Tool | Endpoint | Purpose |
|------|----------|---------|
| `append_to_doc` | `POST /append_to_doc` | Append content to an existing Google Doc |
| `create_email_draft` | `POST /create_email_draft` | Create Gmail draft (Phase 5) |

---

## Phase 4 publish flow

```bash
# 1. Validate pulse
python -m src.guardrails.validate phases/phase-3/pulse.md

# 2. Set env vars in .env
MCP_SERVER_URL=https://mcp-server-rukhsar.up.railway.app
PUBLISH_GOOGLE_DOC_ID=<existing-google-doc-id>

# 3. Publish
python -m src.publish.run
```

The CLI:

1. Re-validates pulse (fail closed)
2. Calls MCP server over HTTP (no Google SDK in repo)
3. Writes `phases/phase-4/doc_metadata.json`

### Doc title convention

`Groww App Weekly Pulse — YYYY-MM-DD` (from `config/product.yaml` → `publish.doc_title_template`)

---

## Getting a Google Doc ID

1. Create a blank Google Doc in your account (or reuse a weekly log doc).
2. Open it — URL format: `https://docs.google.com/document/d/DOC_ID/edit`
3. Copy `DOC_ID` into `.env`:

```bash
PUBLISH_GOOGLE_DOC_ID=DOC_ID
```

Each weekly run appends a new dated section via `append_to_doc`. The server may prepend a timestamp line (e.g. `[2026-06-14 11:04:17]`); LIP-4-4 sends a formatted section with its own title and separator. To remove the server timestamp, update `append_to_doc` in [MCP-SERVER](https://github.com/Rukhsar24081998/MCP-SERVER).

---

## Optional: add `create_document` to MCP server

For a **new document per week** (full Phase 4 exit criteria without a standing doc), extend [MCP-SERVER](https://github.com/Rukhsar24081998/MCP-SERVER):

### 1. Add to `docs_tool.py`

```python
def create_document(title: str, content: str):
    creds = get_creds()
    docs = build("docs", "v1", credentials=creds)
    doc = docs.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]

    docs.documents().batchUpdate(
        documentId=doc_id,
        body={
            "requests": [
                {
                    "insertText": {
                        "location": {"index": 1},
                        "text": content,
                    }
                }
            ]
        },
    ).execute()

    return {
        "status": "success",
        "document_id": doc_id,
        "document_url": f"https://docs.google.com/document/d/{doc_id}/edit",
    }
```

### 2. Add route to `server.py`

```python
class CreateDocInput(BaseModel):
    title: str
    content: str

@app.post("/create_document")
def run_create(data: CreateDocInput):
    if not approve("create_document", data.dict()):
        return {"status": "rejected", "message": "User rejected the action"}
    return create_document(title=data.title, content=data.content)
```

### 3. Register tool in `/tools`

```python
{"name": "create_document", "description": "Create a new Google Doc with title and content"}
```

### 4. Redeploy to Railway

After deploy, `python -m src.publish.run` auto-detects `create_document` and skips `PUBLISH_GOOGLE_DOC_ID`.

---

## Phase 5 — Gmail draft

```bash
# .env
DRAFT_RECIPIENT=your-email@example.com

python -m src.guardrails.validate phases/phase-3/pulse.md
python -m src.publish.draft_run
```

Or full E2E:

```bash
python -m src.publish.e2e_run
```

Creates a **draft only** — check Gmail → Drafts. Never auto-sent.

---

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MCP_SERVER_URL` | Yes (Phase 4) | Railway MCP base URL |
| `DRAFT_RECIPIENT` | Phase 5 | Gmail draft recipient (self or alias) |
| `PUBLISH_GOOGLE_DOC_ID` | Yes* | Existing doc for `append_to_doc` (*not needed if `create_document` deployed) |

Google OAuth credentials (`GOOGLE_CREDENTIALS_JSON`, `GOOGLE_TOKEN_JSON`) live on **Railway only** — never in this repo.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `MCP HTTP 403` | Check Railway env vars; refresh `GOOGLE_TOKEN_JSON` |
| `No google_doc_id available` | Set `PUBLISH_GOOGLE_DOC_ID` or deploy `create_document` |
| `VALIDATION FAILED` | Fix pulse locally; do not publish |
| Server health fails | Check Railway logs: `railway logs` |
