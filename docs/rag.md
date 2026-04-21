# RAG - Phase 1: Smart-Sync Knowledge Base

## Overview

Self-RAG pipeline answering fund/fee questions with 6-bullet responses and source citations. Backed by Pinecone vector DB and OpenRouter embeddings.

---

## Architecture

```
User query
  │
  ▼
PIIMasker.mask(query)          — redact emails, phones, names
  │
  ▼
BGEEmbedder.embed_query()      — OpenRouter text-embedding-3-large (dim 3072)
  │
  ▼
PineconeStore.query()          — top_k chunks from investor-kb index
  │
  ▼
SufficiencyCheck               — are retrieved chunks enough?
  ├── YES → generate response
  └── NO  → QueryExpansion → re-retrieve (max 1 loop)
  │
  ▼
ResponseGenerator              — GPT-4o via OpenRouter
  └── JSON schema: {bullets: [{text, sources}], citations: [...]}
  │
  ▼
QueryResponse returned
  └── bullets (max 6), citations, self_rag debug info
```

---

## Key Files

| File | Role |
|------|------|
| `phase1_knowledgeBase/app/main.py` | FastAPI endpoints, graceful startup |
| `phase1_knowledgeBase/app/services/self_rag.py` | Main pipeline orchestrator |
| `phase1_knowledgeBase/app/services/embeddings.py` | BGEEmbedder (OpenRouter) |
| `phase1_knowledgeBase/app/services/vector_store.py` | PineconeStore |
| `phase1_knowledgeBase/app/services/query_expansion.py` | Expand query on miss |
| `phase1_knowledgeBase/app/services/sufficiency_check.py` | Check retrieval quality |
| `phase1_knowledgeBase/app/services/response_generator.py` | 6-bullet GPT-4o generation |
| `phase1_knowledgeBase/app/utils/pii_masker.py` | PII redaction |

---

## API Endpoints (:8101)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | `{status, rag_ready, rag_init_error}` |
| GET | `/debug` | Env var check (keys set, model names) |
| POST | `/api/v1/query` | RAG query → 6-bullet response |
| GET | `/api/v1/funds/search?query=` | Search fund list |
| GET | `/api/v1/sources` | All indexed document sources |
| POST | `/api/v1/index` | Index documents from data/ragData |

---

## Response Format

```json
{
  "query": "what are HDFC fund fees",
  "bullets": [
    {"text": "HDFC Flexi Cap has expense ratio of 0.79%", "sources": ["S1"]},
    ...
  ],
  "citations": [
    {
      "chunk_id": "hdfc-flexi-cap-001",
      "document": "hdfc-flexi-cap-fund-direct-plan-growth-option-3184.json",
      "preview": "Expense ratio: 0.79% (Direct plan)",
      "score": 0.92,
      "source_url": "https://..."
    }
  ],
  "self_rag": {
    "query_expansion": "HDFC Flexi Cap expense ratio direct plan",
    "sufficiency_check": "sufficient",
    "retrieved_chunks": 5
  }
}
```

---

## Data

Fund JSONs in `data/ragData/`:
- `hdfc-banking-financial-services-fund-direct-growth-1006661.json`
- `hdfc-defence-fund-direct-growth-1043873.json`
- `hdfc-flexi-cap-fund-direct-plan-growth-option-3184.json`
- `hdfc-focused-fund-direct-plan-growth-option-2795.json`
- `hdfc-mid-cap-fund-direct-plan-growth-option-3097.json`
- `hdfc-nifty-midcap-150-index-fund-direct-growth-1043788.json`
- `hdfc-nifty-private-bank-etf-1042349.json`
- `hdfc-small-cap-fund-direct-growth-option-3580.json`

Chunked data in `data/chunking/chunks.json`.

---

## Startup Behaviour

Phase 1 starts **gracefully** even if RAG init fails — runs in degraded mode returning 503 on queries. This prevents the whole container from crashing on HF if Pinecone key has issues.

Common init failure: trailing `\n` in `PINECONE_API_KEY` HF secret. Check `/debug` endpoint.

---

## Frontend Integration (PillarA.js)

- Fund list: `GET /api/v1/funds/search` on mount
- Chat: `POST /api/v1/query` on send
- Sources panel: updates from `citations` in each response (not static `/sources`)
- "View Source" button: uses `source_url` from citation, falls back to Google search

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PINECONE_API_KEY` | — | Required |
| `PINECONE_INDEX_NAME` | `investor-kb` | Index name |
| `PINECONE_CLOUD` | `aws` | Cloud provider |
| `PINECONE_REGION` | `us-east-1` | Region |
| `OPENROUTER_API_KEY` | — | Required for LLM + embeddings |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` | Base URL |
| `OPENROUTER_CHAT_MODEL` | `openai/gpt-4o` | Chat model |
| `EMBEDDING_MODEL` | `openai/text-embedding-3-large` | Embedding model |
| `EMBEDDING_DIMENSION` | `3072` | Vector dimension |
