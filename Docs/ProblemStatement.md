# Weekly App Review Pulse (LIP 4)

## Problem Statement

Pick the **same product you selected in Milestone 1** (mobile app on iOS and Android — **Groww App**). Product, growth, support, and leadership teams need a fast way to understand what users are saying in public store reviews without manually reading hundreds of posts each week.

Turn recent **App Store** and **Play Store** reviews into a **one-page weekly pulse** that summarizes user sentiment and suggests next steps. The weekly pulse must contain:

- **Top themes** — what users talk about most
- **Real user quotes** — anonymized, no PII
- **Three action ideas** — concrete follow-ups for product or support

Finally, **draft an email to yourself** (or an alias) containing the weekly note so it is ready to review and send.

Deliver the note through **Google Workspace using MCP servers in Cursor** — not custom Google API integrations in application code.

---

## Who This Helps

| Audience | Value |
|----------|-------|
| **Product / Growth** | Understand what to fix or improve next |
| **Support** | Know what users are saying and what to acknowledge |
| **Leadership** | Get a quick weekly health pulse without reading raw reviews |

---

## End-to-End Workflow

1. **Ingest** public App Store and Play Store review exports from the last **8–12 weeks** (rating, title, text, date).
2. **Analyze** reviews and cluster them into **at most 5 themes** (e.g., onboarding, KYC, payments, statements, withdrawals).
3. **Generate** a scannable one-page weekly note (≤ 250 words) with:
   - Top **3** themes
   - **3** representative user quotes
   - **3** action ideas
4. **Publish** the note to **Google Docs** via the configured Google Workspace MCP server.
5. **Draft** a Gmail message to yourself (or alias) with the weekly note via the same MCP server.

---

## What You Must Build

- Import reviews from the last 8–12 weeks (rating, title, text, date).
- Group reviews into **≤ 5 themes**.
- Generate a weekly one-page note with top 3 themes, 3 user quotes, and 3 action ideas.
- Create or update a **Google Doc** containing the note using **MCP tools only**.
- Create a **Gmail draft** (to yourself/alias) with the note using **MCP tools only**.
- Do **not** include PII in any artifact.

---

## Integration Requirements: MCP, Not APIs

**Do not** implement direct Google API integration in your application code. That means:

- No `google-api-python-client`, `googleapis`, or similar SDKs
- No custom OAuth flows, service accounts, or credential files in the repo
- No REST calls to `googleapis.com` from scripts or app code

**Do** use a **Google Workspace MCP server** configured in Cursor. The agent invokes MCP tools; the MCP server handles authentication and Google API access on your behalf.

### Recommended MCP server

Use **`@a-bonus/google-docs-mcp`** (or an equivalent Google Docs + Gmail MCP server) in Cursor MCP settings:

```json
{
  "mcpServers": {
    "google-docs": {
      "command": "npx",
      "args": ["-y", "@a-bonus/google-docs-mcp"],
      "env": {
        "GOOGLE_CLIENT_ID": "your-client-id",
        "GOOGLE_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

### Required MCP capabilities

| Step | MCP surface | Example tool intent |
|------|-------------|---------------------|
| Weekly note | **Google Docs** | Create a document and write/append the pulse content |
| Email draft | **Gmail** | Create a draft addressed to you (or alias) with subject + body |

Relevant Gmail tools include `createDraft`, `updateDraft`, and `listDrafts`. Docs tools include `createDocument` and document write/update operations exposed by the server.

### MCP setup (one-time)

1. Enable Google Docs, Drive, and Gmail APIs in Google Cloud Console and create an OAuth Desktop client.
2. Add the MCP server to Cursor (`~/.cursor/mcp.json` or project-level config).
3. Complete OAuth when prompted on first tool use (credentials stay with the MCP server, not in the repo).
4. Verify Docs and Gmail tools are available before building the automation.

---

## Key Constraints

- **Public review exports only** — no scraping behind logins or paywalls.
- **Max 5 themes** when clustering reviews.
- **≤ 250 words** for the weekly note; keep it scannable.
- **No PII** — no usernames, emails, account IDs, phone numbers, or other identifiers in the doc, draft, or any exported artifact.
- **MCP-only Google integration** — Docs and Gmail must go through the configured MCP server, not application-level API code.

---

## Product Context (from Milestone 1)

| Field | Value |
|-------|-------|
| Product | **Groww App** — Groww (stocks, mutual funds, IPO) on iOS and Android |
| Review sources | Apple App Store, Google Play Store |
| Example themes | Onboarding, KYC, payments, statements, withdrawals, login, discovery, performance (`config/themes.yaml`) |

Product locked in Phase 0 — see [decision.md](./decision.md) ADR-002.

---

## Deliverables

1. **Review ingestion** — pipeline that loads 8–12 weeks of public store reviews.
2. **Theme analysis + pulse generation** — logic that produces the structured weekly note.
3. **Google Doc** — created/updated via MCP with the final pulse.
4. **Gmail draft** — created via MCP to yourself/alias (ready to review in Gmail).
5. **README** — setup, MCP configuration, how to run the workflow, and known limitations.

---

## Success Criteria

- Reviews from both stores are ingested and themed correctly (≤ 5 themes).
- Weekly note is concise (≤ 250 words), includes top 3 themes, 3 quotes, and 3 action ideas.
- Google Doc and Gmail draft are produced **only through MCP tools**, with no direct Google API code in the project.
- No PII appears in any output.
- A teammate can reproduce the run using the README and a configured MCP server.
