# App Store — 12-week export required

The public fetch script pulls **~500 reviews per country** from Apple's RSS feed (IN, US, GB, AE, SG, CA, AU — deduped). That still covers only **recent weeks**, not a full 12-week window.

## What to do

1. Sign in to [App Store Connect](https://appstoreconnect.apple.com/).
2. Open **Groww** → **Ratings and Reviews**.
3. Export reviews for the **last 12 weeks**.
4. Save as:

   ```
   data/raw/groww_app_store_reviews.csv
   ```

5. Validate:

   ```bash
   source .venv/bin/activate
   python scripts/validate_raw_exports.py --weeks 12
   python scripts/pre_phase1_check.py
   ```

## Until then

- **Phase 1 development** can proceed using Play Store raw data + `tests/fixtures/reviews/app_store_sample.csv`.
- **Phase 1 sign-off** requires a real 12-week App Store export (both stores ≥8 weeks).

See [Docs/review-export-formats.md](../../Docs/review-export-formats.md).
