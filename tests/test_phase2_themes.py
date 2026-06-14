"""Phase 2 theme clustering tests."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from src.ingest.models import ReviewRecord
from src.themes.aggregate import aggregate_theme_stats, total_quote_candidates
from src.themes.config_loader import load_taxonomy
from src.themes.exceptions import EmptyCorpusError
from src.themes.pipeline import run_theme_clustering
from src.themes.rules import assign_review_rules
from src.themes.sampler import stratified_subsample

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "themes"
SAMPLE_REVIEWS = FIXTURES / "sample_reviews.json"


def _review(review_id: str, text: str, rating: int = 3, title: str | None = None) -> ReviewRecord:
    return ReviewRecord(
        id=review_id,
        store="play_store",
        rating=rating,
        title=title,
        text=text,
        review_date="2026-05-01",
        locale="en",
        week_bucket="2026-W18",
    )


class TestRuleMapping:
    def test_kyc_pending_maps_to_kyc(self):
        taxonomy = load_taxonomy()
        assignment = assign_review_rules(
            _review("1", "My KYC pending for two weeks now please verify"),
            taxonomy,
        )
        assert assignment.theme_id == "kyc"
        assert not assignment.ambiguous

    def test_sip_failed_maps_to_payments(self):
        taxonomy = load_taxonomy()
        assignment = assign_review_rules(
            _review("2", "My SIP failed during auto pay mandate setup yesterday"),
            taxonomy,
        )
        assert assignment.theme_id == "payments"

    def test_otp_login_maps_to_login(self):
        taxonomy = load_taxonomy()
        assignment = assign_review_rules(
            _review("3", "OTP not received during login attempt yesterday evening"),
            taxonomy,
        )
        assert assignment.theme_id == "login"

    def test_tax_statement_maps_to_statements(self):
        taxonomy = load_taxonomy()
        assignment = assign_review_rules(
            _review("4", "Cannot download tax statement from portfolio reports section"),
            taxonomy,
        )
        assert assignment.theme_id == "statements"

    def test_redemption_maps_to_withdrawals(self):
        taxonomy = load_taxonomy()
        assignment = assign_review_rules(
            _review("5", "Redemption amount not credited to bank after sell proceeds"),
            taxonomy,
        )
        assert assignment.theme_id == "withdrawals"

    def test_crash_maps_to_performance(self):
        taxonomy = load_taxonomy()
        assignment = assign_review_rules(
            _review("6", "App crashes on launch every morning since last update"),
            taxonomy,
        )
        assert assignment.theme_id == "performance"

    def test_unknown_review_uses_fallback(self):
        taxonomy = load_taxonomy()
        assignment = assign_review_rules(
            _review("7", "Nice colour scheme on the home screen layout today"),
            taxonomy,
        )
        assert assignment.theme_id == taxonomy.fallback_theme_id
        assert assignment.ambiguous


class TestAggregation:
    def test_theme_cap_at_five(self):
        taxonomy = load_taxonomy()
        reviews = [
            _review("a", "KYC pending verification documents upload issue", 2),
            _review("b", "SIP payment failed during checkout process today", 2),
            _review("c", "OTP not received during login attempt yesterday evening", 1),
            _review("d", "Cannot download tax statement from portfolio reports", 2),
            _review("e", "Withdrawal amount not credited after redemption request", 2),
            _review("f", "Options trading charts freeze during market hours daily", 1),
            _review("g", "App crash slow lag bug error stuck force close", 1),
            _review("h", "Sign up register open account onboarding first time user", 3),
        ]
        assignments = [assign_review_rules(r, taxonomy) for r in reviews]
        stats, _, _ = aggregate_theme_stats(assignments, taxonomy, max_themes=5)
        assert len(stats) <= 5

    def test_top_three_ranked_by_count(self):
        taxonomy = load_taxonomy()
        texts = [
            ("p1", "App crash slow lag bug error stuck force close not working", 1),
            ("p2", "Another crash slow freeze bug error stuck update broke", 1),
            ("s1", "Cannot download tax statement portfolio report capital gains", 2),
            ("s2", "Tax statement portfolio holdings profit loss report download", 2),
            ("l1", "OTP not received during login attempt yesterday evening", 1),
        ]
        assignments = [assign_review_rules(_review(rid, text, rating), taxonomy) for rid, text, rating in texts]
        stats, _, _ = aggregate_theme_stats(assignments, taxonomy, max_themes=5)
        assert stats[0].review_count >= stats[1].review_count >= stats[2].review_count

    def test_quote_candidates_present(self):
        taxonomy = load_taxonomy()
        reviews = [
            _review("q1", "OTP not received during login attempt yesterday evening", 1),
            _review("q2", "Cannot download tax statement from portfolio reports section", 2),
            _review("q3", "Withdrawal amount not credited after redemption request today", 1),
        ]
        assignments = [assign_review_rules(r, taxonomy) for r in reviews]
        stats, _, _ = aggregate_theme_stats(assignments, taxonomy, max_themes=5)
        assert total_quote_candidates(stats) >= 3


class TestSampler:
    def test_subsample_caps_size(self):
        reviews = [
            _review(f"r{i}", f"Review number {i} about portfolio tax statement report", i % 5 + 1)
            for i in range(50)
        ]
        sampled, meta = stratified_subsample(reviews, max_reviews=20, seed=42)
        assert len(sampled) == 20
        assert meta["sampled_from"] == 50


class TestPipeline:
    def test_empty_corpus_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            empty = Path(tmp) / "empty.json"
            empty.write_text(json.dumps({"reviews": []}), encoding="utf-8")
            with pytest.raises(EmptyCorpusError):
                run_theme_clustering(
                    reviews_path=empty,
                    output_path=Path(tmp) / "themes.json",
                    use_groq=False,
                )

    def test_full_pipeline_writes_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "themes.json"
            result = run_theme_clustering(
                reviews_path=SAMPLE_REVIEWS,
                output_path=out,
                use_groq=False,
                config=_test_config(Path(tmp)),
            )
            assert out.exists()
            payload = json.loads(out.read_text())
            assert len(payload["themes"]) <= 5
            assert payload["stats"]["total_assignments"] == result.total_assignments
            assert all(item["theme_id"] for item in payload["assignments"])
            assert len(payload["top_pulse_themes"]) == 3
            assert payload["top_pulse_themes"][0]["rank"] == 1
            assert payload["stats"]["total_assignments"] > 0

    def test_cli_rules_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "themes.json"
            result = run_theme_clustering(
                reviews_path=SAMPLE_REVIEWS,
                output_path=out,
                use_groq=False,
                config=_test_config(Path(tmp)),
            )
            payload = json.loads(out.read_text())
            assert payload["groq_usage"]["enabled"] is False
            assert result.groq_usage.requests == 0


def _test_config(tmp: Path):
    from src.themes.config_loader import GroqConfig, ThemeClusterConfig

    return ThemeClusterConfig(
        product_name="Groww",
        display_name="Groww App",
        reviews_input=tmp / "reviews.json",
        themes_output=tmp / "themes.json",
        themes_yaml=Path(__file__).resolve().parents[1] / "config" / "themes.yaml",
        max_reviews=100,
        sample_seed=42,
        max_themes=5,
        top_pulse_themes=3,
        groq=GroqConfig(
            model="llama-3.3-70b-versatile",
            batch_size=40,
            max_requests_per_minute=3,
            min_seconds_between_requests=21,
            max_samples_per_theme=10,
            max_daily_tokens_abort=80000,
            enabled=True,
        ),
    )
