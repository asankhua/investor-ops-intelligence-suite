"""Theme context provider for Phase 3 greeting enrichment."""

from __future__ import annotations

import os
from typing import Any, Dict, List

import requests


class ThemeProvider:
    def __init__(self):
        self.phase2_base_url = os.getenv("PHASE2_BASE_URL", "http://localhost:8102")

    def get_top_themes(self) -> List[Dict[str, Any]]:
        try:
            resp = requests.get(f"{self.phase2_base_url}/api/v1/pillar-b/themes", timeout=2.5)
            if resp.ok:
                payload = resp.json()
                if isinstance(payload, list):
                    return payload
                if isinstance(payload, dict):
                    return payload.get("themes", [])
        except Exception:
            pass
        return []

    def get_weekly_pulse(self) -> Dict[str, Any]:
        try:
            resp = requests.get(f"{self.phase2_base_url}/api/v1/pillar-b/weekly-pulse", timeout=2.5)
            if resp.ok:
                return resp.json()
        except Exception:
            pass
        return {}

    def get_greeting(self) -> str:
        themes = self.get_top_themes()
        if themes and float(themes[0].get("confidence", 0.0)) >= 0.7:
            return (
                f"Hello! I see many users are asking about {themes[0]['theme']} today. "
                "I can help you schedule a meeting."
            )
        return "Hello! How can I help you schedule a meeting today?"
