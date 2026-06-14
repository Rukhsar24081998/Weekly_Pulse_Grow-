# Publish weekly pulse to Google Doc (Phase 4)

Use the **Railway MCP server** — no Google SDK in this repository. All Google API calls happen on the server.

**Server:** https://mcp-server-rukhsar.up.railway.app  
**Source:** https://github.com/Rukhsar24081998/MCP-SERVER

---

## Prerequisites

1. Phase 3 pulse validated (`phases/phase-3/pulse.json` → `validation_passed: true`).
2. `.env` configured:
   ```bash
   MCP_SERVER_URL=https://mcp-server-rukhsar.up.railway.app
   PUBLISH_GOOGLE_DOC_ID=<your-google-doc-id>   # required until create_document is deployed
   ```
3. MCP server health check returns `200`:
   ```bash
   curl https://mcp-server-rukhsar.up.railway.app/
   ```

---

## Option A — CLI publish (recommended)

```bash
source .venv/bin/activate

# Pre-flight validation
python -m src.guardrails.validate phases/phase-3/pulse.md

# Publish via MCP HTTP server
python -m src.publish.run --doc-id YOUR_GOOGLE_DOC_ID

# Or rely on PUBLISH_GOOGLE_DOC_ID in .env
python -m src.publish.run
```

Output: `phases/phase-4/doc_metadata.json` with `google_doc_id` and `google_doc_url`.

---

## Option B — Cursor agent publish

Follow these steps **only after** validation passes. Stop immediately if validation fails.

### 1. Read artifacts

- `phases/phase-3/pulse.md` — full pulse body
- `phases/phase-3/pulse.json` — confirm `validation_passed: true`

### 2. Confirm guardrails

Run:

```bash
python -m src.guardrails.validate phases/phase-3/pulse.md
```

Exit code must be `0`. Do **not** call MCP if validation fails.

### 3. Build doc title

Format: **`Groww App Weekly Pulse — YYYY-MM-DD`**

Use `week_ending` from `pulse.json` for the date.

### 4. Publish via MCP server

**If `create_document` is available** on the server (`GET /tools`):

```http
POST /create_document
{
  "title": "Groww App Weekly Pulse — 2026-06-13",
  "content": "<full pulse markdown with title header>"
}
```

**Otherwise** (current server — `append_to_doc` only):

```http
POST /append_to_doc
{
  "doc_id": "<PUBLISH_GOOGLE_DOC_ID>",
  "content": "# Groww App Weekly Pulse — 2026-06-13\n\n<pulse.md contents>"
}
```

Or run `python -m src.publish.run` which handles this automatically.

### 5. Verify in browser

Open the Google Doc URL. Confirm:

- [ ] Title matches convention
- [ ] 3 themes, 3 quotes, 3 actions present
- [ ] Word count ≤ 250 (pulse body)
- [ ] No PII visible

### 6. Record metadata

Ensure `phases/phase-4/doc_metadata.json` contains:

```json
{
  "google_doc_id": "...",
  "google_doc_url": "https://docs.google.com/document/d/.../edit",
  "doc_title": "Groww App Weekly Pulse — YYYY-MM-DD",
  "validation_passed": true
}
```

---

## Fail-closed rules

- Invalid pulse → **no MCP calls**
- MCP auth/server error → pulse stays safe on disk; retry after fixing server
- Never import or use Google SDK in this repo

---

## Upgrading MCP server (optional)

To create a **new doc each week** (instead of appending to one doc), add `POST /create_document` to [MCP-SERVER](https://github.com/Rukhsar24081998/MCP-SERVER). See [Docs/mcp-server-integration.md](../Docs/mcp-server-integration.md).
