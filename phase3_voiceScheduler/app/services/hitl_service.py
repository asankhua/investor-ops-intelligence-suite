"""HITL queue and booking orchestration service for Phase 3."""

from __future__ import annotations

from datetime import datetime, timedelta
import os
from typing import Any, Dict, List
import uuid

from .state_store import StateStore
from .theme_provider import ThemeProvider
from .mcp_client import MCPClient


class HITLService:
    def __init__(self, state_store: StateStore, theme_provider: ThemeProvider):
        self.state_store = state_store
        self.theme_provider = theme_provider
        self.mcp_client = MCPClient()

    def generate_booking_code(self) -> str:
        return f"MTG-{datetime.utcnow().year}-{str(uuid.uuid4().int % 1000).zfill(3)}"

    def create_booking_actions(
        self,
        user_text: str,
        topic: str = "General Support",
        slot_datetime: str | None = None,
        meet_url: str | None = None,
        mcp_status: Dict[str, str] | None = None,
        booking_code: str | None = None,
    ) -> Dict[str, Any]:
        booking_code = booking_code or self.generate_booking_code()
        scheduled_for = (
            datetime.fromisoformat(slot_datetime.replace("Z", "+00:00"))
            if slot_datetime
            else (datetime.utcnow() + timedelta(days=1)).replace(hour=15, minute=0, second=0, microsecond=0)
        )
        resolved_meet_url = meet_url or os.getenv("GOOGLE_MEET_URL") or f"https://meet.google.com/{booking_code.lower().replace('-', '')}"
        tool_status = mcp_status or {"calendar": "ok", "doc": "ok", "mail": "ok"}

        # Fetch full weekly pulse for rich email context
        pulse = self.theme_provider.get_weekly_pulse()
        themes = pulse.get("top_themes") or self.theme_provider.get_top_themes()
        summary = pulse.get("summary", "")
        action_ideas = pulse.get("action_ideas", [])
        sentiment_score = pulse.get("sentiment_score")
        generated_at = pulse.get("generated_at", "")

        # Build theme lines with sentiment
        theme_lines = "\n".join([
            f"  • {t.get('theme')} — confidence {int(t.get('confidence', 0) * 100)}%, "
            f"mentions {t.get('mention_count', '-')}, "
            f"sentiment {t.get('sentiment_score', '-')}"
            for t in themes[:3]
        ]) or "  • No themes available"

        action_lines = "\n".join([f"  {i+1}. {a}" for i, a in enumerate(action_ideas)]) or "  • N/A"
        market_context = ", ".join([t.get("theme", "") for t in themes[:3] if t.get("theme")]) or "General market context"

        email_body = (
            f"Dear Advisor,\n\n"
            f"A meeting has been scheduled and requires your review.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"BOOKING DETAILS\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Booking Code : {booking_code}\n"
            f"Topic        : {topic}\n"
            f"Date & Time  : {scheduled_for.strftime('%B %d, %Y at %I:%M %p UTC')}\n"
            f"Google Meet  : {resolved_meet_url}\n"
            f"Customer     : [REDACTED]\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"WEEKLY PULSE CONTEXT\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            + (f"Generated    : {generated_at}\n" if generated_at else "")
            + (f"Sentiment    : {sentiment_score}\n" if sentiment_score is not None else "")
            + f"\nTop Themes:\n{theme_lines}\n\n"
            + (f"Summary:\n  {summary}\n\n" if summary else "")
            + f"Recommended Actions:\n{action_lines}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"MCP Status   : calendar={tool_status.get('calendar')}, "
            f"doc={tool_status.get('doc')}, mail={tool_status.get('mail')}\n\n"
            f"Please review and approve in the HITL Approval Center.\n"
        )
        advisor_email = os.getenv("ADVISOR_EMAIL", "").strip()
        tracking_doc_id = os.getenv("GOOGLE_TRACKING_DOC_ID", "").strip()
        tracking_doc_link = f"https://docs.google.com/document/d/{tracking_doc_id}/edit" if tracking_doc_id else ""

        email_draft = {
            "to": advisor_email,
            "from": os.getenv("NOTIFY_FROM_EMAIL", "noreply@investorsuite.com"),
            "subject": f"Meeting Scheduled - {booking_code}",
            "body": email_body,
            "context": market_context,
            "tracking_doc": tracking_doc_link,
        }

        calendar_action = {
            "id": f"action-{uuid.uuid4().hex[:12]}",
            "type": "calendar",
            "booking_code": booking_code,
            "details": {
                "datetime": f"{scheduled_for.strftime('%Y-%m-%dT%H:%M:%SZ')}",
                "duration_minutes": 30,
                    "meet_url": resolved_meet_url,
                    "topic": topic,
            },
            "status": "pending",
            "requested_at": datetime.utcnow().isoformat() + "Z",
        }
        email_action = {
            "id": f"action-{uuid.uuid4().hex[:12]}",
            "type": "email",
            "booking_code": booking_code,
            "details": {"subject": email_draft["subject"], "to": email_draft["to"]},
            "status": "pending",
            "requested_at": datetime.utcnow().isoformat() + "Z",
        }

        def updater(state):
            state["bookings"].append(
                {
                    "booking_code": booking_code,
                    "status": "pending_approval",
                    "scheduled_for": calendar_action["details"]["datetime"],
                    "meet_url": resolved_meet_url,
                    "user_request": user_text,
                    "topic": topic,
                    "mcp_status": tool_status,
                }
            )
            state["pending_actions"].extend([calendar_action, email_action])
            state["email_drafts"][booking_code] = email_draft

        self.state_store.update(updater)
        return {
            "booking_code": booking_code,
            "status": "pending_approval",
            "meet_url": resolved_meet_url,
            "scheduled_for": calendar_action["details"]["datetime"],
            "topic": topic,
            "mcp_status": tool_status,
        }

    def get_pending_actions(self) -> List[Dict[str, Any]]:
        state = self.state_store.get_state()
        return [a for a in state["pending_actions"] if a.get("status") == "pending"]

    def get_all_actions(self) -> List[Dict[str, Any]]:
        state = self.state_store.get_state()
        actions = state.get("pending_actions", [])
        if not isinstance(actions, list):
            return []
        return actions

    def approve_action(self, action_id: str) -> Dict[str, Any]:
        result = {"status": "not_found"}
        approved_action = None

        def updater(state):
            nonlocal result, approved_action
            for action in state["pending_actions"]:
                if action["id"] == action_id:
                    action["status"] = "approved"
                    action["approved_at"] = datetime.utcnow().isoformat() + "Z"
                    result = {"status": "approved", "action_id": action_id}
                    approved_action = action
                    break

        self.state_store.update(updater)

        # Fire MCP calls on approval
        if approved_action:
            booking_code = approved_action.get("booking_code", "")
            state = self.state_store.get_state()
            draft = state["email_drafts"].get(booking_code, {})
            details = approved_action.get("details", {})

            if approved_action.get("type") == "email" and draft:
                email_body = draft.get("body", "")
                mcp_result = self.mcp_client.send_email(
                    booking_code,
                    details.get("topic", "Advisor Call"),
                    details.get("datetime", ""),
                    draft.get("meet_url", os.getenv("GOOGLE_MEET_URL", "")),
                    draft.get("to", ""),
                    body=email_body,
                )
                result["email_draft"] = mcp_result
                doc_result = self.mcp_client.append_notes(
                    booking_code,
                    details.get("topic", "Advisor Call"),
                    details.get("datetime", ""),
                    draft.get("meet_url", os.getenv("GOOGLE_MEET_URL", "")),
                    email_body=email_body,
                )
                result["doc_append"] = doc_result

            if approved_action.get("type") == "calendar":
                doc_result = self.mcp_client.append_notes(
                    booking_code,
                    details.get("topic", "Advisor Call"),
                    details.get("datetime", ""),
                    details.get("meet_url", os.getenv("GOOGLE_MEET_URL", "")),
                )
                result["doc_append"] = doc_result

        return result

    def reject_action(self, action_id: str, reason: str | None = None) -> Dict[str, Any]:
        result = {"status": "not_found"}

        def updater(state):
            nonlocal result
            for action in state["pending_actions"]:
                if action["id"] == action_id:
                    action["status"] = "rejected"
                    action["rejected_at"] = datetime.utcnow().isoformat() + "Z"
                    action["reason"] = reason or "Rejected by reviewer"
                    result = {"status": "rejected", "action_id": action_id}
                    break

        self.state_store.update(updater)
        return result

    def get_email_preview(self, booking_code: str) -> Dict[str, Any]:
        state = self.state_store.get_state()
        draft = state["email_drafts"].get(booking_code)
        if not draft:
            return {"status": "not_found", "booking_code": booking_code}
        tracking_doc_id = os.getenv("GOOGLE_TRACKING_DOC_ID", "").strip()
        tracking_doc_link = f"https://docs.google.com/document/d/{tracking_doc_id}/edit" if tracking_doc_id else ""
        if draft.get("tracking_doc") in {"", "<configured_tracking_doc_url>"} and tracking_doc_link:
            draft["tracking_doc"] = tracking_doc_link
        return draft

    def edit_email_draft(self, booking_code: str, subject: str | None, body: str | None) -> Dict[str, Any]:
        updated = {}

        def updater(state):
            nonlocal updated
            draft = state["email_drafts"].get(booking_code)
            if not draft:
                updated = {"status": "not_found", "booking_code": booking_code}
                return
            if subject is not None:
                draft["subject"] = subject
            if body is not None:
                draft["body"] = body
            updated = draft

        self.state_store.update(updater)
        return updated

    def send_email(self, booking_code: str) -> Dict[str, Any]:
        state = self.state_store.get_state()
        draft = state["email_drafts"].get(booking_code)
        if not draft:
            return {"status": "not_found", "booking_code": booking_code}

        # Find booking details for doc append
        booking = next((b for b in state.get("bookings", []) if b.get("booking_code") == booking_code), {})
        meet_url = booking.get("meet_url") or os.getenv("GOOGLE_MEET_URL", "")
        slot_datetime = booking.get("scheduled_for", "")
        topic = booking.get("topic", "Advisor Call")

        # Send email draft via MCP
        email_result = self.mcp_client.send_email(
            booking_code, topic, slot_datetime, meet_url, draft.get("to", ""),
            body=draft.get("body", "")
        )

        # Append full email body to tracking doc via MCP
        doc_result = self.mcp_client.append_notes(
            booking_code, topic, slot_datetime, meet_url,
            email_body=draft.get("body", "")
        )

        # Mark email action as approved
        def updater(s):
            for action in s.get("pending_actions", []):
                if action.get("booking_code") == booking_code and action.get("type") == "email":
                    action["status"] = "approved"
                    action["approved_at"] = datetime.utcnow().isoformat() + "Z"

        self.state_store.update(updater)

        return {
            "status": "sent",
            "booking_code": booking_code,
            "email_draft": email_result,
            "doc_append": doc_result,
        }
