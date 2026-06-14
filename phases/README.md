# Weekly App Review Pulse — Phases

Each phase keeps **all of its deliverables** inside its own folder under `phases/phase-N/`.  
Shared **inputs** only (raw store CSV exports) live in `data/raw/`.

## Layout convention

| Phase | Folder | Deliverables (examples) |
|-------|--------|---------------------------|
| 0 | [phase-0/](phase-0/) | `phase0_report.json`, `fetch_metadata.json`, `storage_validation.json` |
| 1 | [phase-1/](phase-1/) | `reviews.json`, `pre_phase1_report.json` |
| 2 | [phase-2/](phase-2/) | `themes.json` |
| 3 | [phase-3/](phase-3/) | `pulse.md`, `pulse.json` |
| 4 | [phase-4/](phase-4/) | `doc_metadata.json` |
| 5 | [phase-5/](phase-5/) | `run.json` |
| 6 | [phase-6/](phase-6/) | `signoff_report.json` |
| 7 | [phase-7/](phase-7/) | Deploy docs only — code in `src/api/`, `frontend/` (see [README](phase-7/README.md)) |

Paths for phases 0–6 are defined in [config/product.yaml](../config/product.yaml) under `deliverables`.  
Phase 7 does not add new pipeline JSON artifacts; it publishes existing artifacts via Railway + Vercel.  
Code resolves phase 0–6 paths via [src/paths.py](../src/paths.py).

## Eval criteria

| Phase | Eval |
|-------|------|
| 0 | [eval.md](../Docs/phases/phase-0/eval.md) |
| 1 | [eval.md](../Docs/phases/phase-1/eval.md) |
| 2 | [eval.md](../Docs/phases/phase-2/eval.md) |
| 3 | [eval.md](../Docs/phases/phase-3/eval.md) |
| 4 | [eval.md](../Docs/phases/phase-4/eval.md) |
| 5 | [eval.md](../Docs/phases/phase-5/eval.md) |
| 6 | [eval.md](../Docs/phases/phase-6/eval.md) |
| 7 | [eval.md](../Docs/phases/phase-7/eval.md) |

**Rule:** Do not start phase N+1 until phase N passes all exit criteria in its eval.

Plan: [Docs/phase-wise-implementationplan.md](../Docs/phase-wise-implementationplan.md)
