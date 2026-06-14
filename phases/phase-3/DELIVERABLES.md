# Phase 3 deliverables

| File | Description |
|------|-------------|
| `pulse.md` | Weekly pulse markdown (`python -m src.pulse.run`) |
| `pulse.json` | Structured pulse sidecar with validation status |

## Modules

| Path | Role |
|------|------|
| `src/pulse/generator.py` | Template-based pulse from themes.json |
| `src/pulse/pipeline.py` | Orchestration |
| `src/pulse/run.py` | CLI |
| `src/guardrails/redact.py` | PII redaction |
| `src/guardrails/validate.py` | Hard constraint gate |
| `tests/test_phase3_pulse.py` | 13 tests |

## Run

```bash
source .venv/bin/activate
python -m src.themes.run --no-groq   # Phase 2 input
python -m src.pulse.run
pytest tests/test_phase3_pulse.py
```

Latest run: **230 words**, validation **PASSED**, 3 themes / 3 quotes / 3 actions.
