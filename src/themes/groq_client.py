"""Groq API client with rate limiting (Phase 2 Tier 2 + Tier 3)."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from src.ingest.models import ReviewRecord
from src.env_loader import load_env
from src.themes.config_loader import GroqConfig
from src.themes.exceptions import GroqError
from src.themes.models import GroqUsage, ThemeStats, ThemeTaxonomy

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
ROOT = Path(__file__).resolve().parents[2]


class GroqRateLimiter:
    def __init__(self, config: GroqConfig) -> None:
        self.config = config
        self._request_times: list[float] = []

    def wait_for_slot(self) -> None:
        now = time.monotonic()
        self._request_times = [t for t in self._request_times if now - t < 60.0]

        if self._request_times:
            elapsed = now - self._request_times[-1]
            min_gap = self.config.min_seconds_between_requests
            if elapsed < min_gap:
                time.sleep(min_gap - elapsed)

        now = time.monotonic()
        self._request_times = [t for t in self._request_times if now - t < 60.0]
        if len(self._request_times) >= self.config.max_requests_per_minute:
            sleep_for = 60.0 - (now - self._request_times[0]) + 0.1
            if sleep_for > 0:
                time.sleep(sleep_for)

        self._request_times.append(time.monotonic())


class GroqClient:
    def __init__(
        self,
        config: GroqConfig,
        api_key: str | None = None,
        *,
        dry_run: bool = False,
    ) -> None:
        load_env()
        self.config = config
        self.api_key = api_key or os.environ.get("GROQ_API_KEY", "").strip()
        self.dry_run = dry_run
        self.limiter = GroqRateLimiter(config)
        self.usage = GroqUsage(enabled=bool(self.api_key) and not dry_run, model=config.model)

    @property
    def available(self) -> bool:
        return bool(self.api_key) and self.config.enabled and not self.dry_run

    def _load_prompt(self, name: str) -> str:
        path = ROOT / "prompts" / name
        return path.read_text(encoding="utf-8")

    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)

    def _chat(self, system: str, user: str) -> str:
        if not self.api_key:
            raise GroqError("GROQ_API_KEY is not set")

        if self.usage.tokens_estimated + self._estimate_tokens(system + user) > self.config.max_daily_tokens_abort:
            raise GroqError("Projected Groq token usage exceeds daily abort threshold")

        self.limiter.wait_for_slot()

        body = {
            "model": self.config.model,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        request = urllib.request.Request(
            GROQ_API_URL,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "LIP-4-4/1.0 (Weekly App Review Pulse)",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            if exc.code == 429:
                time.sleep(60)
                raise GroqError(f"Groq rate limit: {detail}") from exc
            raise GroqError(f"Groq HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise GroqError(f"Groq request failed: {exc}") from exc

        self.usage.requests += 1
        content = payload["choices"][0]["message"]["content"]
        self.usage.tokens_estimated += self._estimate_tokens(system + user + content)
        return content

    def classify_batch(
        self,
        reviews: list[ReviewRecord],
        taxonomy: ThemeTaxonomy,
    ) -> dict[str, str]:
        if not reviews:
            return {}

        system = self._load_prompt("groq-theme-classify.md")
        theme_payload = [
            {"id": theme.id, "label": theme.label, "keywords": theme.keywords[:8]}
            for theme in taxonomy.themes
        ]
        review_payload = [
            {
                "id": review.id,
                "rating": review.rating,
                "text": review.text[:500],
                "title": review.title,
            }
            for review in reviews
        ]
        user = json.dumps(
            {
                "fallback_theme_id": taxonomy.fallback_theme_id,
                "themes": theme_payload,
                "reviews": review_payload,
            },
            ensure_ascii=False,
        )

        raw = self._chat(system, user)
        parsed = json.loads(raw)
        valid = taxonomy.valid_theme_ids()
        assignments: dict[str, str] = {}
        for item in parsed.get("assignments", []):
            review_id = item.get("id") or item.get("review_id")
            theme_id = item.get("theme_id")
            if review_id and theme_id in valid:
                assignments[str(review_id)] = str(theme_id)
        return assignments

    def summarize_themes(
        self,
        theme_stats: list[ThemeStats],
        samples_by_theme: dict[str, list[ReviewRecord]],
        taxonomy: ThemeTaxonomy,
    ) -> dict[str, str]:
        if not theme_stats:
            return {}

        system = self._load_prompt("groq-theme-summary.md")
        theme_map = taxonomy.theme_by_id()
        payload = []
        for stat in theme_stats:
            samples = samples_by_theme.get(stat.theme_id, [])
            payload.append(
                {
                    "theme_id": stat.theme_id,
                    "label": stat.label,
                    "review_count": stat.review_count,
                    "avg_rating": stat.avg_rating,
                    "negative_pct": stat.negative_pct,
                    "definition": theme_map.get(stat.theme_id).label if stat.theme_id in theme_map else stat.label,
                    "sample_reviews": [
                        {"rating": r.rating, "text": r.text[:300]} for r in samples
                    ],
                }
            )

        user = json.dumps({"themes": payload}, ensure_ascii=False)
        raw = self._chat(system, user)
        parsed = json.loads(raw)
        summaries = parsed.get("summaries", parsed)
        if isinstance(summaries, dict):
            return {str(k): str(v) for k, v in summaries.items()}
        return {}
