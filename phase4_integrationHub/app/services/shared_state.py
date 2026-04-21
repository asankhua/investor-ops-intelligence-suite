"""Cross-pillar shared state storage for Phase 4."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class SharedStateStore:
    def __init__(self, state_file: Path, phase2_pulse_file: Path):
        self._state_file = state_file
        self._phase2_pulse_file = phase2_pulse_file
        self._lock = Lock()
        self._state = self._load()

    def _load(self) -> Dict[str, Any]:
        if self._state_file.exists():
            try:
                return json.loads(self._state_file.read_text())
            except Exception:
                pass
        return {
            "active_bookings": [],
            "booking_to_pulse_map": {},
            "weekly_pulse": {"booking_refs": []},
            "sync_events": [],
        }

    def _save(self) -> None:
        self._state_file.parent.mkdir(parents=True, exist_ok=True)
        self._state_file.write_text(json.dumps(self._state, indent=2))

    def get_state(self) -> Dict[str, Any]:
        with self._lock:
            return json.loads(json.dumps(self._state))

    def get_booking_refs(self) -> List[Dict[str, Any]]:
        return self.get_state().get("weekly_pulse", {}).get("booking_refs", [])

    def sync_booking(self, booking_code: str, pulse_context: Dict[str, Any], source: str = "pillar-c") -> Dict[str, Any]:
        with self._lock:
            if booking_code not in self._state["active_bookings"]:
                self._state["active_bookings"].append(booking_code)

            entry = {
                "booking_code": booking_code,
                "source": source,
                "synced_at": _now_iso(),
                "pulse_context": pulse_context,
            }
            refs = self._state["weekly_pulse"]["booking_refs"]
            if not any(item.get("booking_code") == booking_code for item in refs):
                refs.append(entry)

            self._state["booking_to_pulse_map"][booking_code] = pulse_context
            self._state["sync_events"].append({"booking_code": booking_code, "timestamp": _now_iso(), "status": "synced"})
            self._save()

            self._sync_to_phase2_pulse(booking_code, pulse_context)
            return json.loads(json.dumps(entry))

    def _sync_to_phase2_pulse(self, booking_code: str, pulse_context: Dict[str, Any]) -> None:
        if not self._phase2_pulse_file.exists():
            return
        try:
            payload = json.loads(self._phase2_pulse_file.read_text())
            payload.setdefault("booking_refs", [])
            if not any(item.get("booking_code") == booking_code for item in payload["booking_refs"]):
                payload["booking_refs"].append(
                    {"booking_code": booking_code, "context": pulse_context, "synced_at": _now_iso()}
                )
                self._phase2_pulse_file.write_text(json.dumps(payload, indent=2))
        except Exception:
            # Do not fail gateway request on non-critical sync path.
            return
