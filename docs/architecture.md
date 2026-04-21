# Investor Ops & Intelligence Suite - Architecture

## Overview

Full-stack AI platform integrating three pillars across 5 phases, deployed on HuggingFace Spaces.

| Phase | Service | Port | Description |
|-------|---------|------|-------------|
| 1 | `phase1_knowledgeBase` | 8101 | Self-RAG Knowledge Base (Pinecone + OpenRouter) |
| 2 | `phase2_weeklyPulse` | 8102 | Weekly Pulse theme analysis (Groq) |
| 3 | `phase3_voiceScheduler` | 8103 | AI Voice Scheduler + HITL + MCP |
| 4 | `phase4_integrationHub` | 8000 | API Gateway (routes all frontend calls) |
| 5 | `phase5_frontend` | 3000/7860 | React Dashboard UI |

---

## System Architecture

```
Browser
  │
  ▼
phase5_frontend (React)
  │  REACT_APP_API_GATEWAY_URL → http://localhost:8000 (local) or /api (HF)
  ▼
phase4_integrationHub (FastAPI :8000)
  ├──► phase1_knowledgeBase (:8101)  — RAG queries, fund search, sources
  ├──► phase2_weeklyPulse   (:8102)  — themes, pulse, analytics
  └──► phase3_voiceScheduler(:8103)  — voice, HITL, MCP, bookings
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, styled-components, react-query, recharts |
| Backend | Python 3.11, FastAPI, uvicorn |
| Vector DB | Pinecone (serverless, aws/us-east-1) |
| LLM (RAG) | OpenRouter → openai/gpt-4o |
| Embeddings | OpenRouter → openai/text-embedding-3-large (dim: 3072) |
| Theme LLM | Groq → llama3 |
| Voice STT/TTS | Sarvam AI (saarika-v2 / meera) |
| MCP Server | HuggingFace Space: ashishsankhua/google-docs-gmail-mcp-server |
| Deployment | HuggingFace Spaces (Docker), nginx, supervisord |
| CI/CD | GitHub Actions → HF sync on push to main |

---

## Environment Variables

All secrets live in `.env` at repo root. On HuggingFace, set as Space Secrets.

| Variable | Used By | Description |
|----------|---------|-------------|
| `PINECONE_API_KEY` | Phase 1 | Pinecone vector DB |
| `PINECONE_INDEX_NAME` | Phase 1 | Default: `investor-kb` |
| `PINECONE_CLOUD` | Phase 1 | Default: `aws` |
| `PINECONE_REGION` | Phase 1 | Default: `us-east-1` |
| `OPENROUTER_API_KEY` | Phase 1 | LLM + embeddings |
| `OPENROUTER_CHAT_MODEL` | Phase 1 | Default: `openai/gpt-4o` |
| `EMBEDDING_MODEL` | Phase 1 | Default: `openai/text-embedding-3-large` |
| `EMBEDDING_DIMENSION` | Phase 1 | Default: `3072` |
| `GROQ_API_KEY` | Phase 2 | Theme classification |
| `SARVAM_API_KEY` | Phase 3 | Voice STT/TTS |
| `MCP_SERVER_URL` | Phase 3 | Google Docs/Gmail MCP server URL |
| `GOOGLE_TRACKING_DOC_ID` | Phase 3 | Google Doc for booking tracking |
| `GOOGLE_TOKEN_JSON` | Phase 3 (HF) | OAuth token JSON string |
| `ADVISOR_EMAIL` | Phase 3 | Email for HITL notifications |
| `GOOGLE_MEET_URL` | Phase 3 | Fixed Meet URL for all bookings |

---

## Running Locally

```bash
# Terminal 1
python3 -m uvicorn phase1_knowledgeBase.app.main:app --host 0.0.0.0 --port 8101

# Terminal 2
python3 -m uvicorn phase2_weeklyPulse.app.main:app --host 0.0.0.0 --port 8102

