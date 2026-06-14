# Phase 3 — Pulse Generation & Guardrails

**Product:** Groww App  
**Status:** Complete  
**Depends on:** Phase 2  
**Eval:** [Docs/phases/phase-3/eval.md](../Docs/phases/phase-3/eval.md)

## Purpose

Generate the weekly one-page pulse and enforce ≤ 250 words, 3/3/3 structure, and zero PII.

## Pipeline

| Step | Module | Output |
|------|--------|--------|
| Generate | `src/pulse/generator.py` | Pulse draft from `themes.json` |
| Redact | `src/guardrails/redact.py` | PII stripped from quotes + body |
| Validate | `src/guardrails/validate.py` | Hard gate (blocks Phase 4 if fail) |
| Write | `src/pulse/pipeline.py` | `pulse.md`, `pulse.json` |

## Run

```bash
source .venv/bin/activate
python -m src.pulse.run
pytest tests/test_phase3_pulse.py
```

Latest run: **230 words**, validation **PASSED** — top themes: performance, discovery, statements.

## Exit gate

All criteria in [eval.md](../Docs/phases/phase-3/eval.md) before Phase 4 (MCP publish).

← [Phase 2](../phase-2/README.md) · → [Phase 4](../phase-4/README.md)
