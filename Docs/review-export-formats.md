# Review export formats — Groww App

**Phase:** 0 (Foundation)  
**Product:** Groww App (iOS + Android)  
**Policy:** Public exports only — no login scraping.

This document describes how to obtain and place review exports for the Weekly App Review Pulse pipeline.

---

## Primary workflow — download and store

Download **8–12 weeks** of reviews from each store console and save locally:

| Step | Action |
|------|--------|
| 1 | Export from **App Store Connect** (Groww) → save as `data/raw/groww_app_store_reviews.csv` |
| 2 | Export from **Play Console** (Groww) → save as `data/raw/groww_play_store_reviews.csv` |
| 3 | Validate storage: `python scripts/validate_raw_exports.py` |

Files stay in `data/raw/` on your machine (gitignored). Overwrite each week before a new pulse run.

See also [data/raw/README.md](../data/raw/README.md).

---

## Dev fallback (no console access)

| Store | File | Acquisition |
|-------|------|-------------|
| Play Store | `data/raw/groww_play_store_reviews.csv` | `scripts/fetch_public_reviews.py` (public listing) |
| App Store | `data/raw/groww_app_store_reviews.csv` | Same script — multi-country App Store RSS (~500/country, deduped) |

Use only until official exports are available.

---

| Store | File | Acquisition |
|-------|------|-------------|
| Play Store | `data/raw/groww_play_store_reviews.csv` | Public listing via `scripts/fetch_public_reviews.py` |
| App Store | `data/raw/groww_app_store_reviews.csv` | Public App Store RSS via `scripts/fetch_public_reviews.py` |

Re-fetch before each weekly run:

```bash
source .venv/bin/activate
python scripts/fetch_public_reviews.py
```

For production compliance, replace with **official** App Store Connect and Play Console exports when you have console access.

---

4. Export reviews for the desired date range covering **12 weeks** (default per `config/product.yaml`).
|-------|-----------|----------------------------|
| App Store | `data/raw/` | `groww_app_store_reviews.csv` (or `.json`) |
| Play Store | `data/raw/` | `groww_play_store_reviews.csv` (or `.json`) |

Refresh exports weekly before each pulse run. Raw files are gitignored by default.

---

## App Store (Apple App Store Connect)

### How to export

1. Sign in to [App Store Connect](https://appstoreconnect.apple.com/).
2. Open **Apps** → select **Groww** (Groww Stocks, Mutual Fund, IPO).
3. Go to **Ratings and Reviews** (or **Analytics → Reviews** depending on UI version).
4. Export reviews for the desired date range covering **8–12 weeks** (default: 10 weeks per `config/product.yaml`).
5. Save the export to `data/raw/`.

### Expected fields (map in Phase 1)

| Export column (typical) | Canonical field | Notes |
|-------------------------|-----------------|-------|
| Rating | `rating` | Integer 1–5 |
| Title | `title` | May be empty |
| Review | `text` | Body text |
| Date | `review_date` | Normalize to ISO-8601 |
| Territory / Country | `locale` | e.g. `en-IN` |
4. Filter by date range (**12 weeks**) and export CSV.
### Fields to discard (never persist)

- Reviewer nickname / name  
- Reviewer ID  
- Developer response metadata tied to identity  

---

## Play Store (Google Play Console)

### How to export

1. Sign in to [Google Play Console](https://play.google.com/console/).
2. Select the **Groww** app.
3. Go to **Ratings and reviews** → **Reviews**.
4. Filter by date range (8–12 weeks) and export CSV.
5. Save to `data/raw/`.

### Expected fields (map in Phase 1)

| Export column (typical) | Canonical field | Notes |
|-------------------------|-----------------|-------|
| Star Rating | `rating` | Integer 1–5 |
| Review Text | `text` | Primary clustering input |
- **Default:** 12 weeks (`config/product.yaml`)  
| Reviewer Language | `locale` | Optional |

Play Store exports often have **no title** — `title` is nullable in the schema.

### Fields to discard (never persist)

- Reviewer name  
- Device metadata that could identify users  
- Email or account references in free text (also redacted at output)  

---

## Date window

- **Minimum:** 8 weeks of review history  
- **Default:** 10 weeks (`config/product.yaml`)  
- **Maximum:** 12 weeks  

If fewer than 8 weeks are available, the ingestion step should warn or abort per configuration (implemented in Phase 1).

---

## Compliance reminders

- Use only official console exports or other **public** datasets allowed by store terms.  
- Do not commit raw exports to git if they are large or contain identifiable text at scale.  
- Identity fields are dropped at ingestion; quotes are redacted before any Google publish step.

---

## Next phase

Phase 1 implements parsers and normalization using the column mappings above. Update this document if your export format differs from the typical columns listed.
