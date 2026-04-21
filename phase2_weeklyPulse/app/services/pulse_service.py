"""Weekly pulse orchestrator and persistence."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .review_loader import ReviewLoader
from .theme_engine import ThemeResult, extract_themes, generate_action_ideas


class PulseService:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.storage_dir = repo_root / "phase2_weeklyPulse" / "data"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.pulse_file = self.storage_dir / "weekly_pulse.json"
        self.last_sync_file = self.storage_dir / "last_pulse_sync.txt"
        self.loader = ReviewLoader(repo_root)

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def refresh(self, fetch_live_reviews: bool = True) -> Dict[str, Any]:
        source_file = self.loader.fetch_latest_reviews() if fetch_live_reviews else self.loader.latest_reviews_file()
        reviews = self.loader.load_reviews(source_file)
        top_themes, analytics = extract_themes(reviews)
        sentiment_score = round(sum(_safe_float(t.sentiment_score) for t in top_themes) / max(1, len(top_themes)), 3)
        action_ideas = generate_action_ideas(top_themes)
        pulse_text = self._pulse_text(top_themes, sentiment_score, action_ideas)
        word_count = len(pulse_text.split())

        payload = {
            "generated_at": self._now(),
            "reviews_source": str(source_file or ""),
            "raw_reviews_processed": len(reviews),
            "top_themes": [
                {
                    "theme": t.theme,
                    "confidence": t.confidence,
                    "mention_count": t.mention_count,
                    "sentiment_score": t.sentiment_score,
                }
                for t in top_themes
            ],
            "sentiment_score": sentiment_score,
            "action_ideas": action_ideas[:3],
            "word_count": word_count,
            "summary": pulse_text,
            "analytics": {
                "theme_distribution": _theme_distribution(top_themes),
                "sentiment_trends": analytics["sentiment_trends"],
                "mention_volume": analytics["mention_volume"],
                "keywords": analytics["keywords"],
            },
        }
        self.pulse_file.write_text(json.dumps(payload, indent=2))
        self.last_sync_file.write_text(payload["generated_at"])
        return payload

    def get_pulse(self) -> Dict[str, Any]:
        if not self.pulse_file.exists():
            return self.refresh()
        return json.loads(self.pulse_file.read_text())

    def get_themes(self) -> List[Dict[str, Any]]:
        pulse = self.get_pulse()
        return pulse.get("top_themes", [])

    def get_analytics(self) -> Dict[str, Any]:
        pulse = self.get_pulse()
        return pulse.get("analytics", {})

    def get_theme_details(self, theme_id: str) -> Dict[str, Any]:
        pulse = self.get_pulse()
        for theme in pulse.get("top_themes", []):
            if _slug(theme.get("theme", "")) == theme_id or theme.get("theme", "").lower() == theme_id.lower():
                return theme
        return {}

    def freshness(self) -> Dict[str, Any]:
        pulse = self.get_pulse()
        generated_at = pulse.get("generated_at")
        if not generated_at:
            return {"status": "unknown", "days_since_pulse": None, "last_pulse_generated": None}
        dt = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
        days = (datetime.now(timezone.utc) - dt).days
        status = "fresh" if days <= 7 else "stale" if days <= 14 else "outdated"
        top = pulse.get("top_themes", [])
        return {
            "last_pulse_generated": generated_at,
            "days_since_pulse": days,
            "status": status,
            "reviews_analyzed": pulse.get("raw_reviews_processed", 0),
            "top_theme": top[0]["theme"] if top else "None",
            "sentiment_score": pulse.get("sentiment_score", 0.0),
        }

    def _pulse_text(self, top_themes: List[ThemeResult], sentiment_score: float, action_ideas: List[str]) -> str:
        if not top_themes:
            return "No significant themes detected from current reviews."
        themes_line = ", ".join([f"{t.theme} ({t.mention_count} mentions)" for t in top_themes])
        actions = " ".join([f"{idx+1}) {idea}" for idx, idea in enumerate(action_ideas[:3])])
        return (
            f"This week’s customer pulse highlights {themes_line}. "
            f"Overall sentiment score is {sentiment_score}. "
            f"Recommended actions: {actions}"
        )


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def _slug(text: str) -> str:
    return text.lower().replace(" ", "-")


def _theme_distribution(themes: List[ThemeResult]) -> List[Dict[str, Any]]:
    total = sum(t.mention_count for t in themes) or 1
    return [
        {
            "theme": t.theme,
            "count": t.mention_count,
            "percentage": round((t.mention_count / total) * 100, 2),
        }
        for t in themes
    ]