# Terminal 3
python3 -m uvicorn phase3_voiceScheduler.app.main:app --host 0.0.0.0 --port 8103

# Terminal 4
PHASE1_BASE_URL=http://localhost:8101 \
PHASE2_BASE_URL=http://localhost:8102 \
PHASE3_BASE_URL=http://localhost:8103 \
python3 -m uvicorn phase4_integrationHub.app.main:app --host 0.0.0.0 --port 8000

# Terminal 5
cd phase5_frontend && npm start
```

---

## HuggingFace Deployment

- Space: https://huggingface.co/spaces/ashishsankhua/investor-ops-intelligence-suite
- GitHub: https://github.com/asankhua/investor-ops-intelligence-suite
- Auto-sync: GitHub Actions pushes to HF on every commit to `main`
- All 5 services run in one Docker container via supervisord + nginx

### HF Secrets Required (no trailing newlines)
`PINECONE_API_KEY`, `OPENROUTER_API_KEY`, `GROQ_API_KEY`, `SARVAM_API_KEY`,
`MCP_SERVER_URL`, `GOOGLE_TRACKING_DOC_ID`, `ADVISOR_EMAIL`, `GOOGLE_MEET_URL`,
`GOOGLE_TOKEN_JSON`, `PINECONE_INDEX_NAME`, `PINECONE_CLOUD`, `PINECONE_REGION`

---

## API Gateway Routes (Phase 4 :8000)

| Method | Path | Proxies To |
|--------|------|-----------|
| GET | `/health` | Phase 4 health |
| GET | `/api/v1/dashboard/stats` | Aggregates P1+P2+P3 |
| GET | `/api/v1/dashboard/pillars` | P1+P2+P3 health |
| GET | `/api/v1/dashboard/activity` | P3 MCP logs + P4 state |
| GET | `/api/v1/dashboard/performance` | P1+P2+P3 health score |
| POST | `/api/v1/query` | Phase 1 RAG |
| GET | `/api/v1/funds/search` | Phase 1 fund search |
| GET | `/api/v1/sources` | Phase 1 sources |
| GET | `/api/v1/pillar-b/themes` | Phase 2 themes |
| GET | `/api/v1/pillar-b/weekly-pulse` | Phase 2 pulse |
| GET | `/api/v1/pillar-b/analytics` | Phase 2 analytics |
| POST | `/api/v1/pillar-c/conversation/message` | Phase 3 chat |
| POST | `/api/v1/pillar-c/conversation/voice` | Phase 3 voice |
| GET | `/api/v1/hitl/actions` | Phase 3 HITL queue |
| POST | `/api/v1/hitl/approve/{id}` | Phase 3 approve → MCP |
| GET | `/api/v1/hitl/email/preview/{code}` | Phase 3 email draft |

---

## Cross-Pillar Data Flow

```
Phase 2 (Weekly Pulse)
  └── top_themes → Phase 3 ThemeProvider (port 8102)
        └── injected into voice greeting + email body

Phase 3 (Voice Scheduler)
  └── booking confirmed → Phase 4 SharedStateStore
        └── booking_code synced to Phase 2 weekly_pulse.json

Phase 3 (HITL Approve)
  └── MCP: POST /append_to_doc → Google Doc (GOOGLE_TRACKING_DOC_ID)
  └── MCP: POST /create_email_draft → Gmail (ADVISOR_EMAIL)
```

---

## Frontend Pages

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | Dashboard | Live stats, pillar cards, activity feed |
| `/knowledge-base` | PillarA | RAG chat, fund list, sources & citations |
| `/weekly-pulse` | PillarB | Themes, sentiment, analytics charts |
| `/voice-scheduler` | PillarC | Voice/text chat, booking, HITL approval |
| `/evals` | Evals | Run all 4 eval types, live results |
| `/hitl` | → redirect | Redirects to `/voice-scheduler` |
