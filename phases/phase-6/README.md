# Phase 6 — Validation & Hardening

**Product:** Groww App  
**Status:** Complete (automated); manual teammate sign-off optional  
**Depends on:** Phase 5  
**Eval:** [Docs/phases/phase-6/eval.md](../Docs/phases/phase-6/eval.md)

## Purpose

Prove Problem Statement success criteria; CI regression; weekly GitHub Actions scheduler; reproducible README.

## Work in this phase

| Area | Location | Output |
|------|----------|--------|
| CI workflow | `.github/workflows/ci.yml` | pytest on push/PR |
| Weekly scheduler | `.github/workflows/weekly-pulse.yml` | Mon 09:00 IST full pipeline |
| Golden schema | `tests/fixtures/expected-pulse-schema.json` | Pulse structure regression |
| Sign-off script | `scripts/phase6_signoff.py` | `phases/phase-6/signoff_report.json` |
| Tests | `tests/test_phase6_signoff.py` | Phase 6 checks |
| Docs | `Docs/github-actions.md` | Secrets + manual run |

## Run

```bash
pytest tests/ -q
python scripts/phase6_signoff.py
```

## GitHub Actions setup

1. Add 4 repository secrets (see [Docs/github-actions.md](../Docs/github-actions.md))
2. **Actions** tab → enable workflows
3. **Weekly Pulse** → Run workflow (manual test) or wait for Monday schedule

→ [Phase 7](../phase-7/README.md) — public API + Vercel frontend
