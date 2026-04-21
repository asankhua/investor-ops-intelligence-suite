# User Journey - Investor Ops Intelligence Suite

## End-to-End Flow

```
User opens http://localhost:3000 (or HF Space)
  │
  ├── Dashboard (/) — live stats, pillar cards, activity feed
  │
  ├── Knowledge Base (/knowledge-base)
  │     ├── Type question → RAG query → 6-bullet answer + citations
  │     ├── Sources & Citations panel updates with real links
  │     └── Fund list (left panel, search/filter)
  │
  ├── Weekly Pulse (/weekly-pulse)
  │     ├── Top themes with confidence + sentiment
  │     ├── Analytics: theme distribution, sentiment trends, keywords
  │     └── Download reviews CSV
  │
  └── Voice Scheduler (/voice-scheduler)
        ├── Weekly Pulse Themes bar (auto-loads on first message)
        ├── Conversation Chatbot (text or voice input)
        │     ├── "hi" → greeting with theme list
        │     ├── "support and service" → slot options
        │     └── "first" → booking confirmed
        ├── Booking Confirmed card (code, date, time, status)
        ├── Voice Recording panel (mic button, play, send, cancel)
        └── HITL Approval section
              ├── Pending tab → "Mark Done" → MCP fires
              └── Preview Draft Email (full body with pulse context)
```

---

## Journey 1: Knowledge Base Query

1. User opens `/knowledge-base`
2. Types: "What are HDFC fund fees?"
3. Backend: Phase 1 RAG pipeline
   - Query expansion → Pinecone retrieval → sufficiency check → 6-bullet generation
4. Response shown in chat with bullet points + source tags
5. Sources & Citations panel updates with real `source_url` links
6. User clicks "View Source" → opens document URL

---

## Journey 2: Voice Scheduling

1. User opens `/voice-scheduler`
2. Types "hi" → themes auto-fetch → greeting shows theme list
3. Types "support and service" → bot offers two time slots
4. Types "first" → booking confirmed (MTG-2026-XXX)
5. Booking card shows date/time/status
6. HITL table shows new pending row
7. User clicks "Mark Done" → MCP fires:
   - Gmail draft created with full pulse context
   - Google Doc appended with booking details
8. Row moves to Resolved tab

---

## Journey 3: Weekly Pulse Review

1. User opens `/weekly-pulse`
2. Sees top 3 themes with confidence scores
3. Analytics charts: theme distribution pie, sentiment trend line, keyword cloud
4. Clicks "Refresh Analysis" → re-runs theme extraction
5. Downloads reviews CSV for offline analysis

---

## Journey 4: Dashboard Monitoring

1. User opens `/` (Dashboard)
2. Sees live stats: KB docs, active themes, weekly bookings, pending approvals
3. Pillar cards show: status (Live/Down), key metric, sentiment/pending count
4. Recent Activity feed shows last 5 events (bookings synced, MCP calls)
5. Auto-refreshes every 15 seconds

---

## Journey 5: Evals

1. User opens `/evals`
2. Clicks "Run All Evaluations"
3. 4 eval endpoints called in parallel:
   - RAG: Phase 1 health check
   - Safety: PII masking test
   - UX: pulse word count + action count
   - Integration: all 3 phases health + state sync
4. Results update: pass/fail icons, scores, last run timestamp

---

## PII Protection

All user input is masked before processing:
- Emails → `[REDACTED_EMAIL]`
- Phone numbers → `[REDACTED_PHONE]`
- Names → `[REDACTED]`

Booking emails show `Customer: [REDACTED]`.

---

## State Persistence

Booking codes are cross-referenced:
- Stored in `phase3_voiceScheduler/data/state.json`
- Synced to `phase4_integrationHub/data/shared_state.json`
- Appended to Google Doc tracking log
- Visible in Dashboard activity feed
