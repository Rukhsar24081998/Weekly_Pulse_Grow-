# Phase 7 — Public API + Frontend: Evaluation

**Reference:** [Phase 7 in phase-wise-implementationplan.md](../../phase-wise-implementationplan.md#phase-7--public-api--frontend)  
**Deploy guide:** [public-deployment.md](../../public-deployment.md)

---

## Scope

Read-only public access to the latest validated pulse: FastAPI on Railway, Next.js on Vercel, artifact sync from GitHub Actions (no Railway volume required).

---

## Test Plan

| ID | Test | Command / check | Pass? |
|----|------|-----------------|-------|
| P7-T-01 | API health | `curl …/api/health` | ✅ |
| P7-T-02 | Pulse latest | `curl …/api/pulse/latest` returns JSON after sync | ✅ |
| P7-T-03 | Sync auth | Wrong Bearer → 403; missing Railway `SYNC_SECRET` → 503 | ✅ |
| P7-T-04 | API tests | `pytest tests/test_api.py tests/test_api_sync.py` | ✅ |
| P7-T-05 | Frontend build | `cd frontend && npm run build` | ✅ |
| P7-T-06 | Vercel dashboard | [weekly-pulse-grow.vercel.app](https://weekly-pulse-grow.vercel.app) shows pulse stats | ✅ |
| P7-T-07 | Weekly sync | GitHub Action sync step after pipeline (secrets set) | ✅ |
| P7-T-08 | CORS | `CORS_ORIGINS` includes Vercel URL on Railway | ✅ |

---

## Exit criteria

- Public API serves `/api/pulse/latest` from synced phase artifacts
- Vercel frontend displays dashboard and full pulse page
- GitHub Actions can sync without manual laptop step
- Deploy documented in [public-deployment.md](../../public-deployment.md)

---

## Sign-off

| Role | Name | Date | Notes |
|------|------|------|-------|
| Developer | | | |
| Reviewer | | | Optional |
