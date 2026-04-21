"""In-memory + file-backed state store for Phase 3 APIs."""

from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Any, Dict


DEFAULT_PIPELINE = {
    "VAD": "idle",
    "STT": "idle",
    "LLM": "idle",
    "TTS": "idle",
    "Calendar": "idle",
    "Doc": "idle",
    "Email": "idle",
}


class StateStore:
    def __init__(self, state_file: Path):
        self._state_file = state_file
        self._lock = Lock()
        self._state: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        defaults = {
            "recordings": {},
            "messages": [],
            "bookings": [],
            "pending_actions": [],
            "pipeline_status": dict(DEFAULT_PIPELINE),
            "email_drafts": {},
            "conversation_state": {
                "id": None,
                "state": "greeting",
                "topic": None,
                "selected_slot": None,
                "available_slots": [],
                "booking_code": None,
            },
            "mcp_calls": [],
        }
        if self._state_file.exists():
            try:
                loaded = json.loads(self._state_file.read_text())
                if isinstance(loaded, dict):
                    merged = dict(defaults)
                    merged.update(loaded)
                    merged["pipeline_status"] = {**dict(DEFAULT_PIPELINE), **(loaded.get("pipeline_status") or {})}
                    if not isinstance(merged.get("conversation_state"), dict):
                        merged["conversation_state"] = defaults["conversation_state"]
                    return merged
            except Exception:
                pass
        return defaults

    def _save(self) -> None:
        self._state_file.parent.mkdir(parents=True, exist_ok=True)
        self._state_file.write_text(json.dumps(self._state, indent=2))

    def get_state(self) -> Dict[str, Any]:
        with self._lock:
            return json.loads(json.dumps(self._state))

    def update(self, updater) -> Dict[str, Any]:
        with self._lock:
            updater(self._state)
            self._save()
            return json.loads(json.dumps(self._state))
