#!/usr/bin/env python3
"""Fetch public Groww store reviews into export-compatible CSV files.

Uses publicly visible store listing data (Play Store + App Store RSS).
Output excludes reviewer identity fields per project PII policy.
Official App Store Connect / Play Console exports should replace these for production.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PHASE0_DIR = ROOT / "phases" / "phase-0"

PLAY_PACKAGE = "com.nextbillion.groww"
DEFAULT_APP_STORE_COUNTRIES = ("in", "us", "gb", "ae", "sg", "ca", "au")
APP_STORE_RSS_PAGES = 10  # Apple hard cap: 10 pages × 50 reviews = 500 per country
PLAY_MAX_PAGES = 150  # safety cap; ~200 reviews/page
USER_AGENT = "WeeklyPulse/1.0 (LIP-4-4 public review fetch)"


def load_config() -> dict:
    import yaml  # noqa: PLC0415

    return yaml.safe_load((ROOT / "config" / "product.yaml").read_text())


def load_app_store_settings(cfg: dict | None = None) -> tuple[str, tuple[str, ...]]:
    data = cfg or load_config()
    app_store = data.get("stores", {}).get("app_store", {})
    app_id = str(app_store.get("app_id", "1404871703"))
    countries = app_store.get("rss_countries") or list(DEFAULT_APP_STORE_COUNTRIES)
    normalized = tuple(str(code).strip().lower() for code in countries if str(code).strip())
    if not normalized:
        normalized = DEFAULT_APP_STORE_COUNTRIES
    return app_id, normalized


def load_weeks(override: int | None = None) -> int:
    cfg = load_config()
    rw = cfg["review_window"]
    weeks = override if override is not None else int(rw["default_weeks"])
    min_w, max_w = int(rw["min_weeks"]), int(rw["max_weeks"])
    if weeks < min_w or weeks > max_w:
        raise ValueError(f"weeks must be between {min_w} and {max_w}")
    return weeks


def window_start(weeks: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(weeks=weeks)


def parse_date(value: str | datetime) -> datetime | None:
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value).strip()
        if not text:
            return None
        for fmt in (
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ):
            try:
                dt = datetime.strptime(text.replace("+0000", "+00:00"), fmt)
                break
            except ValueError:
                continue
        else:
            try:
                dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
            except ValueError:
                return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def date_span_weeks(rows: list[dict], date_key: str) -> float | None:
    dates = [parse_date(r[date_key]) for r in rows if r.get(date_key)]
    dates = [d for d in dates if d]
    if len(dates) < 2:
        return None
    return round((max(dates) - min(dates)).days / 7, 1)


def _rss_label(entry: dict, key: str) -> str:
    value = entry.get(key, {})
    if isinstance(value, dict):
        return str(value.get("label", "")).strip()
    return str(value or "").strip()


def _review_dedupe_key(entry: dict, *, rating: str, text: str, date_label: str) -> str:
    review_id = _rss_label(entry, "id")
    if review_id:
        return review_id
    return f"{date_label}|{rating}|{text[:160]}"


def fetch_play_reviews(cutoff: datetime) -> list[dict]:
    try:
        from google_play_scraper import Sort, reviews  # noqa: PLC0415
    except ImportError as exc:
        raise SystemExit(
            "Install google-play-scraper: pip install google-play-scraper"
        ) from exc

    collected: list[dict] = []
    token = None

    for _ in range(PLAY_MAX_PAGES):
        batch, token = reviews(
            PLAY_PACKAGE,
            lang="en",
            country="in",
            sort=Sort.NEWEST,
            count=200,
            continuation_token=token,
        )
        if not batch:
            break
        for item in batch:
            dt = parse_date(item.get("at"))
            if dt is None or dt < cutoff:
                continue
            text = (item.get("content") or "").strip()
            if not text:
                continue
            collected.append(
                {
                    "Star Rating": item.get("score", ""),
                    "Review Text": text,
                    "Review Submit Date": dt.strftime("%Y-%m-%d"),
                    "Reviewer Language": "en",
                }
            )
        oldest = parse_date(batch[-1].get("at"))
        if oldest and oldest < cutoff:
            break
        if token is None:
            break

    return collected


def fetch_app_store_country_reviews(
    country: str,
    cutoff: datetime,
    app_id: str,
) -> list[tuple[str, dict]]:
    """Fetch one country's RSS pages. Returns (dedupe_key, row) pairs."""
    rows: list[tuple[str, dict]] = []
    country_code = country.lower()

    for page in range(1, APP_STORE_RSS_PAGES + 1):
        url = (
            f"https://itunes.apple.com/{country_code}/rss/customerreviews/"
            f"page={page}/id={app_id}/sortby=mostrecent/json?l=en"
        )
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                payload = json.load(resp)
        except urllib.error.HTTPError:
            break

        entries = payload.get("feed", {}).get("entry", [])
        if not entries:
            break

        start = 1 if page == 1 else 0
        for entry in entries[start:]:
            dt = parse_date(_rss_label(entry, "updated"))
            if dt is None or dt < cutoff:
                continue
            rating = _rss_label(entry, "im:rating")
            title = _rss_label(entry, "title")
            text = _rss_label(entry, "content")
            if not text:
                continue
            date_label = dt.strftime("%Y-%m-%d")
            dedupe_key = _review_dedupe_key(
                entry, rating=rating, text=text, date_label=date_label
            )
            rows.append(
                (
                    dedupe_key,
                    {
                        "Rating": rating,
                        "Title": title,
                        "Review": text,
                        "Date": date_label,
                        "Territory": country_code.upper(),
                    },
                )
            )

    return rows


