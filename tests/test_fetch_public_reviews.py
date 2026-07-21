"""Tests for public review export generation."""

from __future__ import annotations

import csv

from scripts.fetch_public_reviews import write_csv


def test_write_csv_removes_header_only_export(tmp_path):
    path = tmp_path / "reviews.csv"
    path.write_text("Rating,Review,Date\n", encoding="utf-8")

    write_csv(path, [], ["Rating", "Review", "Date"])

    assert not path.exists()


def test_write_csv_writes_non_empty_export(tmp_path):
    path = tmp_path / "reviews.csv"
    rows = [{"Rating": "5", "Review": "Works well", "Date": "2026-07-20"}]

    write_csv(path, rows, ["Rating", "Review", "Date"])

    with path.open(newline="", encoding="utf-8") as fh:
        assert list(csv.DictReader(fh)) == rows
