# Weekly App Review Pulse — Groww App

Turn public **App Store** and **Play Store** reviews for the **Groww App** into a scannable weekly pulse — published to **Google Docs** and a **Gmail draft** via MCP in Cursor.

**LIP 4** · Milestone 1 product: **Groww** (iOS + Android)

---

## Constraints (non-negotiable)

| Constraint | Value |
|------------|-------|
| Review sources | Public store exports only — no login scraping |
| Theme clustering | ≤ 5 themes per run |
| Weekly pulse | Top 3 themes, 3 quotes, 3 action ideas |
| Word limit | ≤ 250 words |
| PII | None in any artifact (ingest drops identity; output redacted) |
| Google integration | **MCP only** — no Google SDK in application code |
| Email | Gmail **draft** only — operator sends manually |

---

## Product

| Field | Value |
|-------|-------|
| App | Groww App |
| Stores | Apple App Store, Google Play Store |
| Default review window | **12 weeks** (max allowed; configurable 8–12) |
| Theme taxonomy | `config/themes.yaml` |

---

## Repository layout

```
LIP-4-4/
├── config/           # product.yaml (incl. deliverables paths), themes.yaml
├── data/raw/         # Shared inputs only — store CSV exports
├── phases/           # Each phase keeps its own outputs
│   ├── phase-0/      # reports, fetch_metadata, storage_validation
│   ├── phase-1/      # reviews.json
│   ├── phase-2/      # themes.json
│   ├── phase-3/      # pulse.md, pulse.json
│   ├── phase-4/      # doc_metadata.json
│   ├── phase-5/      # run.json
│   └── phase-6/      # signoff_report.json
├── prompts/          # Agent prompts (Phases 4–5)
├── src/              # Pipeline code by phase
├── tests/
└── Docs/
```

---

## Setup

