# Phase 7 deliverables

| Artifact | Description |
|----------|-------------|
| `src/api/` | FastAPI read-only API over phase artifacts |
| `frontend/` | Next.js dashboard (`/`) and pulse page (`/pulse`) |
| `scripts/sync_public_api.py` | Upload `phases/` JSON/MD to Railway pulse-api |
| `Dockerfile` | Railway pulse-api container |
| `railway.toml` | Railway deploy config |
| `Docs/public-deployment.md` | Step-by-step public deploy guide |
| `.github/workflows/weekly-pulse.yml` | Sync step after weekly pipeline (when secrets set) |
| `tests/test_api.py` | Health, status, pulse endpoints |
| `tests/test_api_sync.py` | Sync auth + storage |

## Deployed services (not files in `phases/`)

| Service | Platform | Env vars |
|---------|----------|----------|
| pulse-api | Railway | `SYNC_SECRET`, `CORS_ORIGINS` |
| frontend | Vercel | `NEXT_PUBLIC_API_URL` |

GitHub secrets: `PUBLIC_PULSE_API_URL`, `SYNC_SECRET` (same value as Railway).

## Operational note

Railway redeploy clears synced pulse data. Re-run `sync_public_api.py` or trigger **Weekly Pulse** in GitHub Actions.
