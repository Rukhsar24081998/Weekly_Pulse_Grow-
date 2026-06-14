# GitHub Actions

Automated CI and weekly pulse scheduling for [Weekly_Pulse_Grow-](https://github.com/Rukhsar24081998/Weekly_Pulse_Grow-).

## Workflows

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| **CI** | `.github/workflows/ci.yml` | Push / PR to `main` | Run full `pytest` suite + no-Google-SDK grep |
| **Weekly Pulse** | `.github/workflows/weekly-pulse.yml` | Every **Monday 09:00 IST** + manual | Fetch → ingest → themes → pulse → publish |

## Required repository secrets

Settings → **Secrets and variables → Actions → Repository secrets**

Use these **exact names** (case-sensitive):

| Secret | Purpose | Example |
|--------|---------|---------|
| `MCP_SERVER_URL` | Railway MCP server | `https://mcp-server-rukhsar.up.railway.app` |
| `PUBLISH_GOOGLE_DOC_ID` | Google Doc for append | your doc ID from the URL |
| `DRAFT_RECIPIENT` | Gmail draft recipient |

### Public UI sync (Railway pulse-api)

| Secret | Purpose |
|--------|---------|
| `PUBLIC_PULSE_API_URL` | Railway pulse-api base URL |
| `SYNC_SECRET` | Same as `SYNC_SECRET` on Railway — pushes pulse data after weekly run | `you@example.com` |
| `GROQ_API_KEY` | Optional Groq themes (manual run with `use_groq=true`) | from console.groq.com |

Do **not** use placeholder names like `SECA` — the workflow reads the names above exactly.

## Weekly schedule

```yaml
cron: "30 3 * * 1"   # Monday 03:30 UTC = 09:00 IST
```

### What each weekly run does

1. `python scripts/fetch_public_reviews.py --weeks 12`
2. `python -m src.ingest.run --weeks 12`
3. `python -m src.themes.run --no-groq` (default — reliable in CI)
4. `python -m src.pulse.run`
5. `python -m src.guardrails.validate`
6. `python -m src.publish.e2e_run` (Google Doc + Gmail draft)
7. `python scripts/phase6_signoff.py`

Artifacts (pulse, run metadata, sign-off) are uploaded for **30 days** under Actions → workflow run → **Artifacts**.

## Manual run

1. Go to **Actions** → **Weekly Pulse** → **Run workflow**
2. Options:
   - **use_groq:** `true` to enable Groq (may hit rate limits)
   - **publish:** `false` to skip MCP publish (pipeline only)

## Local equivalent

```bash
source .venv/bin/activate
python scripts/fetch_public_reviews.py --weeks 12
python -m src.ingest.run --weeks 12
python -m src.themes.run --no-groq
python -m src.pulse.run
python -m src.guardrails.validate phases/phase-3/pulse.md
python -m src.publish.e2e_run
python scripts/phase6_signoff.py
```

## Limitations

- Groq free tier often rate-limits CI — weekly job defaults to **rules-only** themes
- App Store RSS still caps at ~500 reviews (~1–2 weeks)
- Gmail draft is **never auto-sent** — review in Gmail manually
- MCP OAuth is on Railway, not in GitHub secrets
