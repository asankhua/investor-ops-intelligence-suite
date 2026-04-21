# MCP Integration - Phase 3 Voice Scheduler

## Overview

MCP (Model Context Protocol) integration handles doc append and email draft creation via the HuggingFace-hosted MCP server after a booking is confirmed and approved through HITL.

**MCP Server**: https://ashishsankhua-google-docs-gmail-mcp-server.hf.space

---

## MCP Server Endpoints

| Endpoint | Method | Payload | Description |
|----------|--------|---------|-------------|
| `/tools` | GET | — | List available tools |
| `/append_to_doc` | POST | `{doc_id, content}` | Append to Google Doc |
| `/create_email_draft` | POST | `{to, subject, body}` | Create Gmail draft |

---

## Booking Flow

```
User says "support and service" + "first"
  │
  ▼
voice_service.py: _run_state_machine()
  ├── create_calendar_event() → returns meet_link (GOOGLE_MEET_URL)
  ├── append_notes() → POST /append_to_doc (booking summary)
  └── mcp_status["mail"] = "pending_approval"
  │
  ▼
hitl_service.py: create_booking_actions()
  ├── Fetches full Weekly Pulse (themes, sentiment, summary, actions)
  ├── Builds rich email body with booking details + pulse context
  └── Stores in state: email_drafts[booking_code]
  │
  ▼
HITL Table shows booking as "pending"
  │
  ▼
User clicks "Mark Done" (approve)
  │
  ▼
hitl_service.py: approve_action()
  ├── POST /create_email_draft → Gmail draft with full email body
  └── POST /append_to_doc → Google Doc with full email body
```

---

## Email Body Structure

The email sent to `ADVISOR_EMAIL` includes:

```
BOOKING DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Booking Code : MTG-2026-XXX
Topic        : Support & Service
Date & Time  : April 22, 2026 at 10:00 AM UTC
Google Meet  : https://meet.google.com/mgq-xoua-egx?authuser=0
Customer     : [REDACTED]

WEEKLY PULSE CONTEXT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated    : 2026-04-21T...
Sentiment    : -0.223

Top Themes:
  • Feature Requests — confidence 80%, mentions 19, sentiment -0.186
  • Support & Service — confidence 71%, mentions 9, sentiment -0.406
  • Performance & Stability — confidence 67%, mentions 6, sentiment -0.078

Summary:
  This week's customer pulse highlights...

Recommended Actions:
  1. Review top requested UX features...
  2. Strengthen support workflow...
  3. Ship performance hotfixes...

MCP Status   : calendar=ok, doc=ok, mail=pending_approval
```

---

## Google Doc Tracking

The same email body is appended to the tracking Google Doc (`GOOGLE_TRACKING_DOC_ID`) wrapped in separators:

```
========================================
[full email body]
========================================
```

---

## Key Files

| File | Role |
|------|------|
| `phase3_voiceScheduler/app/services/mcp_client.py` | HTTP calls to MCP server |
| `phase3_voiceScheduler/app/services/hitl_service.py` | Builds email body, triggers MCP on approve |
| `phase3_voiceScheduler/app/services/voice_service.py` | Booking flow, calls mcp_client |
| `phase3_voiceScheduler/app/services/theme_provider.py` | Fetches themes + full pulse from Phase 2 |

---

## HITL Approval Center (UI)

Merged into `/voice-scheduler` page (PillarC.js). No separate `/hitl` route.

- Pending tab: shows one row per booking (deduped by booking_code)
- Click "Mark Done" → fires approve API → MCP calls execute
- Email preview panel shows full rich body (read-only)
- Status auto-refreshes every 5 seconds

---

## Google OAuth Setup (for HF)

1. Create OAuth credentials in Google Cloud Console (Desktop app type)
2. Enable Google Docs API + Gmail API
3. Run locally: `python3 generate_token.py` → browser login → `token.json`
4. Add `GOOGLE_TOKEN_JSON` secret in HF Space Settings (paste full JSON, no trailing newline)

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `MCP_SERVER_URL` | `https://ashishsankhua-google-docs-gmail-mcp-server.hf.space` |
| `GOOGLE_TRACKING_DOC_ID` | `1PtKhugpyu0W1SBhlHcBqlhpHQ1bJnxm9uh0dr-O5LIU` |
| `ADVISOR_EMAIL` | `ashishsankhuapg@gmail.com` |
| `GOOGLE_MEET_URL` | `https://meet.google.com/mgq-xoua-egx?authuser=0` |
| `GOOGLE_TOKEN_JSON` | Full OAuth token JSON (set in HF secrets) |
