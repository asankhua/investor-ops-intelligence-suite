# Wireframe - Phase 5: Frontend UI

## Overview

React 18 single-page app with sidebar navigation. All API calls go through Phase 4 gateway (`REACT_APP_API_GATEWAY_URL`).

**Local**: `http://localhost:3000` → gateway at `http://localhost:8000`
**HuggingFace**: `https://ashishsankhua-investor-ops-intelligence-suite.hf.space` → nginx proxies `/api/` to gateway

---

## Project Structure

```
phase5_frontend/src/
├── App.js                    — Router, sidebar layout
├── index.js                  — React entry point
├── services/
│   └── api.js                — axios instance, all API calls
├── components/
│   └── Sidebar.js            — Fixed left nav (60px wide)
├── pages/
│   ├── Dashboard.js          — Home: stats, pillar cards, activity
│   ├── PillarA.js            — Knowledge Base: RAG chat + sources
│   ├── PillarB.js            — Weekly Pulse: themes + analytics
│   ├── PillarC.js            — Voice Scheduler + HITL (merged)
│   ├── Evals.js              — Testing & Monitoring
│   └── HITL.js               — Legacy (kept, not routed)
└── styles/
    └── GlobalStyles.js
```

---

## Routes

| Path | Component | Description |
|------|-----------|-------------|
| `/` | Dashboard | Live stats, pillar cards, activity feed |
| `/knowledge-base` | PillarA | RAG chat, fund list, sources |
| `/weekly-pulse` | PillarB | Themes, analytics charts |
| `/voice-scheduler` | PillarC | Voice/text chat + HITL approval |
| `/evals` | Evals | Run evaluations |
| `/hitl` | → redirect | Redirects to `/voice-scheduler` |

---

## Sidebar

Fixed 60px left sidebar with icon nav items + tooltips on hover:
- 🏠 Home (Dashboard)
- 📖 Smart-Sync Knowledge Base
- 📊 Insight-Driven Pulse
- 🎤 AI Voice Scheduler & Approvals
- ⚡ Evals: Testing & Monitoring

HITL nav item removed (merged into Voice Scheduler).

---

## Page: Dashboard (`/`)

**Data sources** (all live, refetch every 15s):
- `GET /api/v1/dashboard/stats` → kb_docs, themes_active, bookings_this_week, pending_approvals
- `GET /api/v1/dashboard/pillars` → pillar status (operational/degraded)
- `GET /api/v1/dashboard/performance` → overall score
- `GET /api/v1/dashboard/activity` → last 5 events
- `GET /api/v1/pillar-b/weekly-pulse` → sentiment score (refetch every 60s)

**Layout**:
- Header: title + performance badge
- Stats grid (4 cards): KB Docs, Active Themes, Weekly Bookings, Pending Approvals
- Pillar cards (3): each shows count + status + contextual 3rd stat
  - Pillar A: Documents, Live/Down, Engine name
  - Pillar B: Themes, Live/Down, Sentiment score (red if negative)
  - Pillar C: Bookings, Live/Down, Pending approvals count
- Recent Activity: last 5 events (tiles)
- Quick Tips footer

---

## Page: Knowledge Base (`/knowledge-base`)

**Layout** (3-column):
- Left: Fund list with search (from `GET /api/v1/funds/search`)
- Center: Conversational chat
  - Messages with bullet points + source tags
  - Self-RAG debug panel (query expansion, sufficiency, chunks)
  - Text input + send button
- Right: Sources & Citations
  - Empty state until first query
  - Updates from `citations` in each RAG response
  - "View Source" links use `source_url` (fallback: Google search)

---

## Page: Weekly Pulse (`/weekly-pulse`)

**Layout**:
- Header: title + refresh + download CSV buttons
- Top themes cards with confidence bars
- Summary text + action ideas
- Analytics section:
  - Theme distribution (pie/bar chart via recharts)
  - Sentiment trend (line chart)
  - Mention volume (bar chart)
  - Keywords list

---

## Page: Voice Scheduler (`/voice-scheduler`)

**Layout**:
- Header: title + Pipeline Status bar (VAD › STT › LLM › TTS › Doc › Email)
- Weekly Pulse Themes bar: chips with confidence %, "Refresh Themes" button
- Main 3-column grid:
  - Left: Voice Recording Interface
    - Red mic button (record/stop)
    - Timer display
    - Play / Send Recording / Cancel buttons
    - Agent Voice TTS player (browser speechSynthesis)
  - Center: Conversation Chatbot
    - Messages (user/agent)
    - Text input + Send button
  - Right: Booking Confirmed card
    - Booking Code, Date, Time, RM, Status
- Quick Tips bar
- HITL Section (tabbed):
  - Pending Approvals tab: table with Booking Code, Details, Requested, Status + "Mark Done" button
  - Resolved tab: same table without action button
  - Stats: Pending count, Resolved count, Total Bookings
  - Tracking Doc button (links to Google Doc)
  - Preview Draft Email panel (560px wide):
    - Subject field (editable when Edit mode)
    - Body textarea (320px min-height, read-only by default)
    - No Send/Edit buttons (removed per request)

**Theme flow**:
- Page load: static greeting, no themes shown
- First message OR "Refresh Themes": themes fetch + greeting updates
- Themes auto-fetch silently on first chat message if not loaded

---

## Page: Evals (`/evals`)

**Layout**:
- Header: title + "Run All Evaluations" button
- Last run timestamp
- Score cards (4): RAG %, Safety %, UX %, Overall %
- Eval cards (4): RAG, Safety, UX, Integration
  - Each shows pass/fail icon + test rows with real API response data
  - Before run: default pass state shown
  - After run: updates from actual API responses

---

## API Service (`api.js`)

```javascript
const API_BASE_URL = process.env.REACT_APP_API_GATEWAY_URL !== undefined
  ? process.env.REACT_APP_API_GATEWAY_URL
  : 'http://localhost:8000';

// baseURL = `${API_BASE_URL}/api/v1`
// Empty string → relative /api/v1 → nginx proxy handles it on HF
```

All API groups: `dashboardAPI`, `pillarAAPI`, `pillarBAPI`, `pillarCAPI`, `hitlAPI`, `evalsAPI`.

---

## Styling

- Color palette: `#1E3A5F` (dark blue), `#5DADE2` (light blue), `#E8F4FC` (bg)
- Status colors: `#27AE60` (green/ok), `#E74C3C` (red/error), `#E67E22` (orange/pending)
- All components: styled-components
- Font: system default (no custom font)
- Responsive: max-width containers, no mobile breakpoints

---

## Build & Deploy

**Local**:
```bash
cd phase5_frontend && npm start   # dev server :3000
cd phase5_frontend && npm run build  # production build
```

**HuggingFace** (Dockerfile):
```dockerfile
RUN npm install --prefix phase5_frontend --silent
COPY phase5_frontend/ ./phase5_frontend/
RUN REACT_APP_API_GATEWAY_URL="" REACT_APP_API_VERSION="v1" npm run build --prefix phase5_frontend
```

Built output served by nginx at port 7860. API calls proxied via `/api/` location block.
