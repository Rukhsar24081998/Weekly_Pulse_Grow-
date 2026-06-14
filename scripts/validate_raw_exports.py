#!/usr/bin/env python3
"""Validate downloaded review exports in data/raw/ (8–12 week window)."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PHASE0_DIR = ROOT / "phases" / "phase-0"

APP_STORE_FILE = "groww_app_store_reviews.csv"
PLAY_STORE_FILE = "groww_play_store_reviews.csv"

APP_DATE_COLUMNS = ("Date", "date", "Review Date", "review_date")
PLAY_DATE_COLUMNS = ("Review Submit Date", "review_submit_date", "Date", "date")
APP_RATING_COLUMNS = ("Rating", "rating", "Star Rating")
PLAY_RATING_COLUMNS = ("Star Rating", "star_rating", "Rating", "rating")


def load_config() -> dict:
    import yaml  # noqa: PLC0415

    return yaml.safe_load((ROOT / "config" / "product.yaml").read_text())


def parse_date(value: str) -> datetime | None:
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def pick_column(row: dict, candidates: tuple[str, ...]) -> str | None:
    lower_map = {k.lower(): k for k in row.keys()}
    for name in candidates:
        if name.lower() in lower_map:
            return lower_map[name.lower()]
    return None


def read_csv_stats(path: Path, date_cols: tuple[str, ...]) -> dict:
    if not path.exists():
        return {"exists": False, "path": str(path)}

    dates: list[datetime] = []
    rows = 0
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        date_col = None
        for row in reader:
            rows += 1
            if date_col is None:
                date_col = pick_column(row, date_cols)
            if date_col and row.get(date_col):
                dt = parse_date(row[date_col])
                if dt:
                    dates.append(dt)

    if not dates:
        return {
            "exists": True,
            "path": str(path),
            "rows": rows,
            "error": "No parseable dates found — check column names",
        }

    earliest = min(dates)
    latest = max(dates)
    span_weeks = (latest - earliest).days / 7
    return {
        "exists": True,
        "path": str(path),
        "rows": rows,
        "date_column": date_col,
        "earliest": earliest.date().isoformat(),
        "latest": latest.date().isoformat(),
        "span_weeks": round(span_weeks, 1),
    }


def validate(weeks: int, min_weeks: int, max_weeks: int) -> dict:
    if weeks < min_weeks or weeks > max_weeks:
        raise ValueError(f"weeks must be between {min_weeks} and {max_weeks}")

    app_stats = read_csv_stats(RAW_DIR / APP_STORE_FILE, APP_DATE_COLUMNS)
    play_stats = read_csv_stats(RAW_DIR / PLAY_STORE_FILE, PLAY_DATE_COLUMNS)

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(weeks=weeks)

    issues: list[str] = []
    if not app_stats.get("exists"):
        issues.append(f"Missing App Store file: {RAW_DIR / APP_STORE_FILE}")
    if not play_stats.get("exists"):
        issues.append(f"Missing Play Store file: {RAW_DIR / PLAY_STORE_FILE}")

    for label, stats in (("app_store", app_stats), ("play_store", play_stats)):
        if not stats.get("exists"):
            continue
        if stats.get("error"):
            issues.append(f"{label}: {stats['error']}")
            continue
        if stats["rows"] == 0:
            issues.append(f"{label}: file is empty")
        latest = datetime.fromisoformat(stats["latest"]).replace(tzinfo=timezone.utc)
        if latest < cutoff - timedelta(days=7):
            issues.append(
                f"{label}: latest review {stats['latest']} is older than expected for {weeks}-week window"
            )
        if stats["span_weeks"] < min_weeks:
            issues.append(
                f"{label}: date span {stats['span_weeks']} weeks < minimum {min_weeks} weeks"
            )

    report = {
        "validated_at": now.isoformat(),
        "target_window_weeks": weeks,
        "allowed_range_weeks": f"{min_weeks}-{max_weeks}",
        "cutoff_date": cutoff.date().isoformat(),
        "app_store": app_stats,
        "play_store": play_stats,
        "valid": len(issues) == 0,
        "issues": issues,
    }
    return report


def main() -> int:
    cfg = load_config()
    rw = cfg["review_window"]
    parser = argparse.ArgumentParser(description="Validate raw review exports (8–12 weeks)")
    parser.add_argument(
        "--weeks",
        type=int,
        default=int(rw["default_weeks"]),
        help=f"Expected review window (default: {rw['default_weeks']})",
    )
    args = parser.parse_args()

    report = validate(args.weeks, int(rw["min_weeks"]), int(rw["max_weeks"]))

    out_path = PHASE0_DIR / "storage_validation.json"
    PHASE0_DIR.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))
    print(f"\nReport -> {out_path}")

    if report["valid"]:
        print(f"\nOK: Both stores stored with ≥{rw['min_weeks']} weeks of review data.")
        return 0

    print("\nFix issues above, then re-run.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
