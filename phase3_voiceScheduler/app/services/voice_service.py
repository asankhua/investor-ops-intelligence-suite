"""Voice scheduling service with state-machine and MCP orchestration."""

from __future__ import annotations

import base64
from datetime import datetime, timedelta
import re
import uuid
from typing import Any, Dict, List, Tuple

import requests

from .state_store import DEFAULT_PIPELINE, StateStore
from .theme_provider import ThemeProvider
from .hitl_service import HITLService
from .mcp_client import MCPClient

VALID_TOPICS = {
    "kyc": "KYC/Onboarding",
    "onboarding": "KYC/Onboarding",
    "sip": "SIP/Mandates",
    "mandate": "SIP/Mandates",
    "statement": "Statements/Tax Docs",
    "tax": "Statements/Tax Docs",
    "withdraw": "Withdrawals",
    "redeem": "Withdrawals",
    "account change": "Account Changes",
    "nominee": "Account Changes",
}


class VoiceService:
    def __init__(self, state_store: StateStore, theme_provider: ThemeProvider, hitl_service: HITLService):
        self.state_store = state_store
        self.theme_provider = theme_provider
        self.hitl_service = hitl_service
        self.mcp_client = MCPClient()

    def _set_step(self, step: str, status: str) -> None:
        def updater(state):
            state["pipeline_status"][step] = status

        self.state_store.update(updater)

    def reset_pipeline(self) -> None:
        def updater(state):
            state["pipeline_status"] = dict(DEFAULT_PIPELINE)

        self.state_store.update(updater)

    def _default_conversation_state(self) -> Dict[str, Any]:
        return {
            "id": str(uuid.uuid4())[:8],
            "state": "greeting",
            "topic": None,
            "selected_slot": None,
            "available_slots": [],
            "booking_code": None,
        }

    def _detect_topic(self, text_lower: str) -> str | None:
        # Prefer weekly pulse themes over static taxonomy.
        theme_topic = self._detect_theme_topic(text_lower)
        if theme_topic:
            return theme_topic
        for key, value in VALID_TOPICS.items():
            if key in text_lower:
                return value
        return None

    def _detect_theme_topic(self, text_lower: str) -> str | None:
        for theme in self.theme_provider.get_top_themes():
            name = str(theme.get("theme") or "").strip()
            if not name:
                continue
            if name.lower() in text_lower:
                return name
            for token in [p for p in re.split(r"[^a-zA-Z0-9]+", name.lower()) if len(p) >= 4]:
                if token in text_lower:
                    return name
        return None

    def _theme_prompt(self) -> str:
        themes = self.theme_provider.get_top_themes()
        names = [str(t.get("theme") or "").strip() for t in themes if str(t.get("theme") or "").strip()]
        if names:
            return ", ".join(names[:3])
        return "your latest weekly pulse themes"

    def _is_investment_advice(self, text_lower: str) -> bool:
        return any(token in text_lower for token in ["which fund", "best fund", "buy", "sell", "recommend", "invest in"])

    def _contains_pii(self, text: str) -> bool:
        return bool(re.search(r"\b\d{10}\b", text) or "@" in text or re.search(r"\b[A-Z]{5}\d{4}[A-Z]\b", text))

    def _offer_slots(self) -> List[Dict[str, str]]:
        tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
        return [
            {"id": "slot1", "datetime": f"{tomorrow}T10:00:00Z"},
            {"id": "slot2", "datetime": f"{tomorrow}T14:00:00Z"},
        ]

    def _fmt_slot(self, dt: str) -> str:
        parsed = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        return parsed.strftime("%I:%M %p, %B %d")

    def _transcribe_audio_base64(self, audio_base64: str) -> str:
        try:
            audio_bytes = base64.b64decode(audio_base64)
        except Exception as exc:
            raise ValueError("Invalid audio payload") from exc

        # Read from env each call so runtime changes are picked up.
        import os
        sarvam_key = os.getenv("SARVAM_API_KEY", "").strip()
        if not sarvam_key:
            raise RuntimeError("SARVAM_API_KEY is missing for voice transcription")

        try:
            response = requests.post(
                "https://api.sarvam.ai/speech-to-text",
                headers={"api-subscription-key": sarvam_key},
                files={"file": ("audio.webm", audio_bytes, "audio/webm")},
                data={"model": "saaras:v3", "language_code": "en-IN", "with_timestamps": "false"},
                timeout=30,
            )
            if not response.ok:
                raise RuntimeError(f"Sarvam STT failed with status {response.status_code}")
            transcript = (response.json().get("transcript") or "").strip()
            if not transcript:
                raise RuntimeError("No speech detected in audio")
            return transcript
        except requests.RequestException as exc:
            raise RuntimeError("Voice transcription request failed") from exc

    def start_recording(self, session_id: str | None = None) -> Dict[str, Any]:
        self.reset_pipeline()
        self._set_step("VAD", "active")
        recording_id = f"rec-{uuid.uuid4().hex[:10]}"

        def updater(state):
            state["recordings"][recording_id] = {
                "recording_id": recording_id,
                "session_id": session_id,
                "status": "recording",
                "started_at": datetime.utcnow().isoformat() + "Z",
            }

        self.state_store.update(updater)
        return {"recording_id": recording_id, "stream_url": f"wss://voice.local/{recording_id}", "status": "recording"}

    def stop_recording(self, recording_id: str) -> Dict[str, Any]:
        self._set_step("VAD", "done")
        self._set_step("STT", "active")
        self._set_step("STT", "done")
        return {
            "recording_id": recording_id,
            "audio_url": f"/api/v1/pillar-c/voice/play/{recording_id}",
            "duration": 5.2,
            "status": "stopped",
        }

    def cancel_recording(self, recording_id: str) -> Dict[str, Any]:
        self.reset_pipeline()

        def updater(state):
            if recording_id in state["recordings"]:
                state["recordings"][recording_id]["status"] = "cancelled"
                state["recordings"][recording_id]["cancelled_at"] = datetime.utcnow().isoformat() + "Z"

        self.state_store.update(updater)
        return {"status": "cancelled", "recording_id": recording_id}

    def _run_state_machine(self, text: str, conv: Dict[str, Any]) -> Tuple[str, Dict[str, Any] | None, Dict[str, Any], Dict[str, str]]:
        lower = text.lower()
        mcp_status = {"calendar": "idle", "doc": "idle", "mail": "idle"}

        if lower in {"hello", "hi", "hey", "reset", "start over"}:
            conv = self._default_conversation_state()
            conv["state"] = "topic_detection"
            return (
                "Hello! This call is informational only and not investment advice. "
                f"Which Weekly Product Pulse theme do you need help with: {self._theme_prompt()}?",
                None,
                conv,
                mcp_status,
            )

        if self._contains_pii(text):
            return (
                "For your security, please don't share personal details on this call. "
                f"Please continue with one of the latest Weekly Product Pulse themes: {self._theme_prompt()}.",
                None,
                conv,
                mcp_status,
            )

        if conv.get("state") == "greeting":
            conv["state"] = "topic_detection"
            return (
                "Hello! This call is informational only and not investment advice. "
                f"Which Weekly Product Pulse theme do you need help with: {self._theme_prompt()}?",
                None,
                conv,
                mcp_status,
            )

        if conv.get("state") == "topic_detection":
            topic = self._detect_topic(lower)
            if self._is_investment_advice(lower):
                conv["state"] = "booking_interest"
                return (
                    "I cannot provide investment recommendations. I can book a human advisor appointment for you. "
                    "Would you like to continue?",
                    None,
                    conv,
                    mcp_status,
                )
            if not topic:
                return (f"Please mention one valid Weekly Product Pulse theme: {self._theme_prompt()}.", None, conv, mcp_status)
            conv["topic"] = topic
            conv["available_slots"] = self._offer_slots()
            conv["state"] = "confirm_slot"
            first = self._fmt_slot(conv["available_slots"][0]["datetime"])
            second = self._fmt_slot(conv["available_slots"][1]["datetime"])
            return (f"I can help with {topic}. I have two slots: {first} or {second}. Say first/second/yes.", None, conv, mcp_status)

        if conv.get("state") == "booking_interest":
            if any(token in lower for token in ["yes", "sure", "ok", "book"]):
                conv["available_slots"] = self._offer_slots()
                conv["state"] = "confirm_slot"
                first = self._fmt_slot(conv["available_slots"][0]["datetime"])
                second = self._fmt_slot(conv["available_slots"][1]["datetime"])
                return (f"Great. Available slots are {first} or {second}. Say first/second/yes.", None, conv, mcp_status)
            return ("Please say yes to proceed with booking, or no to cancel.", None, conv, mcp_status)

        if conv.get("state") == "confirm_slot":
            slots = conv.get("available_slots", [])
            if not slots:
                conv["available_slots"] = self._offer_slots()
                slots = conv["available_slots"]
            if any(token in lower for token in ["first", "yes"]):
                selected = slots[0]
            elif "second" in lower:
                selected = slots[1]
            else:
                return ("Please say first, second, or yes to confirm booking.", None, conv, mcp_status)

            conv["selected_slot"] = selected["datetime"]
            booking_code = self.hitl_service.generate_booking_code()
            conv["booking_code"] = booking_code

            self._set_step("Calendar", "active")
            cal = self.mcp_client.create_calendar_event(conv.get("topic") or "General Support", booking_code, selected["datetime"])
            mcp_status["calendar"] = "ok" if cal.get("success") else "error"
            self._set_step("Calendar", "done")

            meet_link = cal.get("meet_link") or os.getenv("GOOGLE_MEET_URL") or f"https://meet.google.com/{booking_code.lower().replace('-', '')}"
            self._set_step("Doc", "active")
            note = self.mcp_client.append_notes(booking_code, conv.get("topic") or "General Support", selected["datetime"], meet_link)
            mcp_status["doc"] = "ok" if note.get("success") else "error"
            self._set_step("Doc", "done")

            # Email draft is created on HITL approval — not here
            mcp_status["mail"] = "pending_approval"
            self._set_step("Email", "active")
            self._set_step("Email", "done")

            booking = self.hitl_service.create_booking_actions(
                text,
                topic=conv.get("topic") or "General Support",
                slot_datetime=selected["datetime"],
                meet_url=meet_link,
                mcp_status=mcp_status,
                booking_code=booking_code,
            )
            conv["state"] = "complete"
            response = (
                f"Perfect! Your appointment is confirmed. Booking code: {booking_code}. "
                f"Meet link: {meet_link}. Calendar, notes, and advisor email are queued for HITL approval."
            )
            return response, booking, conv, mcp_status

        # complete or fallback
        conv["state"] = "topic_detection"
        return (
            "Your booking flow is complete. If you need another request, please share one "
            f"Weekly Product Pulse theme ({self._theme_prompt()}).",
            None,
            conv,
            mcp_status,
        )

    def process_message(self, message: str) -> Dict[str, Any]:
        text = (message or "").strip()
        if not text:
            return {"response_text": "Please provide a message.", "booking": None}

        self.reset_pipeline()
        self._set_step("VAD", "done")
        self._set_step("STT", "done")
        self._set_step("LLM", "active")
        state = self.state_store.get_state()
        conv = state.get("conversation_state") or self._default_conversation_state()

        response_text, booking, updated_conv, mcp_status = self._run_state_machine(text, conv)

        themes = self.theme_provider.get_top_themes()
        top_theme = themes[0] if themes else None

        self._set_step("LLM", "done")
        self._set_step("TTS", "active")
        self._set_step("TTS", "done")

        def updater(state_obj):
            state_obj["conversation_state"] = updated_conv
            state_obj["messages"].append({"role": "user", "text": text, "timestamp": datetime.utcnow().isoformat() + "Z"})
            state_obj["messages"].append({"role": "agent", "text": response_text, "timestamp": datetime.utcnow().isoformat() + "Z"})
            state_obj["mcp_calls"].append(
                {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "booking_code": (booking or {}).get("booking_code"),
                    "status": mcp_status,
                }
            )

        self.state_store.update(updater)
        return {
            "response_text": response_text,
            "booking": booking,
            "mcp_status": mcp_status,
            "theme_context": {
                "top_theme": top_theme.get("theme") if top_theme else None,
                "confidence": top_theme.get("confidence") if top_theme else None,
            },
        }

    def process_voice_message(self, audio_base64: str) -> Dict[str, Any]:
        self.reset_pipeline()
        self._set_step("VAD", "active")
        self._set_step("VAD", "done")
        self._set_step("STT", "active")
        transcript = self._transcribe_audio_base64(audio_base64)
        self._set_step("STT", "done")
        payload = self.process_message(transcript)
        payload["transcript"] = transcript
        return payload

    def get_pipeline_status(self) -> Dict[str, Any]:
        state = self.state_store.get_state()
        steps = [{"id": k, "status": v} for k, v in state["pipeline_status"].items()]
        active = next((s["id"] for s in steps if s["status"] == "active"), None)
        overall = "active" if active else "idle"
        return {"current_step": active, "steps": steps, "status": overall}
