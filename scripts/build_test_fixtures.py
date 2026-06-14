#!/usr/bin/env python3
"""Build anonymized Phase 1 test fixtures from raw exports (+ synthetic App Store dates)."""

from __future__ import annotations

import csv
import random
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
FIXTURES = ROOT / "tests" / "fixtures" / "reviews"

PLAY_FIELDS = ["Star Rating", "Review Text", "Review Submit Date", "Reviewer Language"]
APP_FIELDS = ["Rating", "Title", "Review", "Date", "Territory"]

SAMPLE_TEXTS = [
    "KYC verification pending for too long",
    "UPI payment failed when adding money",
    "Cannot download tax statement",
    "OTP not received during login",
    "App crashes on opening portfolio",
    "Easy SIP setup for mutual funds",
    "Withdrawal amount not credited yet",
    "Search for stocks works well",
    "Slow app after latest update",
    "Good experience investing in IPO",
]


def sample_play_rows(min_rows: int = 24) -> list[dict]:
    path = RAW / "groww_play_store_reviews.csv"
    if not path.exists():
        return []

    by_week: dict[str, list[dict]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            date = row.get("Review Submit Date", "")[:10]
            if date and row.get("Review Text"):
                week = datetime.fromisoformat(date).strftime("%Y-W%W")
                by_week[week].append(row)

    picked: list[dict] = []
    for week in sorted(by_week.keys()):
        picked.extend(by_week[week][:2])
    if len(picked) < min_rows:
        picked = list(csv.DictReader(path.open(newline="", encoding="utf-8-sig")))[:min_rows]

    out = []
    for row in picked[: max(min_rows, len(picked))]:
        out.append({k: row.get(k, "") for k in PLAY_FIELDS})
    return out


def build_app_fixture(min_rows: int = 24, weeks: int = 12) -> list[dict]:
    """Real recent rows + synthetic older rows so window tests span 12 weeks."""
    path = RAW / "groww_app_store_reviews.csv"
    real: list[dict] = []
    if path.exists():
        with path.open(newline="", encoding="utf-8-sig") as fh:
            for row in csv.DictReader(fh):
                if row.get("Review"):
                    real.append(row)

    out: list[dict] = []
    for row in real[:10]:
        out.append(
            {
                "Rating": row.get("Rating", "3"),
                "Title": row.get("Title") or "Review",
                "Review": row.get("Review", "")[:200],
                "Date": row.get("Date", ""),
                "Territory": row.get("Territory", "IN"),
            }
        )

    today = datetime.now(timezone.utc).date()
    rng = random.Random(42)
    need = max(0, min_rows - len(out))
    for i in range(need):
        days_ago = rng.randint(14, weeks * 7 - 1)
        d = today - timedelta(days=days_ago)
        text = SAMPLE_TEXTS[i % len(SAMPLE_TEXTS)]
        out.append(
            {
                "Rating": str(rng.randint(1, 5)),
                "Title": "User feedback",
                "Review": text,
                "Date": d.isoformat(),
                "Territory": "IN",
            }
        )

    return out[: max(min_rows, len(out))]


def write_fixture(name: str, fieldnames: list[str], rows: list[dict]) -> Path:
    FIXTURES.mkdir(parents=True, exist_ok=True)
    path = FIXTURES / name
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


def main() -> None:
    play_rows = sample_play_rows()
    app_rows = build_app_fixture()
    play_path = write_fixture("play_store_sample.csv", PLAY_FIELDS, play_rows)
    app_path = write_fixture("app_store_sample.csv", APP_FIELDS, app_rows)
    print(f"Wrote {len(play_rows)} rows -> {play_path}")
    print(f"Wrote {len(app_rows)} rows -> {app_path}")
    print("Note: app_store_sample includes synthetic dated rows for 12-week window tests only.")


if __name__ == "__main__":
    main()
