# Public deployment — Railway API + Vercel frontend

Deploy so anyone can open a URL without you running `python -m src.api` locally.

| Service | Platform | URL example |
|---------|----------|-------------|
| **Pulse API** | Railway (this repo) | `https://pulse-api-xxx.up.railway.app` |
| **Frontend** | Vercel (`frontend/`) | `https://groww-pulse.vercel.app` |
| **MCP publish** | Railway (MCP-SERVER repo) | Already deployed — unchanged |

---

## Architecture (no Railway volume required)

```
Browser → Vercel → Railway Pulse API
                         ↑
              GitHub Actions weekly job
              (runs pipeline + POST sync)
```

GitHub Actions already runs your pipeline every Monday. After each run it **uploads** pulse data to Railway — you do **not** need Railway Volumes (often unavailable on free/hobby plans).

---

## Step 1 — Railway: create Pulse API service

1. [Railway](https://railway.com) → **New project** → **Deploy from GitHub repo**
2. Select **`Weekly_Pulse_Grow-`**
3. Name the service **`pulse-api`** (separate from MCP-SERVER)

Wait for deploy. Copy the public URL, e.g.  
`https://pulse-api-production-xxxx.up.railway.app`

Test: `https://YOUR-URL/api/health` → `"status":"ok"`

---

## Step 2 — Railway: environment variables

**pulse-api** → **Variables** → add:

| Variable | Value |
|----------|--------|
| `SYNC_SECRET` | Pick a long random password (you choose once) |
| `CORS_ORIGINS` | Add after Vercel deploy (Step 5), e.g. `https://your-app.vercel.app` |

`SYNC_SECRET` protects the sync endpoint — only GitHub Actions can push data.

**Skip Railway Volumes** — not needed with this setup.

Redeploy after adding variables.

---

## Step 3 — GitHub: add two secrets

**Settings → Secrets and variables → Actions → New repository secret**

| Secret | Value |
|--------|--------|
| `PUBLIC_PULSE_API_URL` | Your Railway pulse-api URL (no trailing slash) |
| `SYNC_SECRET` | **Same value** as on Railway |

---

## Step 4 — First data sync (one time)

Run locally after a successful pipeline on your Mac:

```bash
cd /Users/rukhsarkhan/LIP-4-4
source .venv/bin/activate

# Ensure you have fresh pulse files (or run full pipeline first)
export PUBLIC_PULSE_API_URL=https://YOUR-PULSE-API.up.railway.app
export SYNC_SECRET=your-same-secret-as-railway

python scripts/sync_public_api.py
```

Or trigger **Actions → Weekly Pulse → Run workflow** — it will sync automatically if both secrets are set.

Verify: `https://YOUR-PULSE-API.up.railway.app/api/pulse/latest` → JSON (not 404)

---

## Step 5 — Vercel: deploy frontend

1. [Vercel](https://vercel.com) → **Add New Project** → import **`Weekly_Pulse_Grow-`**
2. **Root Directory:** `frontend`
3. Environment variable:

| Name | Value |
|------|--------|
| `NEXT_PUBLIC_API_URL` | `https://YOUR-PULSE-API.up.railway.app` |

4. Deploy → copy Vercel URL

---

## Step 6 — CORS on Railway

**pulse-api** → **Variables**:

```
CORS_ORIGINS=https://your-vercel-url.vercel.app
```

Redeploy. Open your Vercel site — dashboard should show pulse data.

---

## Step 7 — Weekly updates (automatic)

Every **Monday**, GitHub Actions:

1. Runs fetch → ingest → themes → pulse → publish  
2. **Syncs** results to Railway (`sync_public_api.py`)  
3. Public site stays updated — no laptop required

Manual refresh anytime: **Actions → Weekly Pulse → Run workflow**

---

## Checklist

- [ ] Railway **pulse-api** live (`/api/health`)
- [ ] `SYNC_SECRET` on Railway + GitHub (same value)
- [ ] `PUBLIC_PULSE_API_URL` on GitHub
- [ ] First sync done (`/api/pulse/latest` works)
- [ ] Vercel deployed with `NEXT_PUBLIC_API_URL`
- [ ] `CORS_ORIGINS` on Railway includes Vercel URL

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Can't find Railway Volumes | **Ignore** — use GitHub sync (this guide) |
| `/api/pulse/latest` 404 | Run `python scripts/sync_public_api.py` locally or trigger Weekly Pulse |
| Sync failed 401/403 | `SYNC_SECRET` must match on Railway and GitHub / your terminal |
| Vercel "API not reachable" | Check `NEXT_PUBLIC_API_URL`, redeploy Vercel |
| CORS error | Add Vercel URL to `CORS_ORIGINS` on Railway |

---

## Optional: Railway volume or cron

If your Railway plan supports **Volumes**, you can mount `/app/phases` and use `bash scripts/run_pipeline_public.sh` on a cron instead of GitHub sync. The sync method above is simpler and works on all plans.
