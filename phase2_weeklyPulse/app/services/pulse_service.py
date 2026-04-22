"""Weekly pulse orchestrator and persistence."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import threading
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
        self.scheduler_state_file = self.storage_dir / "scheduler_state.json"
        self.loader = ReviewLoader(repo_root)
        self.scheduler_interval_days = max(1, int(os.getenv("PULSE_SCHEDULER_INTERVAL_DAYS", "7")))
        self._refresh_lock = threading.Lock()

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def refresh(self, fetch_live_reviews: bool = True) -> Dict[str, Any]:
        with self._refresh_lock:
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

    def get_scheduler_status(self) -> Dict[str, Any]:
        state = self._load_scheduler_state()
        last_run = state.get("last_run_at")
        next_run = self._next_run_at(last_run)
        source_cfg = self.loader.source_config()
        return {
            "enabled": True,
            "interval_days": self.scheduler_interval_days,
            "last_run_at": last_run,
            "next_run_at": next_run,
            "last_status": state.get("last_status", "never_run"),
            "last_error": state.get("last_error"),
            "last_reviews_source": state.get("last_reviews_source"),
            "last_reviews_processed": state.get("last_reviews_processed", 0),
            "review_urls": source_cfg.get("review_urls", []),
            "app_ids": source_cfg.get("app_ids", []),
            "updated_at": state.get("updated_at"),
        }

    def run_scheduler_if_due(self) -> Dict[str, Any]:
        state = self._load_scheduler_state()
        now = datetime.now(timezone.utc)
        last_run = _parse_iso(state.get("last_run_at"))
        due = last_run is None or (now - last_run).days >= self.scheduler_interval_days
        if not due:
            return {"status": "skipped", "reason": "not_due", "next_run_at": self._next_run_at(state.get("last_run_at"))}

        try:
            pulse = self.refresh(fetch_live_reviews=True)
            updated = {
                **state,
                "last_run_at": pulse.get("generated_at"),
                "last_status": "success",
                "last_error": None,
                "last_reviews_source": pulse.get("reviews_source"),
                "last_reviews_processed": pulse.get("raw_reviews_processed", 0),
                "updated_at": self._now(),
            }
            self._save_scheduler_state(updated)
            return {"status": "success", "generated_at": pulse.get("generated_at")}
        except Exception as exc:
            updated = {
                **state,
                "last_status": "failed",
                "last_error": str(exc),
                "updated_at": self._now(),
            }
            self._save_scheduler_state(updated)
            return {"status": "failed", "error": str(exc)}

    def _load_scheduler_state(self) -> Dict[str, Any]:
        defaults = {
            "last_run_at": None,
            "last_status": "never_run",
            "last_error": None,
            "last_reviews_source": None,
            "last_reviews_processed": 0,
            "updated_at": None,
        }
        if not self.scheduler_state_file.exists():
            return defaults
        try:
            payload = json.loads(self.scheduler_state_file.read_text())
            if isinstance(payload, dict):
                merged = dict(defaults)
                merged.update(payload)
                return merged
        except Exception:
            pass
        return defaults

    def _save_scheduler_state(self, state: Dict[str, Any]) -> None:
        self.scheduler_state_file.write_text(json.dumps(state, indent=2))

    def _next_run_at(self, last_run_at: Optional[str]) -> Optional[str]:
        if not last_run_at:
            return None
        dt = _parse_iso(last_run_at)
        if not dt:
            return None
        next_dt = dt + _days(self.scheduler_interval_days)
        return next_dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")

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


def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def _days(value: int):
    from datetime import timedelta

    return timedelta(days=value)