def fetch_app_store_reviews(
    cutoff: datetime,
    *,
    app_id: str,
    countries: tuple[str, ...],
    pause_seconds: float = 0.25,
) -> tuple[list[dict], dict]:
    """Fetch and dedupe App Store RSS reviews across multiple country storefronts."""
    seen: set[str] = set()
    collected: list[dict] = []
    raw_by_country: dict[str, int] = {}
    duplicates_dropped = 0

    for country in countries:
        batch = fetch_app_store_country_reviews(country, cutoff, app_id)
        raw_by_country[country.upper()] = len(batch)
        for dedupe_key, row in batch:
            if dedupe_key in seen:
                duplicates_dropped += 1
                continue
            seen.add(dedupe_key)
            collected.append(row)
        if pause_seconds > 0:
            time.sleep(pause_seconds)

    collected.sort(key=lambda row: row["Date"], reverse=True)
    stats = {
        "countries": [code.upper() for code in countries],
        "raw_by_country": raw_by_country,
        "raw_total": sum(raw_by_country.values()),
        "deduped_total": len(collected),
        "duplicates_dropped": duplicates_dropped,
    }
    return collected, stats


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch public Groww reviews (8–12 weeks)")
    parser.add_argument(
        "--weeks",
        type=int,
        default=None,
        help="Review window in weeks (default from config/product.yaml)",
    )
    parser.add_argument(
        "--countries",
        nargs="+",
        default=None,
        help="App Store RSS country codes (default from config/product.yaml)",
    )
    args = parser.parse_args()

    cfg = load_config()
    app_id, default_countries = load_app_store_settings(cfg)
    countries = tuple(
        code.strip().lower()
        for code in (args.countries or default_countries)
        if code.strip()
    )

    weeks = load_weeks(args.weeks)
    cutoff = window_start(weeks)
    print(f"Fetching Groww reviews from {cutoff.date()} to today ({weeks} weeks)")
    print(f"App Store RSS countries: {', '.join(code.upper() for code in countries)}")

    play_rows = fetch_play_reviews(cutoff)
    play_path = RAW_DIR / "groww_play_store_reviews.csv"
    write_csv(
        play_path,
        play_rows,
        ["Star Rating", "Review Text", "Review Submit Date", "Reviewer Language"],
    )
    play_span = date_span_weeks(play_rows, "Review Submit Date")
    print(f"Play Store: {len(play_rows)} reviews, span ~{play_span} weeks -> {play_path}")

    app_rows, app_stats = fetch_app_store_reviews(
        cutoff, app_id=app_id, countries=countries
    )
    app_path = RAW_DIR / "groww_app_store_reviews.csv"
    write_csv(
        app_path,
        app_rows,
        ["Rating", "Title", "Review", "Date", "Territory"],
    )
    app_span = date_span_weeks(app_rows, "Date")
    print(
        f"App Store: {len(app_rows)} deduped reviews "
        f"(raw {app_stats['raw_total']}, dupes dropped {app_stats['duplicates_dropped']}), "
        f"span ~{app_span} weeks -> {app_path}"
    )

    meta = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "product": "Groww App",
        "window_weeks": weeks,
        "cutoff_date": cutoff.date().isoformat(),
        "play_store_count": len(play_rows),
        "play_store_span_weeks": play_span,
        "app_store_count": len(app_rows),
        "app_store_span_weeks": app_span,
        "app_store_rss": app_stats,
        "source": "public_store_listings",
        "note": (
            "App Store RSS is capped at ~500 reviews per country (~3500 raw across 7 storefronts). "
            "Deduped by review ID. Still not a full 12-week window — use App Store Connect export."
        ),
    }
    meta_path = PHASE0_DIR / "fetch_metadata.json"
    PHASE0_DIR.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Metadata -> {meta_path}")

    if len(play_rows) == 0 and len(app_rows) == 0:
        print("WARNING: No reviews fetched. Check network or store IDs.", file=sys.stderr)
        return 1

    if play_span is not None and play_span < weeks:
        print(
            f"WARNING: Play Store span ({play_span}w) < target ({weeks}w). "
            "Download official Play Console export for full 12 weeks.",
            file=sys.stderr,
        )
    if app_span is not None and app_span < weeks:
        print(
            f"WARNING: App Store span ({app_span}w) < target ({weeks}w). "
            "Download official App Store Connect export for full 12 weeks.",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
