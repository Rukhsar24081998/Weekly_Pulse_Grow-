# Architecture & Business Decision Log

**Project:** Weekly App Review Pulse (LIP 4)  
**Format:** Newest decisions at the top. Status: `proposed` | `accepted` | `superseded`

This log records **major technical and logical decisions** made while designing and building the project — not implementation trivia. Each entry should answer: *What did we decide, why, and what trade-off did we accept?*

---

## How to Use This Log

- Add an entry when a choice affects architecture, scope, integrations, data handling, or business rules.
- Link to the phase where the decision was made or confirmed.
- If a decision changes, add a new ADR and mark the old one `superseded` — do not silently edit history.
- Small choices (variable names, minor refactors) do not belong here.

---

## ADR-025 — Re-run same week: append doc, new draft

| Field | Value |
|-------|-------|
| **Status** | accepted |
| **Date** | 2026-06-14 |
| **Phase** | 5 |
| **Category** | Integration |

**Context:** Operators may re-run the weekly workflow after fixing data or MCP failures. Need predictable Google Workspace behavior.

**Decision:** On re-run for the same week, **append** pulse content to the configured Google Doc (`PUBLISH_GOOGLE_DOC_ID`) via MCP `append_to_doc`. Create a **new Gmail draft** each run (no in-place draft update).

**Consequences:** Doc accumulates weekly sections if re-run multiple times — operator may trim manually. Each draft is independent for review.

**Alternatives considered:** Create new doc each run — rejected because Railway MCP has no `createDocument` tool.

---

## ADR-024 — Email body: header + doc link + full pulse

| Field | Value |
|-------|-------|
| **Status** | accepted |
| **Date** | 2026-06-14 |
| **Phase** | 5 |
| **Category** | Output |

**Context:** Gmail draft must be self-contained for operator review while linking to the Google Doc.

**Decision:** Email body includes a short header (product, week ending, review window), optional **Google Doc URL** from Phase 4 metadata, then the **full pulse markdown** below a separator (`src/publish/draft_pipeline.py` → `build_email_body`).

**Consequences:** Draft is readable without opening the doc; doc link supports leadership who prefer Docs.

**Alternatives considered:** Summary + link only — rejected because Problem Statement expects draft ready to review/send with pulse content.

---

## ADR-023 — GitHub Actions weekly scheduler (Phase 6)

| Field | Value |
|-------|-------|
| **Status** | accepted |
| **Date** | 2026-06-14 |
| **Phase** | 6 |
| **Category** | Technical |

**Context:** ADR-013 assumed MCP publish required a Cursor agent session. Railway HTTP MCP + GitHub Actions enables scheduled unattended runs.

**Decision:** Add **CI** (pytest on push/PR) and **Weekly Pulse** workflow (Monday 09:00 IST) that runs fetch → ingest → themes (`--no-groq` default) → pulse → validate → `e2e_run` → sign-off. Secrets: `GROQ_API_KEY`, `MCP_SERVER_URL`, `PUBLISH_GOOGLE_DOC_ID`, `DRAFT_RECIPIENT`.

**Consequences:** Partially supersedes ADR-013 unattended-cron limitation for this deployment. Operator still reviews Gmail draft manually.

**Alternatives considered:** Cursor-only weekly runs — retained as Option C in runbook for local/agent use.

---

## ADR-022 — Railway HTTP MCP for publish (Phase 4–5)

| Field | Value |
|-------|-------|
| **Status** | accepted |
| **Date** | 2026-06-14 |
| **Phase** | 4 |
| **Category** | Integration |

**Context:** Problem Statement requires MCP-only Google integration. Cursor `@a-bonus/google-docs-mcp` works in IDE but not in headless CI. A deployed MCP server exposes HTTP tools.

**Decision:** Implement **`src/publish/mcp_client.py`** HTTP client against Railway MCP (`MCP_SERVER_URL`). Tools: `append_to_doc`, `create_email_draft`. Pre-create Google Doc; set `PUBLISH_GOOGLE_DOC_ID` in `.env`. No Google SDK in `src/`.

