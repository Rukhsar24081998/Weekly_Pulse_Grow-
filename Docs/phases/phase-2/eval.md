# Phase 2 — Theme Clustering: Evaluation

**Reference:** [Phase 2 in phase-wise-implementationplan.md](../../phase-wise-implementationplan.md#phase-2--theme-clustering)  
**Architecture:** [architecture.md](../../architecture.md) §6

---

## Scope

Assign reviews to themes; produce ≤ 5 themes with counts, averages, and quote candidates for the pulse.

---

## Test Plan

### Unit tests

| ID | Test | File | Expected result |
|----|------|------|-----------------|
| P2-T-01 | Rule-based mapping | `tests/test_phase2_themes.py` | "KYC pending" → `kyc` theme |
| P2-T-02 | SIP payment text | `tests/test_phase2_themes.py` | "SIP failed" → `payments` theme |
| P2-T-03 | Theme cap | `tests/test_phase2_themes.py` | Output has ≤ 5 themes |
| P2-T-04 | Full assignment | `tests/test_phase2_themes.py` | Every review has a `theme_id` |
| P2-T-05 | Top 3 selection | `tests/test_phase2_themes.py` | Top 3 ranked by `review_count` |
| P2-T-06 | Quote sampling | `tests/test_phase2_themes.py` | ≥ 3 quote candidates across themes |
| P2-T-07 | Unknown review fallback | `tests/test_phase2_themes.py` | Unmatched text → `discovery` or `performance` default |
| P2-T-08 | Empty corpus | `tests/test_phase2_themes.py` | Zero reviews → clear error |

### Integration tests

| ID | Test | Steps | Expected result |
|----|------|-------|-----------------|
| P2-T-09 | Theme CLI | `python -m src.themes.run` | Writes `phases/phase-2/themes.json` |
| P2-T-10 | Stats accuracy | Compare theme counts to manual count on 50-review sample | ± 1 review per theme |
| P2-T-11 | Product-relevant themes | Inspect top themes on real data | Top 5 themes align with `config/themes.yaml` for chosen product |

### Golden set (manual review)

| ID | Review snippet (paraphrased) | Expected theme |
|----|------------------------------|----------------|
| P2-T-12 | "OTP not received during login" | `login` |
| P2-T-13 | "Cannot download tax statement" | `statements` |
| P2-T-14 | "Redemption amount not credited" | `withdrawals` |
| P2-T-15 | "App crashes on launch" | `performance` |
| P2-T-16 | "Easy to start first SIP" | `onboarding` or `payments` |

---

## Exit Criteria

- [ ] **P2-EC-01** `phases/phase-2/themes.json` produced with ≤ 5 themes
- [ ] **P2-EC-02** 100% of reviews assigned a theme
- [ ] **P2-EC-03** Top 3 themes identifiable with `review_count` and `avg_rating`
- [ ] **P2-EC-04** Quote candidates stored per theme (for Phase 3)
- [ ] **P2-EC-05** `tests/test_phase2_themes.py` passes
- [ ] **P2-EC-06** Golden set P2-T-12 through P2-T-16: ≥ 4/5 correct on manual review
- [ ] **P2-EC-07** Theme labels match `config/themes.yaml` IDs

---

## Sign-off

| Role | Name | Date | Pass/Fail |
|------|------|------|-----------|
| Developer | | | |
| Reviewer | | | |

**Notes:**
