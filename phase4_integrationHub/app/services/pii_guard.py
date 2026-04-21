"""PII masking utilities for Phase 4 gateway."""

from __future__ import annotations

import re
from typing import Any, Dict, List


class PIIGuard:
    PATTERNS = [
        (re.compile(r"\S+@\S+\.\S+"), "[REDACTED_EMAIL]"),
        (re.compile(r"\b\d{10,12}\b"), "[REDACTED_PHONE]"),
        (re.compile(r"\d{4}[ -]?\d{4}[ -]?\d{4}"), "[REDACTED_AADHAR]"),
        (re.compile(r"[A-Z]{5}[0-9]{4}[A-Z]"), "[REDACTED_PAN]"),
        (re.compile(r"\b\d{9,18}\b"), "[REDACTED_ACCT]"),
    ]

    def mask_text(self, text: str) -> str:
        masked = text
        for pattern, replacement in self.PATTERNS:
            masked = pattern.sub(replacement, masked)
        return masked

    def mask(self, value: Any) -> Any:
        if isinstance(value, str):
            return self.mask_text(value)
        if isinstance(value, list):
            return [self.mask(v) for v in value]
        if isinstance(value, dict):
            return {k: self.mask(v) for k, v in value.items()}
        return value

    def has_unmasked_pii(self, value: Any) -> bool:
        if isinstance(value, str):
            return any(pattern.search(value) for pattern, _ in self.PATTERNS)
        if isinstance(value, list):
            return any(self.has_unmasked_pii(v) for v in value)
        if isinstance(value, dict):
            return any(self.has_unmasked_pii(v) for v in value.values())
        return False
