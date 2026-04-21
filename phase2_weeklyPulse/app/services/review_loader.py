"""Load and normalize review data for Phase 2 pulse generation."""

from __future__ import annotations

from datetime import datetime
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from google_play_scraper import Sort, reviews


class ReviewLoader:
    def __init__(self, repo_root: Path):
        self.reviews_dir = repo_root / "data" / "reviews"
        self.reviews_dir.mkdir(parents=True, exist_ok=True)
        self.playstore_app_ids = self._resolve_app_ids()
        self.review_count = int(os.getenv("PLAYSTORE_REVIEW_COUNT", "100"))
        self.lang = os.getenv("PLAYSTORE_LANG", "en")
        self.country = os.getenv("PLAYSTORE_COUNTRY", "in")

    def _resolve_app_ids(self) -> List[str]:
        review_urls = os.getenv("PLAYSTORE_REVIEW_URLS", "").strip()
        if review_urls:
            ids: List[str] = []
            for url in [item.strip() for item in review_urls.split(",") if item.strip()]:
                app_id = _extract_app_id_from_url(url)
                if app_id:
                    ids.append(app_id)
            if ids:
                return ids

        app_ids = os.getenv("PLAYSTORE_APP_IDS", "in.indwealth")
        return [app_id.strip() for app_id in app_ids.split(",") if app_id.strip()]

    def latest_reviews_file(self) -> Optional[Path]:
        files = sorted(self.reviews_dir.glob("*.json"))
        return files[-1] if files else None

    def load_reviews(self, file_path: Optional[Path] = None) -> List[Dict[str, Any]]:
        path = file_path or self.latest_reviews_file()
        if not path or not path.exists():
            return []
        try:
            payload = json.loads(path.read_text())
            if isinstance(payload, list):
                return [r for r in payload if isinstance(r, dict)]
        except Exception:
            pass
        return []

    def fetch_latest_reviews(self) -> Path:
        if not self.playstore_app_ids:
            raise RuntimeError("No Play Store app IDs configured. Set PLAYSTORE_APP_IDS.")

        fetched: List[Dict[str, Any]] = []
        for app_id in self.playstore_app_ids:
            result, _ = reviews(
                app_id,
                lang=self.lang,
                country=self.country,
                sort=Sort.NEWEST,
                count=self.review_count,
                filter_score_with=None,
            )
            for row in result:
                fetched.append(
                    {
                        "reviewId": row.get("reviewId", ""),
                        "rating": row.get("score"),
                        "text": row.get("content", ""),
                        "date": row.get("at").isoformat() if row.get("at") else None,
                        "userName": "[REDACTED]",
                        "appVersion": row.get("reviewCreatedVersion"),
                        "appId": app_id,
                    }
                )

        if not fetched:
            raise RuntimeError("Play Store fetch returned zero reviews.")

        output_path = self.reviews_dir / f"{datetime.now().strftime('%Y-%m-%d')}.json"
        output_path.write_text(json.dumps(fetched, indent=2))
        return output_path


def _extract_app_id_from_url(url: str) -> Optional[str]:
    try:
        parsed = urlparse(url)
        app_id = parse_qs(parsed.query).get("id", [None])[0]
        return app_id
    except Exception:
        return None
