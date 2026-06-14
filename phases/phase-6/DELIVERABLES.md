# Phase 6 deliverables

| Artifact | Description |
|----------|-------------|
| `.github/workflows/ci.yml` | CI — pytest on push/PR |
| `.github/workflows/weekly-pulse.yml` | Weekly scheduler (Mon 09:00 IST) |
| `tests/fixtures/expected-pulse-schema.json` | Golden pulse structure (P6-T-11) |
| `tests/test_phase6_signoff.py` | Phase 6 regression tests |
| `scripts/phase6_signoff.py` | Generates `signoff_report.json` |
| `Docs/github-actions.md` | Actions operator guide |
| `signoff_report.json` | Generated each run (artifact / local) |

## Run locally

```bash
pytest tests/test_phase6_signoff.py
python scripts/phase6_signoff.py
```

## GitHub

See [Docs/github-actions.md](../../Docs/github-actions.md) for secrets and manual trigger steps.
