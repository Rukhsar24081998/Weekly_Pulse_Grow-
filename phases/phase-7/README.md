# Phase 7 — Public API + Frontend

**Product:** Groww App  
**Status:** Complete  
**Depends on:** Phase 6  
**Eval:** [Docs/phases/phase-7/eval.md](../../Docs/phases/phase-7/eval.md)  
**Deploy guide:** [Docs/public-deployment.md](../../Docs/public-deployment.md)

## Purpose

Expose the latest validated pulse on public URLs — Railway read API + Vercel dashboard — without running the pipeline locally.

## Why code is not only in this folder

Phases 0–6 store **pipeline artifacts** here (`reviews.json`, `pulse.json`, etc.).  
Phase 7 is a **deployment and consumption layer**: it reads those artifacts and serves them publicly. Implementation lives in:

| Area | Location | Role |
|------|----------|------|
| Read + sync API | `src/api/` | FastAPI (`GET /api/pulse/latest`, `POST /api/sync/artifacts`) |
| Frontend | `frontend/` | Next.js dashboard + pulse page |
| Sync script | `scripts/sync_public_api.py` | Push `phases/` to Railway after weekly run |
| Railway image | `Dockerfile`, `railway.toml` | pulse-api service |
| Tests | `tests/test_api.py`, `tests/test_api_sync.py` | API + sync regression |

This folder documents Phase 7 deliverables and eval criteria, matching phases 0–6.

## Live URLs (Groww)

| Service | URL |
|---------|-----|
| Frontend | [weekly-pulse-grow.vercel.app](https://weekly-pulse-grow.vercel.app) |
| API | [weeklypulsegrow-production.up.railway.app](https://weeklypulsegrow-production.up.railway.app) |

## Run locally

```bash
# Terminal 1 — API
source .venv/bin/activate
python -m src.api

# Terminal 2 — frontend
cd frontend && npm run dev
```

## Sync to Railway (after redeploy or first deploy)

```bash
export PUBLIC_PULSE_API_URL=https://weeklypulsegrow-production.up.railway.app
export SYNC_SECRET='your-secret'
python scripts/sync_public_api.py
```

← [Phase 6](../phase-6/README.md)
