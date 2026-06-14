# Public deployment — Railway API + Vercel frontend

Deploy so anyone can open a URL without you running `python -m src.api` locally.

| Service | Platform | URL example |
|---------|----------|-------------|
| **Pulse API** | Railway (this repo) | `https://pulse-api-xxx.up.railway.app` |
| **Frontend** | Vercel (`frontend/`) | `https://groww-pulse.vercel.app` |
| **MCP publish** | Railway (MCP-SERVER repo) | Already deployed — unchanged |

---

## Architecture

```
Browser → Vercel (Next.js) → Railway Pulse API → phases/ volume
                                    ↑
                          weekly cron / manual script
GitHub Actions (optional) → MCP publish only
```

---

## Step 1 — Railway: create Pulse API service

1. Open [Railway](https://railway.com) → **New project** → **Deploy from GitHub repo**
2. Select **`Weekly_Pulse_Grow-`** (this repo)
3. Name the service **`pulse-api`** (keep MCP in a **separate** project/service)

Railway detects `Dockerfile` + `railway.toml` automatically.

---

## Step 2 — Railway: persistent volume (important)

Without a volume, pulse data is lost on every redeploy.

1. Service **pulse-api** → **Settings** → **Volumes**
2. **Add volume** → mount path: **`/app/phases`**
3. Redeploy the service

---

## Step 3 — Railway: environment variables

Service **pulse-api** → **Variables**:

| Variable | Value |
|----------|--------|
| `CORS_ORIGINS` | Your Vercel URL (add after Step 5), e.g. `https://groww-pulse.vercel.app` |
| `MCP_SERVER_URL` | `https://mcp-server-rukhsar.up.railway.app` |
| `PUBLISH_GOOGLE_DOC_ID` | your doc ID |
| `DRAFT_RECIPIENT` | your email |
| `GROQ_API_KEY` | optional |

`CORS_ORIGINS` can list multiple URLs comma-separated.

---

## Step 4 — Bootstrap pulse data on Railway

After first deploy, run the pipeline **once** on Railway so the API has data:

**Option A — Railway dashboard**

1. **pulse-api** → **Settings** → **Cron** (or one-off **Run command** if available)
2. Command: `bash scripts/run_pipeline_public.sh`

**Option B — Railway CLI (local)**

```bash
npm i -g @railway/cli
railway login
railway link          # select pulse-api service
railway run bash scripts/run_pipeline_public.sh
```

Verify: open `https://YOUR-PULSE-API.up.railway.app/api/pulse/latest` — should return JSON.

---

## Step 5 — Railway: weekly cron (auto refresh)

1. **pulse-api** → **Settings** → **Cron Jobs** → **Add**
2. Schedule: `30 3 * * 1` (Monday 03:30 UTC = 09:00 IST)
3. Command: `bash scripts/run_pipeline_public.sh`

Public users always see fresh data without your laptop.

---

## Step 6 — Vercel: deploy frontend

1. Open [Vercel](https://vercel.com) → **Add New Project**
2. Import **`Weekly_Pulse_Grow-`** from GitHub
3. **Root Directory:** `frontend`
4. Framework: Next.js (auto-detected)

**Environment variable:**

| Name | Value |
|------|--------|
| `NEXT_PUBLIC_API_URL` | `https://YOUR-PULSE-API.up.railway.app` |

5. Deploy

Copy the Vercel URL (e.g. `https://groww-pulse.vercel.app`).

---

## Step 7 — Link CORS

Back in Railway **pulse-api** variables, set:

```
CORS_ORIGINS=https://your-project.vercel.app
```

Redeploy pulse-api. Open your Vercel URL — dashboard should load pulse data.

---

## Step 8 — Keep GitHub Actions (optional)

Your existing **Weekly Pulse** workflow can stay for:

- MCP publish (Doc + Gmail draft)
- CI tests

To avoid running the pipeline twice, either:

- Use **Railway cron** for data + **GitHub Actions** with `publish: true` only (advanced), or
- Keep GitHub Actions as-is for publish and use Railway cron for public API data (both run pipeline — acceptable for demo)

---

## Checklist

- [ ] Railway **pulse-api** deployed and healthy (`/api/health`)
- [ ] Volume mounted at `/app/phases`
- [ ] Bootstrap script ran once (`/api/pulse/latest` works)
- [ ] Weekly cron on Railway
- [ ] Vercel deployed with `NEXT_PUBLIC_API_URL`
- [ ] `CORS_ORIGINS` includes Vercel URL

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Vercel shows "API not reachable" | Check `NEXT_PUBLIC_API_URL`, redeploy Vercel |
| CORS error in browser | Add Vercel URL to `CORS_ORIGINS`, redeploy API |
| `/api/pulse/latest` 404 | Run `bash scripts/run_pipeline_public.sh` on Railway |
| Data resets after deploy | Add volume at `/app/phases` |
