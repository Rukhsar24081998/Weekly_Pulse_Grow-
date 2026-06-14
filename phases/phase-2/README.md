# Phase 2 — Theme Clustering

**Product:** Groww App  
**Status:** Complete (rules + Groq client)  
**Depends on:** Phase 1  
**Eval:** [Docs/phases/phase-2/eval.md](../Docs/phases/phase-2/eval.md)

## Purpose

Assign every review in a **1,000-review stratified sample** to a theme; produce ≤ 5 ranked themes with quote candidates for the pulse.

## Pipeline

| Tier | Step | Groq? |
|------|------|-------|
| 0 | Subsample 1,000 from `reviews.json` | No |
| 1 | Rule-based keyword assign | No |
| 2 | Classify ambiguous reviews (40/batch, paced) | Yes |
| 3 | One-line theme summaries (single call) | Yes |

## Work in this phase

| Area | Module | Output |
|------|--------|--------|
| Subsample | `src/themes/sampler.py` | 1,000-review sample |
| Rule matching | `src/themes/rules.py` | Per-review theme_id |
| Groq client | `src/themes/groq_client.py` | Classify + summarize |
| Aggregation | `src/themes/aggregate.py` | Rank, cap, quotes |
| CLI | `src/themes/run.py` | `phases/phase-2/themes.json` |
| Tests | `tests/test_phase2_themes.py` | 14 tests (rules-only in CI) |

## Run

```bash
source .venv/bin/activate
python -m src.themes.run              # uses GROQ_API_KEY from .env if set
python -m src.themes.run --no-groq    # rules-only
# or: ./scripts/run_themes.sh
pytest tests/test_phase2_themes.py
```

Latest run: **1,000** reviews sampled from 2,143 → **5 themes**; top pulse themes: **performance**, **discovery**, **statements**.

## LLM

**Provider:** Groq (`llama-3.3-70b-versatile`) · See [architecture §16](../../Docs/architecture.md) for rate limits (~8–10 calls, ~25–32K tokens/run).

## Exit gate

All criteria in [eval.md](../Docs/phases/phase-2/eval.md) before Phase 3.

← [Phase 1](../phase-1/README.md) · → [Phase 3](../phase-3/README.md)
