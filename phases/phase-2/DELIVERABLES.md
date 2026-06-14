# Phase 2 deliverables

| File | Description |
|------|-------------|
| `themes.json` | Theme assignments, stats, quotes (`python -m src.themes.run`) |

## Modules

| Path | Role |
|------|------|
| `src/themes/sampler.py` | Stratified subsample (max 1,000) |
| `src/themes/rules.py` | Keyword theme assignment (Tier 1) |
| `src/themes/groq_client.py` | Groq classify + summarize (Tier 2/3) |
| `src/themes/aggregate.py` | Rank, cap ≤5 themes, quote candidates |
| `src/themes/pipeline.py` | Orchestration |
| `src/themes/run.py` | CLI |
| `tests/test_phase2_themes.py` | 14 tests |

## Run

```bash
source .venv/bin/activate
export GROQ_API_KEY=...   # optional — hybrid path
python -m src.themes.run           # rules + Groq if key set
python -m src.themes.run --no-groq # rules-only (CI)
pytest tests/test_phase2_themes.py
```

Latest run (rules-only): **1,000** sample from 2,143 → **5 themes**, top pulse: performance, discovery, statements.
