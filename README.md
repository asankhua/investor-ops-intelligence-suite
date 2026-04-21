---
title: Investor Ops Intelligence Suite
emoji: 📊
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
app_port: 7860
---

# Investor Ops & Intelligence Suite

A full-stack AI platform for investor operations with 5 integrated phases:

- **Phase 1** — Smart-Sync Knowledge Base (Self-RAG, Pinecone, OpenRouter)
- **Phase 2** — Insight-Driven Weekly Pulse (Theme analysis, Groq)
- **Phase 3** — AI Voice Scheduler + HITL Approval + MCP (Gmail/Docs)
- **Phase 4** — Integration Hub API Gateway
- **Phase 5** — Unified React Dashboard

## Required Secrets (set in HF Space Settings)

| Secret | Description |
|--------|-------------|
| `PINECONE_API_KEY` | Pinecone vector DB key |
| `PINECONE_INDEX_NAME` | Pinecone index name |
| `OPENROUTER_API_KEY` | OpenRouter LLM key |
| `GROQ_API_KEY` | Groq theme classification key |
| `SARVAM_API_KEY` | Sarvam AI voice STT/TTS |
| `GOOGLE_TOKEN_JSON` | Google OAuth token JSON |
| `GOOGLE_TRACKING_DOC_ID` | Google Doc ID for tracking |
| `ADVISOR_EMAIL` | Email for HITL notifications |
| `GOOGLE_MEET_URL` | Fixed Google Meet URL |