**Consequences:** CLI and GitHub Actions can publish without Cursor. Server repo: [Rukhsar24081998/MCP-SERVER](https://github.com/Rukhsar24081998/MCP-SERVER). ADR-008 remains valid for Cursor-native MCP; ADR-022 is the primary path for automated publish.

**Alternatives considered:** Google SDK in CI — rejected per Problem Statement.

---

## ADR-009 — Artifact-based handoff between pipeline and agent

| Field | Value |
|-------|-------|
| **Status** | accepted |
| **Date** | 2026-06-09 |
| **Phase** | 0 (architecture) |
| **Category** | Technical |

**Context:** The system has two execution modes: offline Python analysis and Cursor agent MCP publish. They must interoperate without tight coupling.

**Decision:** The pipeline writes **validated artifacts to disk** (normalized reviews, themes JSON, pulse markdown/JSON, run metadata). The agent **reads those artifacts** and performs MCP steps. No in-process coupling between Python and MCP.

**Consequences:**
- (+) Pipeline testable without Cursor or Google credentials
- (+) Operator can inspect/fix artifacts before publish
- (+) Partial recovery when MCP fails (retry publish only)
- (−) Extra manual or prompted step between batch and publish phases

**Alternatives considered:** Single monolithic agent doing all analysis and publish — rejected for testability and repeatability.

---

## ADR-008 — MCP server selection: `@a-bonus/google-docs-mcp`

| Field | Value |
|-------|-------|
| **Status** | accepted |
| **Date** | 2026-06-09 |
| **Phase** | 0 |
| **Category** | Integration |

**Context:** Need both Google Docs and Gmail draft tools in one MCP server configured in Cursor.

**Decision:** Standardize on **`@a-bonus/google-docs-mcp`** unless a cohort-specific alternative is mandated. Required capabilities: create document, write/update document content, create Gmail draft.

**Consequences:** Team follows npm package setup in `mcp.json` with `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in environment (not repo). Tool names may vary by server version — agent prompts describe intent, not hardcoded tool strings.

**Alternatives considered:** `@fryorcraken/google-docs-mcp` (adds Slides) — acceptable substitute if Docs + Gmail parity confirmed.

---

## ADR-007 — Python pipeline + Cursor agent orchestration

| Field | Value |
|-------|-------|
| **Status** | accepted |
| **Date** | 2026-06-09 |
| **Phase** | 0 |
| **Category** | Technical |

**Context:** Need repeatable ingestion/analysis and MCP-based delivery within Problem Statement constraints.

**Decision:** Implement **deterministic Python modules** for ingest, themes, pulse, and guardrails. Use the **Cursor agent** as orchestrator for MCP publish steps, validation gate enforcement at publish time, and ad-hoc recovery.

**Consequences:**
- (+) Unit tests on pipeline phases 1–3 without MCP
- (+) Clear separation: analysis vs integration
- (−) Two execution modes documented (CLI/batch + agent prompts)

**Alternatives considered:** Fully agent-driven analysis with no scripts — rejected because theme caps, word limits, and PII checks need reproducible automated tests.

---

## ADR-006 — PII: redact before any external artifact

| Field | Value |
|-------|-------|
| **Status** | accepted |
| **Date** | 2026-06-09 |
| **Phase** | 0 |
| **Category** | Privacy / Compliance |

**Context:** Store reviews may contain names, emails, phone numbers, or account references. Problem Statement forbids PII in any artifact including Google Doc and Gmail draft.

**Decision:** Two-layer approach:
1. **Ingestion:** Drop reviewer identity fields — never persist them.
2. **Output:** Run PII redaction on quotes and pulse text before writing output files and before any MCP call.

Validator blocks publish if PII patterns remain. Agent must not call MCP when validation fails.

**Consequences:** Quotes may read slightly unnatural after redaction; acceptable trade-off for compliance. Run metadata contains counts and IDs only — no review text.

**Alternatives considered:** Redact only at MCP boundary — rejected because local artifacts would still contain PII on disk.

---

## ADR-005 — Pulse length: hard limit 250 words

| Field | Value |
|-------|-------|
| **Status** | accepted |
| **Date** | 2026-06-09 |
| **Phase** | 0 |
| **Category** | Output |

**Context:** Leadership audience needs a scannable weekly health pulse, not a report.

**Decision:** Enforce **≤ 250 words** via automated validator. Block MCP publish if validation fails. Generator should target below the limit to avoid truncation edge cases.

**Consequences:** Pulse favors bullets and one-line theme summaries. Long quotes must be trimmed before redaction.

**Alternatives considered:** Soft guideline only — rejected because Problem Statement treats this as a hard constraint.

---

## ADR-004 — Theme cap: 5 clusters, pulse shows top 3

| Field | Value |
|-------|-------|
| **Status** | accepted |
| **Date** | 2026-06-09 |
| **Phase** | 0 |
| **Category** | Business / Output |

**Context:** Problem Statement requires max 5 themes when grouping, but the weekly note highlights top 3 themes with 3 quotes and 3 actions.

**Decision:** Clustering produces **≤ 5 themes** with full assignment coverage. The pulse surfaces the **top 3 by review volume** (default ranking). Remaining themes inform analysis and run metadata but do not appear as pulse header sections.

**Consequences:** Clear separation between analysis breadth (5) and leadership scanability (3). Action ideas map to top themes only.

**Alternatives considered:** Show all 5 themes in pulse — rejected due to word limit and scannability goals.

---

## ADR-003 — Review data: public exports only

| Field | Value |
|-------|-------|
| **Status** | accepted |
| **Date** | 2026-06-09 |
| **Phase** | 0 |
| **Category** | Data / Compliance |

**Context:** Store reviews can be obtained via official export tools or public datasets; scraping behind login is disallowed by Problem Statement.

**Decision:** Ingest only **public review export files** (CSV/JSON from App Store Connect and Play Console exports). No authenticated scraping, third-party paywalled review APIs, or persistence of reviewer identity fields.

**Consequences:**
- (+) Compliant with Problem Statement and store terms
- (−) Requires per-store parsers when export formats differ
- (−) Weekly operator must obtain fresh exports manually (no scraper automation)

**Alternatives considered:** Third-party review aggregation APIs — rejected due to cost, terms, and PII handling uncertainty.

---

## ADR-017 — Phase 0 review acquisition via public store listings

| Field | Value |
|-------|-------|
| **Status** | accepted |
| **Date** | 2026-06-09 |
| **Phase** | 0 |
| **Category** | Data |

**Context:** Phase 0 requires review data in `data/raw/` before Phase 1. Official App Store Connect / Play Console exports need authenticated console access.

**Decision:** Use **`scripts/fetch_public_reviews.py`** to pull publicly visible reviews from Groww's Play Store listing (`com.nextbillion.groww`) and App Store RSS (`1404871703`), save as export-compatible CSV **without reviewer identity fields**. Default 10-week window. Replace with official console exports when available.

**Consequences:**
- (+) Unblocks Phase 1 without console credentials
- (+) Real Groww review text for theme/pulse development
- (−) Public RSS/API caps App Store volume (~500); Play paginated to 3000
- (−) Column layout may differ slightly from console exports — parsers must stay flexible

**Alternatives considered:** Synthetic-only fixtures — rejected for unrealistic theme testing.

---

## ADR-016 — Default review window: 12 weeks

| Field | Value |
|-------|-------|
| **Status** | accepted |
| **Date** | 2026-06-09 |
| **Phase** | 0 |
| **Category** | Business |

**Context:** Problem Statement allows 8–12 weeks of review history. Groww weekly pulse uses the maximum window for richer theme signal.

**Decision:** Default to **12 weeks** (`config/product.yaml`). Operators may set 8–11 if needed; 12 is the project default.

**Consequences:** More reviews per run; Play Store public fetch may need deep pagination; App Store public RSS cannot cover 12 weeks — official App Store Connect export required for full iOS window.

**Alternatives considered:** 10 weeks — superseded by operator preference for full 12-week window.

---

## ADR-002 — Product scope: Groww App (Milestone 1)

| Field | Value |
|-------|-------|
| **Status** | accepted |
| **Date** | 2026-06-09 |
| **Phase** | 0 |
| **Category** | Business |

**Context:** LIP 4 continues the same product selected in Milestone 1. Phase 0 locks the target app for ingestion, themes, and pulse branding.

**Decision:** Use **Groww App** (Groww — stocks, mutual funds, IPO on iOS and Android) as the review target. Review sources are Apple App Store Connect and Google Play Console public exports. Configuration in `config/product.yaml`; fintech theme taxonomy in `config/themes.yaml`.

**Consequences:** Pulse titles, doc naming, and theme keywords use Groww domain language (KYC, SIP, UPI, redemption, portfolio, etc.).

**Alternatives considered:** N/A — Milestone 1 product selection.

---

## ADR-001 — Google Workspace via MCP only (no direct APIs)

| Field | Value |
|-------|-------|
| **Status** | accepted |
| **Date** | 2026-06-09 |
| **Phase** | 0 |
| **Category** | Integration |

**Context:** The weekly pulse must be published to Google Docs and drafted in Gmail. Direct Google API integration adds OAuth complexity, credential management, and SDK dependencies to the repo — explicitly forbidden by Problem Statement.

**Decision:** All Google Docs and Gmail operations go through **`@a-bonus/google-docs-mcp`** configured in Cursor. Application code produces markdown artifacts; the Cursor agent invokes MCP tools. No `google-api-python-client`, service accounts, or `googleapis.com` calls from application source.

**Consequences:**
- (+) No Google SDK or tokens in the application repo
- (+) OAuth handled by MCP server
- (+) CI can grep-check for accidental Google SDK imports
- (−) Publishing requires Cursor agent session — not a headless cron without MCP
- (−) E2E Google steps are manual or agent-driven, not fully automated in CI

**Alternatives considered:** `google-api-python-client` with service account; standalone Gmail script — rejected per Problem Statement constraints.

---

## ADR-010 — Rule-based theme clustering as primary; LLM optional

| Field | Value |
|-------|-------|
| **Status** | accepted |
| **Date** | 2026-06-09 |
| **Phase** | 0 (architecture) |
| **Category** | Technical |

**Context:** Reviews must be assigned to themes reproducibly with automated tests. LLM labeling is non-deterministic and may not run in CI.

**Decision:** **Primary:** keyword/rule matching against `config/themes.yaml`. **Optional:** LLM-assisted labeling for ambiguous reviews only. Golden tests and CI must pass with rules-only path.

**Consequences:**
- (+) Deterministic, fast, testable clustering baseline
- (+) Taxonomy updates do not require model prompt changes
- (−) Requires good keyword curation per product
- (−) Edge-case reviews may misclassify without optional LLM pass

**Alternatives considered:** Pure embedding clustering — rejected for MVP complexity and explainability; pure LLM classification — rejected for CI reproducibility; OpenAI/Anthropic — rejected in favor of Groq for Phase 2 (see ADR-021).

---

## ADR-021 — Groq as Phase 2 LLM provider

| Field | Value |
|-------|-------|
| **Status** | accepted |
| **Date** | 2026-06-09 |
| **Phase** | 2 (theme clustering) |
| **Category** | Technical |

**Context:** Phase 2 needs LLM assistance for ambiguous review classification and one-line theme summaries. ~63% of Groww reviews (2,143 after Phase 1 filters) do not match current taxonomy keywords and fall into the `performance` fallback. Sending all reviews to an LLM is ~64K tokens per run — too costly. CI must remain Groq-free.

**Decision:** Use **Groq** as the LLM provider for Phase 2 with a **hybrid pipeline**:

1. **Tier 1 — Rules:** Keyword matching against `config/themes.yaml` (deterministic; CI path).
2. **Tier 2 — Groq classify:** Batch only ambiguous reviews (no match + multi-match) after taxonomy expansion — 50–100 reviews per API call.
3. **Tier 3 — Groq summarize:** One call with aggregated stats + 10–15 sample reviews per top theme for leadership summaries in `themes.json`.

| Setting | Value |
|---------|-------|
| API key | `GROQ_API_KEY` (environment only) |
| Default model | `llama-3.3-70b-versatile` |
| Client | `src/themes/groq_client.py` |
| Prompts | `prompts/groq-theme-classify.md`, `prompts/groq-theme-summary.md` |

**Consequences:**
- (+) Fast inference; lower cost than classifying full corpus
- (+) Rules-only fallback when key missing or API fails
- (+) Summaries are leadership-ready without sending 2K+ reviews to the model
- (−) Groq output is non-deterministic — tests assert structure, not exact prose
- (−) Requires API key for full hybrid runs (not for CI)

**Alternatives considered:** OpenAI GPT-4 — rejected for cost on batch classification; rules-only — insufficient given 63% fallback rate on Groww data; send-all-reviews-to-LLM — rejected per token budget analysis in `phases/phase-1/DATA_PROFILE.md`.

---

## ADR-011 — Gmail draft only; no auto-send

| Field | Value |
|-------|-------|
| **Status** | accepted |
| **Date** | 2026-06-09 |
| **Phase** | 0 |
| **Category** | Business / Integration |

**Context:** Problem Statement asks for a draft email to self or alias "ready to review and send" — not automated delivery to leadership lists.

**Decision:** MCP workflow creates a **Gmail draft** only. Operator manually reviews and sends or forwards. Agent prompts must not invoke send-mail tools.

**Consequences:**
- (+) Human quality gate before external distribution
- (+) Reduces risk of PII or draft content reaching wrong recipients
- (−) Extra manual step each week

**Alternatives considered:** Auto-send to distribution list — rejected for privacy and review control.

---

## ADR-012 — Fail-closed validation before MCP publish

| Field | Value |
|-------|-------|
| **Status** | accepted |
| **Date** | 2026-06-09 |
| **Phase** | 0 (architecture) |
| **Category** | Privacy / Technical |

**Context:** PII or constraint violations in Google Doc/Gmail are harder to retract than blocking locally.

**Decision:** Automated validator must pass (word count, 3/3/3 structure, PII scan) **before** any MCP call. Agent instructions treat validator failure as a hard stop.

**Consequences:**
- (+) Prevents non-compliant content reaching Google Workspace
- (−) Operator must fix and re-run pipeline or regenerate pulse on failure

**Alternatives considered:** Warn-only validation — rejected for PII and word-limit requirements.

---

## ADR-013 — Semi-automated weekly workflow (not headless cron)

| Field | Value |
|-------|-------|
| **Status** | accepted |
| **Date** | 2026-06-09 |
| **Phase** | 0 (architecture) |
| **Category** | Technical |

**Context:** MCP publish requires Cursor agent session; Problem Statement centers on MCP in Cursor, not a production SaaS deployment.

**Decision:** Design for **weekly operator-driven runs**: drop exports → run pipeline → agent publishes via MCP → operator reviews draft. Not optimized for unattended scheduled production jobs.

**Consequences:**
- (+) Matches LIP scope and MCP constraint
- (+) Human checkpoints for exports freshness and email send
- (−) No unattended cron without future architecture change (out of MVP scope)

**Alternatives considered:** Headless server with service account — rejected by MCP-only Google constraint.

---

## ADR-014 — Separate parsers per store; unified normalized schema

| Field | Value |
|-------|-------|
| **Status** | accepted |
| **Date** | 2026-06-09 |
| **Phase** | 1 (design) |
| **Category** | Technical |

**Context:** App Store and Play Store exports use different columns, date formats, and optional fields.

**Decision:** Maintain **separate ingestion logic per store**, converging to one **canonical review schema** for downstream theme and pulse stages. Do not force a single parser for both formats.

**Consequences:**
- (+) Easier to update one store when export format drifts
- (+) Downstream phases store-agnostic
- (−) Duplicate parser maintenance and test fixtures for both stores

**Alternatives considered:** Single generic CSV mapper — rejected due to format divergence.

---

## ADR-015 — Stable review ID via content hash

| Field | Value |
|-------|-------|
| **Status** | accepted |
| **Date** | 2026-06-09 |
| **Phase** | 1 (design) |
| **Category** | Technical |

**Context:** Weekly exports may overlap; same review can appear in multiple files.

**Decision:** Generate review `id` as a hash of store + review_date + text (and related stable fields). Use for deduplication across ingest runs.

**Consequences:**
- (+) Idempotent merges when operators drop overlapping exports
- (−) Text edits in export would produce new ID (acceptable for public review snapshots)

**Alternatives considered:** Store-provided review IDs — often unavailable or PII-adjacent in exports.

---

## ADR-018 — Missing store export: warn and continue

| Field | Value |
|-------|-------|
| **Status** | accepted |
| **Date** | 2026-06-09 |
| **Phase** | 1 (pre-implementation) |
| **Category** | Technical |

**Context:** Play Store raw data may be ready before App Store Connect export is uploaded. Phase 1 ingestion should not hard-fail during development.

**Decision:** If one store CSV is missing, **log a warning** and continue with the available store (`config/product.yaml` → `ingestion.missing_store: warn`). Phase 1 **sign-off** still requires both stores when exports exist.

**Consequences:** Pipeline can run Play-only temporarily; pulse should note single-store coverage in run metadata.

**Alternatives considered:** Abort on missing store — rejected for dev velocity; too strict before official iOS export is placed.

---

## ADR-019 — Short date window: warn in dev, strict at sign-off

| Field | Value |
|-------|-------|
| **Status** | accepted |
| **Date** | 2026-06-09 |
| **Phase** | 1 (pre-implementation) |
| **Category** | Technical |

**Context:** Public App Store fetch cannot cover 12 weeks. Raw validation fails for iOS until official export is uploaded.

**Decision:** Ingestion **`warn`s** when a file’s date span is below `min_weeks` (8) but still processes available rows (`ingestion.short_window: warn`). **`scripts/pre_phase1_check.py`** distinguishes *ready for implementation* (Play ≥8 weeks) vs *ready for sign-off* (both stores ≥8 weeks). Unit tests use `tests/fixtures/reviews/` including synthetic App Store dates for window logic.

**Consequences:** Phase 1 coding unblocked; operator must replace App Store raw CSV before final Phase 1 eval.

**Alternatives considered:** Abort always — blocks Phase 1 while waiting for App Store Connect access.

---

## ADR-020 — Phase-local deliverables under `phases/phase-N/`

| Field | Value |
|-------|-------|
| **Status** | accepted |
| **Date** | 2026-06-10 |
| **Phase** | 0 (convention) |
| **Category** | Technical |

**Context:** Phase outputs were split across `data/processed/`, `data/output/`, and ad hoc paths, making it unclear which artifact belonged to which phase.

**Decision:** Every file or folder **created by a phase** lives under **`phases/phase-N/`**. Only shared **inputs** (raw store CSVs) stay in `data/raw/`. Paths are declared in `config/product.yaml` → `deliverables` and resolved via `src/paths.py`.

**Consequences:**
- (+) Clear ownership per phase folder (e.g. `phases/phase-1/reviews.json`)
- (+) Easier review and sign-off against eval criteria
- (−) Downstream phases must read from prior phase folders, not a shared `data/processed/` tree

**Alternatives considered:** Central `data/processed/` + `data/output/` — superseded by this layout.

---

## Decisions deferred to implementation (record when resolved)

| Topic | Options | Resolve in |
|-------|---------|------------|
| ~~Default review window~~ | ~~8, 10, or 12 weeks~~ | **Resolved** — ADR-016 (12 weeks) |
| ~~Single-store missing~~ | ~~Warn vs abort~~ | **Resolved** — ADR-018 (warn) |
| ~~Short window (<8 weeks)~~ | ~~Warn vs abort~~ | **Resolved** — ADR-019 (warn; abort at sign-off) |
| ~~Email body format~~ | ~~Full pulse vs summary + doc link~~ | **Resolved** — ADR-024 |
| ~~Re-run same week~~ | ~~New doc/draft vs update existing~~ | **Resolved** — ADR-025 |
| Hybrid LLM labeling | ~~Enable or rules-only~~ | **Resolved** — ADR-021 (Groq hybrid) |
| Groq model | Default vs alternate | ADR-021 |

When resolved, add a new ADR or update the relevant phase entry and mark deferred item closed.

---

## Template for New Decisions

```markdown
## ADR-NNN — Title

| Field | Value |
|-------|-------|
| **Status** | proposed |
| **Date** | YYYY-MM-DD |
| **Phase** | N |
| **Category** | Technical / Business / Integration / Privacy |

**Context:** ...

**Decision:** ...

**Consequences:** ...

**Alternatives considered:** ...
```
