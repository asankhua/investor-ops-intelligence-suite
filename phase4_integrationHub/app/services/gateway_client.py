"""HTTP gateway client for routing requests to phase services."""

from __future__ import annotations

import os
import re
from typing import Any, Dict, Optional, Tuple

import requests

from .pii_guard import PIIGuard


class GatewayClient:
    def __init__(self) -> None:
        self.phase1_base_url = os.getenv("PHASE1_BASE_URL", "http://localhost:8000")
        self.phase2_base_url = os.getenv("PHASE2_BASE_URL", "http://localhost:8002")
        self.phase3_base_url = os.getenv("PHASE3_BASE_URL", "http://localhost:8001")
        self.timeout_s = float(os.getenv("GATEWAY_TIMEOUT_S", "20"))
        self.guard = PIIGuard()

    def parse_booking_code(self, payload: Any) -> Optional[str]:
        haystack = str(payload)
        match = re.search(r"(MTG-\d{4}-\d{3,})", haystack)
        return match.group(1) if match else None

    def get(
        self,
        phase: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        mask_response: bool = True,
    ) -> Tuple[int, Dict[str, Any]]:
        return self._request("GET", phase, path, params=params, mask_response=mask_response)

    def post(
        self,
        phase: str,
        path: str,
        json_body: Optional[Dict[str, Any]] = None,
        mask_response: bool = True,
    ) -> Tuple[int, Dict[str, Any]]:
        return self._request("POST", phase, path, json_body=json_body, mask_response=mask_response)

    def _request(
        self,
        method: str,
        phase: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        mask_response: bool = True,
    ) -> Tuple[int, Dict[str, Any]]:
        base = self._base_url(phase)
        if base is None:
            return 400, {"error": "invalid_phase", "message": f"Unknown phase: {phase}"}

        url = f"{base}{path}"
        safe_params = self.guard.mask(params or {})
        safe_body = self.guard.mask(json_body) if json_body is not None else None

        try:
            response = requests.request(
                method,
                url,
                params=safe_params if safe_params else None,
                json=safe_body if json_body is not None else None,
                timeout=self.timeout_s,
            )
            try:
                payload = response.json()
            except Exception:
                payload = {"raw": response.text}

            safe_payload = self.guard.mask(payload) if mask_response else payload
            return response.status_code, safe_payload if isinstance(safe_payload, dict) else {"data": safe_payload}
        except requests.RequestException:
            return 503, {
                "error": "service_unavailable",
                "message": f"{phase} service is temporarily unavailable. Please try again in a few minutes.",
                "phase": phase,
            }

    def _base_url(self, phase: str) -> Optional[str]:
        if phase == "phase1":
            return self.phase1_base_url
        if phase == "phase2":
            return self.phase2_base_url
        if phase == "phase3":
            return self.phase3_base_url
        return None
