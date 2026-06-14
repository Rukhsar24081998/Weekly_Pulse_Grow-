# Phase 3 — Pulse Generation & Guardrails: Evaluation

**Reference:** [Phase 3 in phase-wise-implementationplan.md](../../phase-wise-implementationplan.md#phase-3--pulse-generation--guardrails)  
**Architecture:** [architecture.md](../../architecture.md) §3.3, §7

---

## Scope

Generate the weekly pulse markdown; enforce ≤ 250 words, 3 themes / 3 quotes / 3 actions, and zero PII.

---

## Test Plan

### Unit tests — generator

| ID | Test | File | Expected result |
|----|------|------|-----------------|
| P3-T-01 | Pulse structure | `tests/test_phase3_pulse.py` | Sections: top themes, quotes, action ideas |
| P3-T-02 | Exactly 3 themes in pulse | `tests/test_phase3_pulse.py` | Output lists 3 themes only |
| P3-T-03 | Exactly 3 quotes | `tests/test_phase3_pulse.py` | 3 quote blocks present |
| P3-T-04 | Exactly 3 actions | `tests/test_phase3_pulse.py` | 3 action items present |
| P3-T-05 | Word count ≤ 250 | `tests/test_phase3_pulse.py` | `word_count <= 250` |
| P3-T-06 | Scannable format | Manual / snapshot | Bullets or short paragraphs; no wall of text |

### Unit tests — PII redactor

| ID | Test | Input | Expected result |
|----|------|-------|-----------------|
| P3-T-07 | Email redaction | `contact me at a@b.com` | `[email redacted]` |
| P3-T-08 | Phone redaction | `call 9876543210` | `[phone redacted]` |
| P3-T-09 | PAN-like token | `ABCDE1234F` | `[id redacted]` |
| P3-T-10 | @handle strip | `@username said` | Handle removed or genericized |

### Unit tests — validator

| ID | Test | File | Expected result |
|----|------|------|-----------------|
| P3-T-11 | Block over word limit | `tests/test_phase3_pulse.py` | Validator returns error if > 250 words |
| P3-T-12 | Block missing sections | `tests/test_phase3_pulse.py` | Validator fails if quotes < 3 |
| P3-T-13 | Block PII in output | `tests/test_phase3_pulse.py` | Validator fails if email pattern found |
| P3-T-14 | Pass valid pulse | `tests/test_phase3_pulse.py` | Golden fixture passes all checks |

### Integration tests

| ID | Test | Steps | Expected result |
|----|------|-------|-----------------|
| P3-T-15 | Pulse CLI | `python -m src.pulse.run` | Writes `phases/phase-3/pulse.md` |
| P3-T-16 | JSON sidecar | Inspect `phases/phase-3/pulse.json` | Structured pulse schema populated |
| P3-T-17 | Validator gate | Run publish script with invalid pulse | Exit non-zero before MCP phase |

---

## Exit Criteria

- [ ] **P3-EC-01** `phases/phase-3/pulse.md` generated from themes JSON
- [ ] **P3-EC-02** Pulse contains top 3 themes, 3 quotes, 3 action ideas
- [ ] **P3-EC-03** Word count ≤ 250 (automated check)
- [ ] **P3-EC-04** PII redactor applied; zero PII patterns in final output
- [ ] **P3-EC-05** `src/guardrails/validate.py` blocks invalid pulses
- [ ] **P3-EC-06** `tests/test_phase3_pulse.py` passes (≥ 10 test cases)
- [ ] **P3-EC-07** Human readability: reviewer can scan pulse in < 60 seconds

---

## Sample Pulse Checklist (manual)

- [ ] Opens with product name and week ending date
- [ ] Each theme has a one-line summary
- [ ] Quotes are anonymized and tied to themes
- [ ] Action ideas are specific and actionable (not generic "improve UX")
- [ ] No usernames, emails, or account numbers visible

---

## Sign-off

| Role | Name | Date | Pass/Fail |
|------|------|------|-----------|
| Developer | | | |
| Reviewer | | | |

**Notes:**
