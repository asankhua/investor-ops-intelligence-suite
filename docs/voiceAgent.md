# Voice Agent - Phase 3

## Overview

AI Voice Scheduler with text + voice input, theme-aware conversation, booking flow, and HITL approval. Merged with HITL Approval Center in the same UI page.

---

## Conversation Flow (State Machine)

```
greeting
  │ any message
  ▼
topic_detection
  │ valid theme detected (e.g. "support and service")
  ▼
confirm_slot
  │ "first" / "second" / "yes"
  ▼
complete → booking confirmed, MCP triggered
```

### Theme Detection

Themes are fetched from Phase 2 (`/api/v1/pillar-b/themes`) via `ThemeProvider`. The state machine matches user input against theme names using substring matching.

**Default port fix**: `ThemeProvider` defaults to `http://localhost:8102` (not 8002).

### Slot Options

Two slots offered: tomorrow at 10:00 AM and 14:00 PM UTC.

---

## Voice Pipeline

```
User mic → MediaRecorder (browser) → audio blob
  │
  ▼
POST /api/v1/pillar-c/voice/record/start → recording_id
  │
  ▼
POST /api/v1/pillar-c/voice/record/stop → audio_url
  │
  ▼
POST /api/v1/pillar-c/conversation/voice {audio_base64}
  │
  ├── Sarvam STT (saarika-v2, en-IN) → transcript
  ├── State machine → response_text
  └── Browser speechSynthesis → TTS playback
```

### Text Pipeline

```
User types → POST /api/v1/pillar-c/conversation/message
  │
  ├── State machine → response_text
  └── If voice mode active → browser speechSynthesis
```

---

## Weekly Pulse Themes Integration

- On page load: static greeting shown, no themes
- On first message OR "Refresh Themes" click: themes fetched from Phase 2
- Theme chips shown: `Feature Requests 80%`, `Support & Service 71%`, etc.
- Greeting updates to list current themes after refresh
- Backend always knows themes (fetched internally by ThemeProvider)

---

## Booking Confirmation Card

Shows after booking is confirmed:
- Booking Code (e.g. `MTG-2026-427`)
- Date + Time (parsed from `scheduled_for` ISO string)
- Relationship Manager: Advisor
- Status: `pending_approval`

**Date parsing fix**: `scheduled_for` format is `2026-04-22T10:00:00Z` (clean ISO). Frontend uses `parseBookingDate()` to handle edge cases.

---

## HITL Approval (merged into same page)

See `docs/mcpIntegration.md` for full flow.

UI sections:
1. Pending Approvals tab — one row per booking, "Mark Done" button
2. Resolved tab — approved/rejected bookings
3. Preview Draft Email — full email body (read-only), 560px wide

---

## Pipeline Status Bar

Shows real-time status of: `VAD › STT › LLM › TTS › Doc › Email`

- `idle` → grey
- `active` → blue highlight
- `done` → completed

Calendar step removed (internal only).

---

## Key Files

| File | Role |
|------|------|
| `phase3_voiceScheduler/app/services/voice_service.py` | State machine, STT, booking flow |
| `phase3_voiceScheduler/app/services/theme_provider.py` | Fetches themes + pulse from Phase 2 |
| `phase3_voiceScheduler/app/services/hitl_service.py` | HITL queue, email body, MCP trigger |
| `phase3_voiceScheduler/app/services/mcp_client.py` | HTTP calls to MCP server |
| `phase3_voiceScheduler/app/services/state_store.py` | JSON state persistence |
| `phase5_frontend/src/pages/PillarC.js` | Full UI: voice, chat, booking, HITL |

---

## API Endpoints (Phase 3 :8103)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/debug` | Env var debug (MCP URL, advisor email, etc.) |
| POST | `/api/v1/pillar-c/voice/record/start` | Start recording |
| POST | `/api/v1/pillar-c/voice/record/stop` | Stop recording |
| POST | `/api/v1/pillar-c/voice/record/cancel` | Cancel recording |
| POST | `/api/v1/pillar-c/conversation/message` | Text message |
| POST | `/api/v1/pillar-c/conversation/voice` | Voice message (base64) |
| GET | `/api/v1/pillar-c/pipeline/status` | Pipeline step status |
| GET | `/api/v1/hitl/actions` | All HITL actions |
| GET | `/api/v1/hitl/pending` | Pending actions only |
| POST | `/api/v1/hitl/approve/{id}` | Approve → fires MCP |
| POST | `/api/v1/hitl/reject/{id}` | Reject action |
| GET | `/api/v1/hitl/email/preview/{code}` | Email draft preview |

---

## Sarvam API

- STT: `POST https://api.sarvam.ai/speech-to-text`
  - model: `saaras:v3`, language: `en-IN`
  - file: audio/webm
- TTS: browser `speechSynthesis` (fallback, no Sarvam TTS in current impl)

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SARVAM_API_KEY` | Sarvam AI key for STT |
| `PHASE2_BASE_URL` | `http://localhost:8102` (ThemeProvider) |
| `GOOGLE_MEET_URL` | Fixed Meet URL for all bookings |
| `ADVISOR_EMAIL` | Email recipient for drafts |
| `GOOGLE_TRACKING_DOC_ID` | Doc ID for append |
| `MCP_SERVER_URL` | MCP server base URL |
