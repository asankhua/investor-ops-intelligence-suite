# Investor Ops & Intelligence Suite - End-to-End User Journey

Complete user journey mapping showing how customers, agents, and advisors interact with the unified platform across all three pillars.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Personas](#2-personas)
3. [Primary User Journeys](#3-primary-user-journeys)
   - Journey 1: Investor Self-Service Knowledge
   - Journey 2: Theme-Aware Voice Scheduling
   - Journey 3: Advisor Preparation via HITL
   - Journey 4: Weekly Pulse to Product Action
4. [Cross-Pillar State Flow](#4-cross-pillar-state-flow)
5. [Error Recovery Paths](#5-error-recovery-paths)
6. [Metrics & Success Criteria](#6-metrics--success-criteria)

---

## 1. Overview

### The Unified Experience

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    END-TO-END USER JOURNEY FLOW                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   INVESTOR                    PLATFORM                    ADVISOR      │
│      │                          │                          │          │
│      │  1. Search Question       │                          │          │
│      ├─────────────────────────►│                          │          │
│      │                          │  2. RAG Retrieval        │          │
│      │                          │  (M1 + M1.1 Sources)      │          │
│      │                          │◄────────┐                │          │
│      │  3. 6-Bullet Answer       │         │                │          │
│      │◄─────────────────────────┤         │                │          │
│      │  [Source: M1, M1.1]      │         │                │          │
│      │                          │         │                │          │
│      │  4. Voice Call Started    │         │                │          │
│      ├─────────────────────────►│         │                │          │
│      │                          │  5. Check Weekly Pulse    │          │
│      │                          │  (M2 Top Themes)         │          │
│      │                          │◄────────┘                │          │
│      │  6. Theme-Aware Greeting  │                          │          │
│      │◄─────────────────────────┤                          │          │
│      │  "I see users asking      │                          │          │
│      │   about Nominee updates"  │                          │          │
│      │                          │                          │          │
│      │  7. Schedule Meeting      │                          │          │
│      ├─────────────────────────►│                          │          │
│      │                          │  8. MCP Actions Triggered │          │
│      │                          ├────────► Calendar Hold    │          │
│      │                          ├────────► Email Draft      │          │
│      │                          │                          │          │
│      │  9. Booking Code: MTG-001 │                          │          │
│      │◄─────────────────────────┤                          │          │
│      │                          │  10. HITL Approval        │          │
│      │                          ├─────────────────────────►│          │
│      │                          │  [Advisor reviews email   │          │
│      │                          │   with Market Context]   │          │
│      │                          │◄─────────────────────────┤          │
│      │                          │  11. Confirmation Sent     │          │
│      │  12. Email Received       │◄─────────────────────────┤          │
│      │◄──────────────────────────────────────────────────────┤          │
│      │                          │                          │          │
│      │                          │  13. Log to M2 Notes       │          │
│      │                          ├─────────────────────────►│          │
│      │                          │  (Cross-reference for      │          │
│      │                          │   future theme analysis)   │          │
│      ▼                          ▼                          ▼          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Personas

### Persona 1: Retail Investor (Rahul)
- **Profile**: 32-year-old IT professional, first-time mutual fund investor
- **Goals**: Understand fees, schedule advisor calls, get quick answers
- **Pain Points**: Confusing fee structures, long wait times for support
- **Tech Comfort**: High (uses apps daily)

### Persona 2: Support Agent (Priya)
- **Profile**: Customer support team lead at fintech company
- **Goals**: Monitor voice agent performance, review HITL approvals
- **Pain Points**: Fragmented tools, no visibility into customer context
- **Tech Comfort**: Medium (uses dashboards, not technical)

### Persona 3: Financial Advisor (Vikram)
- **Profile**: Certified financial planner, 50+ client meetings/week
- **Goals**: Prepare for meetings, understand client sentiment
- **Pain Points**: No context before calls, manual scheduling
- **Tech Comfort**: Low (prefers email, minimal app usage)

### Persona 4: Product Manager (Anita)
- **Profile**: Product lead for investor platform
- **Goals**: Understand user pain points, prioritize features
- **Pain Points**: Feedback scattered across channels
- **Tech Comfort**: High (uses analytics tools)

---

## 3. Primary User Journeys

### Journey 1: Investor Self-Service Knowledge (Pillar A)

**Scenario**: Rahul notices an unexpected charge on his ELSS fund redemption.

```
┌─────────────────────────────────────────────────────────────────────────┐
│  JOURNEY 1: KNOWLEDGE SELF-SERVICE                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  STEP 1: Discovery                                                      │
│  ─────────────────                                                      │
│  Trigger: Rahul sees unexpected exit load charge in app                 │
│  Action: Opens Investor Ops Suite → Pillar A                          │
│  Emotional State: 😕 Confused, slightly anxious                         │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ [Pillar A: Smart-Sync Knowledge Base]                           │   │
│  │                                                                 │   │
│  │ 🔍 "Why was I charged exit load on my ELSS fund?"              │   │
│  │     [Search Button]                                             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  STEP 2: Unified Retrieval (Backend)                                  │
│  ───────────────────────────────────                                  │
│  System Actions:                                                        │
│  • Query vectorized and sent to ChromaDB                              │
│  • EnsembleRetriever fetches from M1 (FAQ) + M1.1 (Fee Explainer)     │
│  • Hybrid search: 60% vector + 40% BM25                                 │
│  • Top 5 chunks retrieved with source tagging                           │
│                                                                         │
│  Retrieved Context:                                                     │
│  ┌────────────┬────────┬────────────────────────────────────────┐    │
│  │ Chunk 1    │ M1.1   │ "Exit load: 1% if redeemed < 1 year"  │    │
│  │ Chunk 2    │ M1     │ "ELSS lock-in: 3 years mandatory"     │    │
│  │ Chunk 3    │ M1.1   │ "Calculated on redemption value"      │    │
│  │ Chunk 4    │ M1     │ "Tax benefit under 80C"               │    │
│  │ Chunk 5    │ M1.1   │ "Applicable only to recent units"    │    │
│  └────────────┴────────┴────────────────────────────────────────┘    │
│                                                                         │
│  STEP 3: Constrained Generation                                       │
│  ──────────────────────────────                                       │
│  LLM (GPT-4o) processes with JSON schema constraint:                  │
│  • Max 6 bullets enforced via response_format                         │
│  • Source citation required for each bullet                             │
│  • Guardrails: PII check, investment advice block                       │
│                                                                         │
│  STEP 4: Response Delivery                                            │
│  ─────────────────────────                                            │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 📄 Response (6 Bullets + Citations)                              │   │
│  │                                                                 │   │
│  │ • Exit load for ELSS is 1% if redeemed within 1 year          │   │
│  │   [Source: M1.1 - Fee Explainer]                                │   │
│  │                                                                 │   │
│  │ • ELSS funds have a 3-year lock-in period for tax benefits    │   │
│  │   [Source: M1 - FAQ]                                            │   │
│  │                                                                 │   │
│  │ • Exit load applies only to units purchased within last year    │   │
│  │   [Source: M1.1 - Fee Explainer]                                │   │
│  │                                                                 │   │
│  │ • Your charge was likely due to early withdrawal                │   │
│  │   [Source: M1.1 - Fee Explainer]                                │   │
│  │                                                                 │   │
│  │ • Check your holding period in the app portfolio section        │   │
│  │   [Source: M1 - FAQ]                                            │   │
│  │                                                                 │   │
│  │ • For disputes, schedule a call with our advisor               │   │
│  │   [Source: M1.1 - Fee Explainer]                                │   │
│  │                                                                 │   │
│  │ [📄 View M1.1 Source]  [📄 View M1 Source]                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  STEP 5: Resolution or Escalation                                     │
│  ─────────────────────────────────                                    │
│  Rahul's Options:                                                       │
│  ✅ Satisfied → Closes app                                             │
│  🔍 Follow-up question → New search                                    │
│  📞 Schedule advisor call → Journey 2 (Voice Agent)                    │
│                                                                         │
│  Emotional State: 😊 Informed, confident                               │
│  Time to Resolution: 45 seconds                                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Success Metrics**:
- Answer relevance >90% (RAGAS metric)
- Source citation accuracy 100%
- 6-bullet constraint adherence 100%
- User satisfaction rating ≥4.5/5

---

### Journey 2: Theme-Aware Voice Scheduling (Pillar B + C)

**Scenario**: After reading about exit loads, Rahul wants to schedule a call but the voice agent knows about current user issues.

```
┌─────────────────────────────────────────────────────────────────────────┐
│  JOURNEY 2: THEME-AWARE VOICE SCHEDULING                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  STEP 1: Voice Agent Activation                                         │
│  ────────────────────────────                                           │
│  Trigger: Rahul clicks "📞 Schedule Call" from Pillar A response       │
│  Action: Redirected to Pillar C Voice Agent                           │
│  Emotional State: 😊 Ready to talk                                     │
│                                                                         │
│  STEP 2: Backend Context Preparation (Cross-Pillar)                     │
│  ─────────────────────────────────────────────────                    │
│  System Actions (before greeting):                                      │
│  • Fetch Weekly Pulse from Pillar B (M2)                              │
│  • Check top themes with confidence >0.7                               │
│  • Inject theme context into voice agent prompt                         │
│                                                                         │
│  Weekly Pulse Data (from M2):                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 📊 Weekly Product Pulse (Generated from 1,247 reviews)          │   │
│  │                                                                 │   │
│  │ 🔥 Top Themes:                                                  │   │
│  │    1. Login Issues (Confidence: 0.87, 43 mentions)               │   │
│  │    2. Nominee Updates (Confidence: 0.82, 38 mentions)          │   │
│  │    3. Exit Load Queries (Confidence: 0.79, 31 mentions) ← MATCH │   │
│  │                                                                 │   │
│  │ Sentiment: -0.2 (Slightly negative)                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  STEP 3: Dynamic Greeting Generation                                    │
│  ───────────────────────────────────                                  │
│  Prompt Injection via Jinja2 template:                                  │
│                                                                         │
│  Template variables:                                                    │
│  • top_themes = ["Login Issues", "Nominee Updates", "Exit Load Queries"]│
│  • user_context = "Just searched about exit loads" (from Pillar A)    │
│                                                                         │
│  Generated Greeting:                                                    │
│  "Hello! I see you were looking into exit load charges.                │
│   Many users have similar questions about fees this week.              │
│   I can help you schedule a call with an advisor to discuss this.        │
│   Would you like me to check available slots?"                         │
│                                                                         │
│  STEP 4: Voice Interaction Flow                                       │
│  ────────────────────────────────                                       │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 🎙️ PILLAR C: AI VOICE SCHEDULER                                  │   │
│  │                                                                 │   │
│  │ 🔧 Pipeline Status:                                             │   │
│  │ [VAD] → [STT] → [LLM] → [TTS] → [MCP]                           │   │
│  │                                                                 │   │
│  │ 💬 Conversation:                                                │   │
│  │                                                                 │   │
│  │ 🤖 Agent: "I see you were looking into exit load charges...     │   │
│  │           Would you like to schedule a call?"                     │   │
│  │                                                                 │   │
│  │ 👤 User: [Voice] "Yes, morning slot please"                     │   │
│  │     ↓                                                            │   │
│  │    [Silero VAD] → [Sarvam STT] → Intent: "schedule_morning"    │   │
│  │                                                                 │   │
│  │ 🤖 Agent: "Great! Here are morning slots: 9:00 AM, 10:30 AM,   │   │
│  │           11:00 AM. Which works for you?"                       │   │
│  │                                                                 │   │
│  │ 👤 User: [Voice] "10:30 AM on Tuesday"                          │   │
│  │                                                                 │   │
│  │ 🤖 Agent: "Perfect! I'll create a calendar hold for             │   │
│  │           Tuesday, January 16 at 10:30 AM.                        │   │
│  │           I'll also draft an email to your advisor.              │   │
│  │           Please hold while I prepare these..."                  │   │
│  │                                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  STEP 5: MCP Actions Triggered                                          │
│  ─────────────────────────────                                          │
│  System Actions:                                                        │
│  • Generate booking code: MTG-2024-001                                 │
│  • Call MCP Tool: create_calendar_hold()                               │
│  • Call MCP Tool: draft_email()                                        │
│  • LangGraph interrupt() for HITL approval                             │
│                                                                         │
│  Email Draft with Market Context:                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 📧 Email Draft (Pending Approval)                               │   │
│  │                                                                 │   │
│  │ To: advisor@groww.com                                           │   │
│  │ Subject: Meeting Scheduled - Rahul Sharma (Exit Load Query)    │   │
│  │                                                                 │   │
│  │ --- MARKET CONTEXT (from Weekly Pulse) ---                      │   │
│  │ Current customer sentiment: Slightly negative (-0.2)            │   │
│  │ Top issues this week: Exit load queries (31 mentions)         │   │
│  │                       Login issues (43 mentions)                │   │
│  │                                                                 │   │
│  │ Client Question: Why was I charged exit load on ELSS?          │   │
│  │ Suggested Approach: Explain 1% rule + 3-year lock-in            │   │
│  │                                                                 │   │
│  │ --- MEETING DETAILS ---                                         │   │
│  │ Date: Tuesday, Jan 16, 2024 at 10:30 AM                         │   │
│  │ Booking Code: MTG-2024-001                                      │   │
│  │ Meet Link: meet.google.com/mtg-2024-001                          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  STEP 6: Booking Confirmation                                          │
│  ────────────────────────────                                           │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ ✅ BOOKING CONFIRMED                                            │   │
│  │                                                                 │   │
│  │ 🎫 Your Booking Code: MTG-2024-001                               │   │
│  │ 📅 Tuesday, January 16, 2024 at 10:30 AM                      │   │
│  │ 🔗 Google Meet: meet.google.com/mtg-2024-001                     │   │
│  │                                                                 │   │
│  │ 📧 Confirmation email will be sent once approved                │   │
│  │ ⏱️ Expected approval: Within 15 minutes                         │   │
│  │                                                                 │   │
│  │ [📋 Copy Code] [🔗 Open Meet] [📧 View Email Draft]              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  STEP 7: Cross-Pillar State Update                                     │
│  ─────────────────────────────────                                     │
│  • Booking code MTG-2024-001 logged to M2 tracking document            │
│  • Associated with "Exit Load Queries" theme                         │
│  • Future theme analysis will include this booking data                │
│                                                                         │
│  Emotional State: 😊 Satisfied, appointment secured                     │
│  Time to Completion: 3 minutes 30 seconds                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Success Metrics**:
- Theme propagation accuracy 100%
- Voice intent recognition >95%
- MCP action success rate >98%
- HITL approval time <15 minutes average

---

### Journey 3: Advisor Preparation via HITL (Pillar C)

**Scenario**: Advisor Vikram reviews and approves the meeting request with full context.

```
┌─────────────────────────────────────────────────────────────────────────┐
│  JOURNEY 3: HITL APPROVAL & ADVISOR PREPARATION                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  STEP 1: HITL Notification                                              │
│  ─────────────────────────                                              │
│  Trigger: MCP actions created, awaiting approval                          │
│  Action: Notification sent to advisor queue                             │
│  User: Vikram (Financial Advisor)                                     │
│                                                                         │
│  Notification:                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 📬 New Meeting Request Pending Approval                         │   │
│  │                                                                 │   │
│  │ Client: Rahul Sharma                                            │   │
│  │ Topic: Exit Load Query                                          │   │
│  │ Time: Tuesday, Jan 16, 10:30 AM                                 │   │
│  │ Booking Code: MTG-2024-001                                      │   │
│  │                                                                 │   │
│  │ 🔍 Includes Market Context from Weekly Pulse                    │   │
│  │                                                                 │   │
│  │ [Review & Approve] → Opens HITL Approval Center               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  STEP 2: HITL Approval Center Review                                    │
│  ─────────────────────────────────────                                  │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 👤 HITL APPROVAL CENTER (3 Pending Actions)                     │   │
│  │                                                                 │   │
│  │ ┌──────────┬────────────────┬────────────────┬──────────────┐  │   │
│  │ │ Action   │ Booking Code   │ Context        │ Approve?     │  │   │
│  │ ├──────────┼────────────────┼────────────────┼──────────────┤  │   │
│  │ │ Calendar │ MTG-2024-001   │ Jan 16, 10:30  │ [✅] [❌]    │  │   │
│  │ │ Email    │ MTG-2024-001   │ Exit Load Q    │ [✅] [❌]    │  │   │
│  │ │          │                │ + Mkt Context  │              │  │   │
│  │ └──────────┴────────────────┴────────────────┴──────────────┘  │   │
│  │                                                                 │   │
│  │ 📊 Market Context Preview:                                      │   │
│  │ • Sentiment: -0.2 (Slightly negative)                          │   │
│  │ • Top Theme: Exit Load Queries (31 mentions)                   │   │
│  │ • Suggested Approach: Explain 1% rule + lock-in                │   │
│  │                                                                 │   │
│  │ [✅ Approve All]  [🔍 View Full Email]  [✏️ Edit Email]      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  STEP 3: Advisor Decision                                              │
│  ─────────────────────────                                              │
│  Vikram reviews and decides:                                          │
│                                                                         │
│  Option A: ✅ Approve as-is                                            │
│  • Calendar hold confirmed                                            │
│  • Email sent to investor                                              │
│  • Status updated to "approved"                                        │
│                                                                         │
│  Option B: ✏️ Edit Email Content                                        │
│  • Modify email draft with personalized message                        │
│  • Re-submit for approval                                              │
│                                                                         │
│  Option C: ❌ Reject with Reason                                        │
│  • Provide reason: "Time conflict, suggest 2:00 PM"                   │
│  • Voice agent notified to contact investor for rescheduling           │
│                                                                         │
│  STEP 4: Post-Approval Actions                                          │
│  ────────────────────────────                                           │
│  Upon approval:                                                         │
│  • Calendar event created in advisor's Google Calendar                 │
│  • Confirmation email sent to investor (Rahul)                         │
│  • Meeting link generated (meet.google.com/mtg-2024-001)               │
│  • Entry added to M2 tracking document with booking code               │
│                                                                         │
│  STEP 5: Advisor Preparation                                            │
│  ───────────────────────────                                            │
│  Before meeting, Vikram reviews:                                        │
│  • Client's original question (from Pillar A search)                   │
│  • Market context (from Pillar B Weekly Pulse)                         │
│  • Suggested talking points                                            │
│  • Past interactions (if any)                                          │
│                                                                         │
│  Meeting Outcome: Well-informed advisor, satisfied investor            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### Journey 4: Weekly Pulse to Product Action (Pillar B)

**Scenario**: Product Manager Anita analyzes reviews to identify trends.

```
┌─────────────────────────────────────────────────────────────────────────┐
│  JOURNEY 4: FROM REVIEWS TO PRODUCT INSIGHTS                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  STEP 1: Data Ingestion                                                 │
│  ───────────────────                                                    │
│  Sources: App Store reviews, Support tickets, Social mentions          │
│  Volume: 1,247 new reviews this week                                    │
│  User: Anita (Product Manager)                                         │
│                                                                         │
│  STEP 2: Automated Analysis                                             │
│  ─────────────────────────                                              │
│  System Actions:                                                        │
│  • Theme extraction using GPT-4o + scikit-learn K-means               │
│  • Sentiment analysis (TextBlob/VADER)                                   │
│  • Confidence scoring for each theme                                    │
│  • Action idea generation                                               │
│                                                                         │
│  STEP 3: Weekly Pulse Generation                                        │
│  ─────────────────────────────────                                     │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 📈 WEEKLY PRODUCT PULSE (Jan 10-16, 2024)                       │   │
│  │                                                                 │   │
│  │ 📊 Data Summary:                                                │   │
│  │ • Reviews Analyzed: 1,247                                       │   │
│  │ • Avg Sentiment: -0.2 (↓ from last week)                        │   │
│  │ • Response Volume: ↑ 15% vs previous week                         │   │
│  │                                                                 │   │
│  │ 🔥 Top Themes (with Confidence):                                │   │
│  │                                                                 │   │
│  │ 1. Login Issues         (0.87)  - 43 mentions                    │   │
│  │    Sentiment: Very Negative (-0.6)                              │   │
│  │    🔴 Urgent: Biometric login failing on Android 14            │   │
│  │                                                                 │   │
│  │ 2. Nominee Updates      (0.82)  - 38 mentions                    │   │
│  │    Sentiment: Neutral (0.1)                                     │   │
│  │    🟡 Info: Users want simpler nominee change process          │   │
│  │                                                                 │   │
│  │ 3. Exit Load Queries    (0.79)  - 31 mentions ← NEW THIS WEEK  │   │
│  │    Sentiment: Confused (-0.3)                                   │   │
│  │    🟢 Action: Add clearer fee breakdown in app                 │   │
│  │                                                                 │   │
│  │ 💡 Recommended Actions (3):                                     │   │
│  │ 1. Prioritize biometric login fix for Android 14               │   │
│  │ 2. Simplify nominee update flow (3 clicks → 1 click)             │   │
│  │ 3. Add "Fee Calculator" tool in portfolio section              │   │
│  │                                                                 │   │
│  │ [📥 Download PDF] [📤 Share with Team] [🔗 View Raw Data]      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  STEP 4: Cross-Pillar Activation                                        │
│  ───────────────────────────────                                        │
│  Weekly Pulse automatically feeds into:                                │
│  • Voice Agent greetings (Pillar C) - Theme-aware responses            │
│  • Advisor email drafts (Pillar C) - Market context snippets         │
│  • Product roadmap priorities (Internal)                                 │
│                                                                         │
│  STEP 5: Product Action                                                 │
│  ───────────────────                                                    │
│  Anita creates tickets:                                                 │
│  • P0: Fix biometric login (Engineering)                               │
│  • P1: Simplify nominee flow (Design)                                  │
│  • P2: Build fee calculator (Product)                                  │
│                                                                         │
│  Next Week: Verify if theme volume decreases                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Cross-Pillar State Flow

### State Persistence Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CROSS-PILLAR STATE MANAGEMENT                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐ │
│  │   PILLAR A      │      │   PILLAR B      │      │   PILLAR C      │ │
│  │   (RAG Chat)    │◄────►│   (Weekly Pulse)│◄────►│   (Voice Agent) │ │
│  │                 │      │                 │      │                 │ │
│  │ • Queries       │      │ • Themes        │      │ • Bookings      │ │
│  │ • Responses     │      │ • Sentiment     │      │ • Greetings     │ │
│  │ • Source refs   │      │ • Confidence    │      │ • MCP actions   │ │
│  └─────────────────┘      │ • Action ideas  │      │ • HITL status   │ │
│                           └─────────────────┘      └─────────────────┘ │
│                                    │                   │                │
│                                    ▼                   ▼                │
│                           ┌─────────────────────────────────────┐      │
│                           │      UNIFIED STATE STORE            │      │
│                           │  ┌─────────────────────────────┐     │      │
│                           │  │ weekly_pulse               │     │      │
│                           │  │ ├── top_themes[]           │     │      │
│                           │  │ ├── sentiment_score        │     │      │
│                           │  │ └── last_updated           │     │      │
│                           │  ├─────────────────────────────┤     │      │
│                           │  │ active_bookings[]          │     │      │
│                           │  │ ├── booking_code           │     │      │
│                           │  │ ├── advisor_email          │     │      │
│                           │  │ ├── datetime               │     │      │
│                           │  │ └── theme_reference          │     │      │
│                           │  ├─────────────────────────────┤     │      │
│                           │  │ booking_to_pulse_map       │     │      │
│                           │  │ ├── MTG-2024-001           │     │      │
│                           │  │ │   └── theme: "Exit Load" │   │      │
│                           │  │ └── MTG-2024-002           │     │      │
│                           │  │     └── theme: "Login"     │     │      │
│                           │  └─────────────────────────────┘     │      │
│                           └─────────────────────────────────────┘      │
│                                                                         │
│  DATA FLOWS:                                                            │
│  ───────────                                                            │
│  1. Pillar B → Pillar C: Top themes flow to voice agent greetings      │
│  2. Pillar B → Pillar C: Market context flows to advisor emails        │
│  3. Pillar C → Pillar B: Booking codes logged for future analysis      │
│  4. Pillar A → Pillar C: Search queries inform voice agent context     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Error Recovery Paths

### Common Failure Scenarios

| Scenario | Detection | Recovery Path | User Experience |
|----------|-----------|---------------|-----------------|
| **RAG Empty Retrieval** | Chunks returned = 0 | Fallback to general knowledge + suggestion | "I couldn't find specific info. Try asking about ELSS or Equity funds." |
| **Voice Unclear Audio** | VAD confidence <0.5 | Prompt to repeat + offer text input | "I didn't catch that. Could you repeat or type your request?" |
| **MCP Server Unavailable** | Connection timeout | Queue for retry + notify admin | "Booking is queued. You'll receive confirmation shortly." |
| **HITL Timeout** | No response in 30 min | Auto-escalate to supervisor + notify user | "Escalated to senior advisor. Expect response within 1 hour." |
| **Low Theme Confidence** | Confidence <0.7 | Skip theme injection, use generic greeting | Standard greeting without theme mention |
| **Conflicting Sources** | M1 vs M1.1 mismatch | Flag for review + cite both sources | "Sources differ. Here's what M1 says... And what M1.1 says..." |

---

## 6. Metrics & Success Criteria

### Journey Completion Metrics

| Journey | Success Metric | Target | Measurement |
|---------|---------------|--------|-------------|
| **Knowledge Self-Service** | Query resolution without escalation | >85% | Tracked via follow-up actions |
| **Voice Scheduling** | End-to-end booking completion | >90% | Booking code generation |
| **HITL Approval** | Approval time | <15 min | Timestamp analysis |
| **Theme Propagation** | Theme appears in greeting | 100% | Log analysis |

### User Satisfaction Metrics

| Metric | Target | Collection Method |
|--------|--------|-------------------|
| CSAT (Voice Agent) | ≥4.5/5 | Post-call survey |
| NPS (Knowledge Base) | ≥50 | In-app micro-survey |
| HITL Approval Rate | >95% | Action audit logs |
| First Contact Resolution | >80% | Ticket tracking |

---

**Document Version**: 1.0  
**Last Updated**: April 2026  
**Related Documents**: 
- `architecture.md` - System architecture
- `wireframe.md` - UI specifications
- `evals.md` - Evaluation framework