### 1. Python environment

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
```

Requires **Python 3.10+**.

```bash
source .venv/bin/activate
python -m src.themes.run
```

Or use `./scripts/run_themes.sh` without activating the venv.

### 2. Environment variables (`.env`)

For Groq (Phase 2 hybrid themes), copy the template and add your key:

```bash
cp .env.example .env
# Edit .env — set GROQ_API_KEY=your_key_here
```

`.env` is gitignored. Google MCP credentials stay in `~/.cursor/mcp.json`, not in `.env`.

### 3. MCP (Google Docs + Gmail)

Phase 4–5 use the **Railway MCP server** (HTTP) — see [Docs/mcp-server-integration.md](Docs/mcp-server-integration.md).

```bash
# .env
MCP_SERVER_URL=https://mcp-server-rukhsar.up.railway.app
PUBLISH_GOOGLE_DOC_ID=<your-google-doc-id>
```

Server repo: [Rukhsar24081998/MCP-SERVER](https://github.com/Rukhsar24081998/MCP-SERVER)

For Cursor-native MCP (`@a-bonus/google-docs-mcp`), see [.cursor/mcp.json.example](.cursor/mcp.json.example).

### 4. Review exports (download and store)

Download **8–12 weeks** from App Store Connect and Play Console, then save to `data/raw/`:

| File | Store |
|------|-------|
| `groww_app_store_reviews.csv` | App Store Connect |
| `groww_play_store_reviews.csv` | Play Console |

```bash
source .venv/bin/activate
python scripts/validate_raw_exports.py          # after placing downloads
python scripts/validate_raw_exports.py --weeks 12
```

Dev fallback (no console): `python scripts/fetch_public_reviews.py`

Details: [Docs/review-export-formats.md](Docs/review-export-formats.md) · [data/raw/README.md](data/raw/README.md)

### Before Phase 1

```bash
python scripts/build_test_fixtures.py
python scripts/pre_phase1_check.py
```

### Phase 1 — ingest reviews

```bash
source .venv/bin/activate
python -m src.ingest.run              # default 12 weeks
python -m src.ingest.run --weeks 10   # optional window override
python -m src.ingest.run --help
pytest tests/test_phase1_ingest.py
```

Output: `phases/phase-1/reviews.json`

### Phase 2 — theme clustering

```bash
python -m src.themes.run
pytest tests/test_phase2_themes.py
```

Output: `phases/phase-2/themes.json`

### Phase 3 — pulse generation

```bash
python -m src.pulse.run
pytest tests/test_phase3_pulse.py
```

Output: `phases/phase-3/pulse.md`, `phases/phase-3/pulse.json`

### Phase 4 — publish to Google Doc

```bash
python -m src.guardrails.validate phases/phase-3/pulse.md
python -m src.publish.run --doc-id YOUR_GOOGLE_DOC_ID
pytest tests/test_phase4_publish.py
```

Output: `phases/phase-4/doc_metadata.json` with `google_doc_id`

### Phase 5 — Gmail draft + E2E

```bash
# Set DRAFT_RECIPIENT=your-email@example.com in .env
python -m src.publish.draft_run              # draft only
python -m src.publish.e2e_run                # Doc + draft + run.json
pytest tests/test_phase5_draft.py
```

Output: `phases/phase-5/run.json` with `gmail_draft_id` (draft **not** auto-sent)

See [Docs/mcp-server-integration.md](Docs/mcp-server-integration.md), [prompts/publish-doc.md](prompts/publish-doc.md), and [prompts/draft-email.md](prompts/draft-email.md).

Replace App Store raw with a 12-week Connect export when available — see [data/raw/APP_STORE_EXPORT_NEEDED.md](data/raw/APP_STORE_EXPORT_NEEDED.md).

---

## Weekly workflow (full build — Phases 1–5)

```
1. Drop latest Play Store export in data/raw/ (App Store optional)
2. `python -m src.ingest.run --weeks 12` → themes → pulse (Phases 1–3)
3. `python -m src.guardrails.validate phases/phase-3/pulse.md`
4. `python -m src.publish.e2e_run` (Phase 4 doc + Phase 5 draft)
5. Review Google Doc and Gmail draft manually; send email when ready
```

Detailed runbook: [Docs/phase-wise-implementationplan.md](Docs/phase-wise-implementationplan.md)

---

## Documentation

| Document | Purpose |
|----------|---------|
| [Docs/ProblemStatement.md](Docs/ProblemStatement.md) | Requirements |
| [Docs/architecture.md](Docs/architecture.md) | System design |
| [Docs/phase-wise-implementationplan.md](Docs/phase-wise-implementationplan.md) | Phase plan |
| [Docs/decision.md](Docs/decision.md) | Architecture decision log |
| [Docs/phases/](Docs/phases/) | Per-phase evaluation criteria |

---

## Phase status

| Phase | Name | Status |
|-------|------|--------|
| 0 | Foundation & Planning | Complete |
| 1 | Review Ingestion | **Complete** |
| 2 | Theme Clustering | **Complete** |
| 3 | Pulse & Guardrails | **Complete** |
| 4 | Google Docs via MCP | **Complete** |
| 5 | Gmail Draft & E2E | **Complete** |
| 6 | Validation & Hardening | **Complete** |

---

## GitHub Actions

| Workflow | When | What |
|----------|------|------|
| **CI** | Every push to `main` | Full `pytest` suite |
| **Weekly Pulse** | Monday 09:00 IST | Fetch → pipeline → Google Doc + Gmail draft |

Setup: [Docs/github-actions.md](Docs/github-actions.md) — add 4 repository secrets, then **Actions → Weekly Pulse → Run workflow** to test.

---

## Known limitations

- **App Store RSS** caps at ~500 reviews per country (~1–2 weeks); full 12-week iOS needs App Store Connect export
- **Groq** free tier may rate-limit; GitHub Actions weekly job uses `--no-groq` by default
- **GitHub Actions** weekly run creates Gmail **draft only** — operator sends manually
- MCP OAuth lives on **Railway** (`MCP_SERVER_URL`), not in repo secrets beyond the URL/doc ID
- Export column formats may differ — update `Docs/review-export-formats.md` if parsers fail
