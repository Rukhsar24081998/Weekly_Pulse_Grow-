# Create Gmail draft with weekly pulse (Phase 5)

Use the **Railway MCP server** — draft only, **never auto-send**.

**Server:** https://mcp-server-rukhsar.up.railway.app  
**Endpoint:** `POST /create_email_draft`

---

## Prerequisites

1. Phase 3 pulse validated (`validation_passed: true`)
2. Phase 4 doc published (optional but recommended — link included in email body)
3. `.env` configured:
   ```bash
   MCP_SERVER_URL=https://mcp-server-rukhsar.up.railway.app
   DRAFT_RECIPIENT=your-email@example.com
   ```

---

## Option A — CLI (recommended)

```bash
source .venv/bin/activate

python -m src.guardrails.validate phases/phase-3/pulse.md
python -m src.publish.draft_run

# Or override recipient
python -m src.publish.draft_run --to you@example.com

# Full E2E (Doc + draft + run.json)
python -m src.publish.e2e_run
```

Output: `phases/phase-5/run.json` with `gmail_draft_id`.

---

## Option B — Cursor agent

### 1. Confirm validation passed

```bash
python -m src.guardrails.validate phases/phase-3/pulse.md
```

Stop if exit code ≠ 0.

### 2. Build email

| Field | Value |
|-------|-------|
| **To** | `DRAFT_RECIPIENT` from `.env` (self or alias only) |
| **Subject** | `Weekly App Review Pulse — Groww App — YYYY-MM-DD` |
| **Body** | Google Doc link + full pulse markdown |

### 3. Call MCP

```http
POST /create_email_draft
{
  "to": "your-email@example.com",
  "subject": "Weekly App Review Pulse — Groww App — 2026-06-13",
  "body": "<pulse text + doc link>"
}
```

Or run `python -m src.publish.draft_run`.

### 4. Verify in Gmail

- Open **Gmail → Drafts**
- Confirm recipient, subject, and body
- **Do not send automatically** — operator reviews and sends manually

### 5. Record metadata

Ensure `phases/phase-5/run.json` contains `gmail_draft_id` and `google_doc_id`.

---

## Fail-closed rules

- Invalid pulse → no MCP call
- Missing `DRAFT_RECIPIENT` → blocked with clear error
- **Never** call send-mail tools — draft only (ADR-011)

---

## Re-run same week

Each run creates a **new draft**. Google Doc appends a new section (Phase 4). Operator may delete old drafts manually.
