"""Phase 1 ingestion tests."""

from __future__ import annotations

import json
import tempfile
from datetime import date
from pathlib import Path

import pytest

from src.ingest.app_store import parse_app_store_csv, parse_app_store_row
from src.ingest.dates import review_window
from src.ingest.exceptions import EmptyExportError, IngestionError
from src.ingest.models import FORBIDDEN_FIELDS, ReviewRecord
from src.ingest.normalize import dedupe_records, make_review_id, normalize_reviews
from src.ingest.pipeline import run_ingestion
from src.ingest.play_store import parse_play_store_csv, parse_play_store_row

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "reviews"
APP_FIXTURE = FIXTURES / "app_store_sample.csv"
PLAY_FIXTURE = FIXTURES / "play_store_sample.csv"


class TestAppStoreParser:
    def test_parse_fixture_csv(self):
        records = parse_app_store_csv(APP_FIXTURE)
        assert len(records) >= 20
        assert all(r.store == "app_store" for r in records)
        assert all(r.text for r in records)

    def test_parse_row_schema(self):
        row = {
            "Rating": "2",
            "Title": "Login issue",
            "Review": "OTP not received during login",
            "Date": "2026-05-01",
            "Territory": "IN",
        }
        record = parse_app_store_row(row)
        assert record is not None
        assert record.rating == 2
        assert record.title == "Login issue"
        assert record.review_date == "2026-05-01"
        assert record.locale == "en-IN"


class TestPlayStoreParser:
    def test_parse_fixture_csv(self):
        records = parse_play_store_csv(PLAY_FIXTURE)
        assert len(records) >= 20
        assert all(r.store == "play_store" for r in records)
        assert all(r.title is None for r in records)

    def test_parse_row_schema(self):
        row = {
            "Star Rating": "1",
            "Review Text": "UPI payment failed",
            "Review Submit Date": "2026-04-10",
            "Reviewer Language": "en",
        }
        record = parse_play_store_row(row)
        assert record is not None
        assert record.rating == 1
        assert record.text == "UPI payment failed"


class TestSchemaAndPII:
    def test_required_fields_on_fixture_records(self):
        records = parse_play_store_csv(PLAY_FIXTURE) + parse_app_store_csv(APP_FIXTURE)
        for record in records:
            data = record.to_dict()
            ReviewRecord.validate(data)
            assert "store" in data
            assert "rating" in data
            assert "text" in data
            assert "review_date" in data

    def test_no_pii_fields_in_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp)
            _copy_fixtures(raw)
            out = raw / "out.json"
            run_ingestion(weeks=12, raw_dir=raw, output_path=out, reference_date=date(2026, 6, 8))
            payload = json.loads(out.read_text())
            for review in payload["reviews"]:
                for key in FORBIDDEN_FIELDS:
                    assert key not in review


class TestDateWindow:
    def test_eight_week_window_excludes_old_reviews(self):
        records = parse_app_store_csv(APP_FIXTURE)
        ref = date(2026, 6, 8)
        result = normalize_reviews(records, weeks=8, min_weeks=8, reference=ref)
        start, _ = review_window(8, ref)
        for r in result.reviews:
            assert r.review_date >= start.isoformat()

    def test_twelve_week_window_includes_boundary(self):
        records = parse_app_store_csv(APP_FIXTURE)
        ref = date(2026, 6, 8)
        result = normalize_reviews(
            records, weeks=12, min_weeks=8, reference=ref, apply_content_filters=False
        )
        dates = {r.review_date for r in result.reviews}
        assert "2026-03-23" in dates


class TestEmptyExport:
    def test_empty_file_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.csv"
            path.write_text("", encoding="utf-8")
            with pytest.raises(EmptyExportError):
                parse_play_store_csv(path)


