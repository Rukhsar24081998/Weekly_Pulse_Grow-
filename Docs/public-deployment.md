# Public deployment — Render API + Vercel frontend

Deploy so anyone can open a URL without you running `python -m src.api` locally.

| Service | Platform | URL example |
|---------|----------|-------------|
| **Pulse API** | Render (this repo) | `https://pulse-api-xxxx.onrender.com` |
| **Frontend** | Vercel (`frontend/`) | `https://weekly-pulse-grow.vercel.app` |
| **MCP publish** | Separate MCP-SERVER deploy | Unchanged — set `MCP_SERVER_URL` |

### Is Render free?

**Yes.** Free web services are **$0/month** (no credit card required to start). Limits:

| Limit | What it means for pulse-api |
|-------|-----------------------------|
| Spins down after **15 min** idle | First request after sleep can take ~1 minute |
| **750** free instance hours / month | Enough for one always-warm service if you ping it |
| No persistent disk on free | Redeploy **or** spin-down clears synced `phases/` files |

**Practical tip:** After deploy, run a sync (Step 4). If the site shows empty data after idle time, re-run sync or trigger **Weekly Pulse**. For always-on (no cold starts / less data loss), upgrade the service to **Starter (~$7/mo)**.

---

## Architecture (no persistent volume required)

```
Browser → Vercel → Render Pulse API
                         ↑
              GitHub Actions weekly job
              (runs pipeline + POST sync)
```

GitHub Actions already runs your pipeline every Monday. After each run it **uploads** pulse data to Render — you do **not** need a disk volume.

---

## Step 1 — Render: create Pulse API service

1. [Render](https://render.com) → **New** → **Blueprint** (uses `render.yaml`)  
   **or** **New** → **Web Service** → connect **`Weekly_Pulse_Grow-`**
2. If manual Web Service:
   - **Runtime:** Docker
   - **Dockerfile path:** `./Dockerfile`
   - **Instance type:** Free
   - **Health check path:** `/api/health`
3. Name the service **`pulse-api`**

Wait for deploy. Copy the public URL, e.g.  
`https://pulse-api-xxxx.onrender.com`

Test: `https://YOUR-URL/api/health` → `"status":"ok"`  
(First hit on free tier may take ~1 minute while the service wakes up.)

---

## Step 2 — Render: environment variables

**pulse-api** → **Environment** → add:

| Variable | Value |
|----------|--------|
| `SYNC_SECRET` | Pick a long random password (you choose once) |
| `CORS_ORIGINS` | Add after Vercel is set (Step 5), e.g. `https://weekly-pulse-grow.vercel.app` |

`SYNC_SECRET` protects the sync endpoint — only GitHub Actions (or you) can push data.

`PORT` is set automatically by Render — do not override.

Redeploy after adding variables.

---

## Step 3 — GitHub: add two secrets

**Settings → Secrets and variables → Actions → New repository secret**

| Secret | Value |
|--------|--------|
| `PUBLIC_PULSE_API_URL` | Your Render pulse-api URL (no trailing slash) |
| `SYNC_SECRET` | **Same value** as on Render |

---

## Step 4 — First data sync (one time)

Run locally after a successful pipeline on your Mac:

```bash
cd /Users/rukhsarkhan/Projects/Weekly_Pulse_Grow-
source .venv/bin/activate

# Ensure you have fresh pulse files (or run full pipeline first)
export PUBLIC_PULSE_API_URL=https://YOUR-PULSE-API.onrender.com
export SYNC_SECRET=your-same-secret-as-render

python scripts/sync_public_api.py
```

Or trigger **Actions → Weekly Pulse → Run workflow** — it will sync automatically if both secrets are set.

Verify: `https://YOUR-PULSE-API.onrender.com/api/pulse/latest` → JSON (not 404)

---

## Step 5 — Vercel: deploy frontend

1. [Vercel](https://vercel.com) → project for **`Weekly_Pulse_Grow-`** (or import fresh)
2. **Root Directory:** `frontend`
3. Environment variable:

| Name | Value |
|------|--------|
| `NEXT_PUBLIC_API_URL` | `https://YOUR-PULSE-API.onrender.com` |

4. Redeploy → open the Vercel URL

If the site already exists at [weekly-pulse-grow.vercel.app](https://weekly-pulse-grow.vercel.app), only update `NEXT_PUBLIC_API_URL` and redeploy.

---

## Step 6 — CORS on Render

**pulse-api** → **Environment**:

```
CORS_ORIGINS=https://weekly-pulse-grow.vercel.app
```

Redeploy. Open your Vercel site — dashboard should show pulse data.

---

## Step 7 — Weekly updates (automatic)

Every **Monday**, GitHub Actions:

1. Runs fetch → ingest → themes → pulse → publish  
2. **Syncs** results to Render (`sync_public_api.py`)  
3. Public site stays updated — no laptop required

Manual refresh anytime: **Actions → Weekly Pulse → Run workflow**

---

## Checklist

- [ ] Render **pulse-api** live (`/api/health`)
- [ ] `SYNC_SECRET` on Render + GitHub (same value)
- [ ] `PUBLIC_PULSE_API_URL` on GitHub = Render URL
- [ ] First sync done (`/api/pulse/latest` works)
- [ ] Vercel `NEXT_PUBLIC_API_URL` points at Render
- [ ] `CORS_ORIGINS` on Render includes Vercel URL
- [ ] Old Railway pulse-api project deleted / unused

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| First request hangs / 502 | Free tier cold start — wait ~1 min and retry |
| `/api/pulse/latest` 404 | Run `python scripts/sync_public_api.py` or trigger Weekly Pulse |
| Empty dashboard after idle | Free spin-down cleared disk — re-sync, or upgrade to Starter |
| Sync failed 401/403 | `SYNC_SECRET` must match on Render and GitHub / your terminal |
| Vercel "API not reachable" | Check `NEXT_PUBLIC_API_URL`, redeploy Vercel |
| CORS error | Add Vercel URL to `CORS_ORIGINS` on Render |

---

## Optional: paid instance or keepalive

- **Starter (~$7/mo):** service stays up; fewer cold starts; synced files last until the next deploy.
- **Keepalive:** a cron that hits `/api/health` every ~10 minutes can reduce free-tier sleep (uses free instance hours).
