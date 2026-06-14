# Phase 1 — Review Ingestion

**Product:** Groww App  
**Status:** Complete  
**Depends on:** Phase 0  
**Eval:** [Docs/phases/phase-1/eval.md](../Docs/phases/phase-1/eval.md)

## Purpose

Load 8–12 weeks of App Store and Play Store exports into unified, PII-free normalized JSON.

## Deliverables

| Module | Output |
|--------|--------|
| `src/ingest/app_store.py` | App Store CSV parser |
| `src/ingest/play_store.py` | Play Store CSV parser |
| `src/ingest/normalize.py` | Dedupe + date window filter |
| `src/ingest/pipeline.py` | Orchestration |
| `src/ingest/run.py` | CLI |
| `tests/test_phase1_ingest.py` | 13 tests |
| `phases/phase-1/reviews.json` | Normalized output |

## Run

```bash
source .venv/bin/activate
python -m src.ingest.run --weeks 12
pytest tests/test_phase1_ingest.py
```

Latest run: **2,143 reviews** (play_store=2,143; app_store=0 after filters), 12-week window, 5,612 content-filtered, 2,574 duplicates removed.

**Data profile for Phase 2:** [DATA_PROFILE.md](./DATA_PROFILE.md) — theme gaps, Groq routing strategy, quote pool analysis.

## Exit gate

All criteria in [eval.md](../Docs/phases/phase-1/eval.md) before Phase 2.

← [Phase 0](../phase-0/README.md) · → [Phase 2](../phase-2/README.md)
