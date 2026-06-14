# Raw review exports — Groww App

Store **official** App Store Connect and Play Console exports here.

## Required files (weekly pulse)

| Store | Filename | Source |
|-------|----------|--------|
| App Store | `groww_app_store_reviews.csv` | App Store Connect export |
| Play Store | `groww_play_store_reviews.csv` | Play Console export |

## Date window

Each export must cover **8–12 weeks** of reviews (default **12 weeks** — see `config/product.yaml`).

When downloading:
1. Set the console date filter to your chosen window (8, 9, 10, 11, or 12 weeks).
2. Export CSV for each store.
3. Save using the filenames above (overwrite previous week’s files).

## Validate after download

```bash
source .venv/bin/activate
python scripts/validate_raw_exports.py
python scripts/validate_raw_exports.py --weeks 12   # optional window override
```

## Storage notes

- Files in this folder are **gitignored** (see root `.gitignore`) — they stay on your machine only.
- Do not commit raw exports; they may contain review text at scale.
- Identity columns from console exports are dropped during Phase 1 ingestion — never persisted.

Validation report: `phases/phase-0/storage_validation.json`  
Dev fetch metadata: `phases/phase-0/fetch_metadata.json`

## App Store gap

Until you upload an official export, Phase 1 **development** uses Play raw data + test fixtures.