class TestDedupe:
    def test_duplicate_reviews_same_id(self):
        text = "Same review text"
        day = "2026-05-01"
        r1 = ReviewRecord(
            id=make_review_id("play_store", day, text),
            store="play_store",
            rating=5,
            title=None,
            text=text,
            review_date=day,
            locale="en",
            week_bucket="2026-W18",
        )
        r2 = ReviewRecord(
            id=make_review_id("play_store", day, text),
            store="play_store",
            rating=5,
            title=None,
            text=text,
            review_date=day,
            locale="en",
            week_bucket="2026-W18",
        )
        unique, removed = dedupe_records([r1, r2])
        assert len(unique) == 1
        assert removed == 1


class TestContentFilters:
    def test_rejects_short_text(self):
        from src.ingest.filters import review_passes_content_filters

        record = ReviewRecord(
            id="x",
            store="play_store",
            rating=5,
            title=None,
            text="good app",
            review_date="2026-05-01",
            locale="en",
            week_bucket="2026-W18",
        )
        ok, reason = review_passes_content_filters(record, min_words=6)
        assert not ok
        assert reason == "short_text"

    def test_rejects_emoji(self):
        from src.ingest.filters import review_passes_content_filters

        record = ReviewRecord(
            id="x",
            store="play_store",
            rating=5,
            title=None,
            text="This is a great application experience overall",
            review_date="2026-05-01",
            locale="en",
            week_bucket="2026-W18",
        )
        record.text = "This is a great application experience 🙏 overall"
        ok, reason = review_passes_content_filters(record, min_words=6)
        assert not ok
        assert reason == "emoji"

    def test_rejects_non_english_script(self):
        from src.ingest.filters import review_passes_content_filters

        record = ReviewRecord(
            id="x",
            store="play_store",
            rating=5,
            title=None,
            text="यह ऐप बहुत अच्छा है और उपयोगी है",
            review_date="2026-05-01",
            locale="en",
            week_bucket="2026-W18",
        )
        ok, reason = review_passes_content_filters(record, min_words=6)
        assert not ok
        assert reason == "non_english_text"

    def test_keeps_english_review_with_enough_words(self):
        from src.ingest.filters import review_passes_content_filters

        record = ReviewRecord(
            id="x",
            store="play_store",
            rating=2,
            title="Login issue",
            text="OTP not received during login attempt yesterday evening",
            review_date="2026-05-01",
            locale="en",
            week_bucket="2026-W18",
        )
        ok, _ = review_passes_content_filters(record, min_words=6)
        assert ok


class TestIntegration:
    def test_full_ingest_cli_writes_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp)
            _copy_fixtures(raw)
            out = Path(tmp) / "reviews.json"
            result = run_ingestion(
                weeks=10,
                raw_dir=raw,
                output_path=out,
                reference_date=date(2026, 6, 8),
            )
            assert out.exists()
            payload = json.loads(out.read_text())
            assert payload["filters"]["min_words"] == 6
            assert payload["filters"]["english_only"] is True
            for review in payload["reviews"]:
                assert len(review["text"].split()) >= 6
            assert payload["review_window_weeks"] == 10
            assert payload["stats"]["total"] == result.total_reviews
            assert payload["stats"]["total"] > 0
            assert payload["stats"]["play_store"] > 0

    def test_date_range_in_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp)
            _copy_fixtures(raw)
            out = Path(tmp) / "reviews.json"
            run_ingestion(weeks=12, raw_dir=raw, output_path=out, reference_date=date(2026, 6, 8))
            payload = json.loads(out.read_text())
            start = payload["window"]["start"]
            end = payload["window"]["end"]
            for r in payload["reviews"]:
                assert start <= r["review_date"] <= end

    def test_invalid_weeks_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw = Path(tmp)
            _copy_fixtures(raw)
            with pytest.raises(IngestionError):
                run_ingestion(weeks=7, raw_dir=raw, reference_date=date(2026, 6, 8))


def _copy_fixtures(raw_dir: Path) -> None:
    import shutil

    shutil.copy(APP_FIXTURE, raw_dir / "groww_app_store_reviews.csv")
    shutil.copy(PLAY_FIXTURE, raw_dir / "groww_play_store_reviews.csv")
