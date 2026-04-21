# Phase 1 Backend: Self-RAG Knowledge Base (Pillar A)

Self-RAG API implementation for Investor Ops & Intelligence Suite.

## Features

- **Self-RAG Pipeline**: Query expansion, sufficiency checks, 6-bullet responses
- **BGE Embeddings**: BAAI/bge-large-en-v1.5 (1024-dim)
- **Pinecone Vector Store**: Document storage with metadata filtering
- **PII Masking**: [REDACTED] tokens for sensitive data
- **FastAPI**: REST endpoints with auto-generated docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/query` | Main RAG query with 6-bullet format |
| GET | `/api/v1/funds/search` | Search available funds |
| GET | `/api/v1/sources` | Get document sources |
| POST | `/api/v1/index` | Index documents to Pinecone |
| GET | `/health` | Health check |

## Setup

### 1. Environment Variables

Create `.env` in root folder:

```env
PINECONE_API_KEY=your_key
PINECONE_ENVIRONMENT=your_env
PINECONE_INDEX_NAME=investor-kb
OPENROUTER_API_KEY=your_key
BGE_MODEL_PATH=BAAI/bge-large-en-v1.5
```

### 2. Install Dependencies

```bash
cd phase1_knowledgeBase
pip install -r requirements.txt
```

### 3. Index Documents

```bash
python -c "import asyncio; from app.main import *; asyncio.run(rag_pipeline.index_documents())"
```

### 4. Run Server

```bash
uvicorn app.main:app --reload
```

## Docker

```bash
docker build -t phase1-backend .
docker run -p 8000:8000 --env-file ../.env phase1-backend
```

## Self-RAG Response Format

```json
{
  "query": "What is exit load for ELSS?",
  "bullets": [
    {"text": "Exit load is 1% if redeemed within 1 year", "sources": ["M1.1"]},
    {"text": "ELSS has 3-year lock-in period", "sources": ["M1"]},
    ...
  ],
  "citations": [...],
  "self_rag": {
    "query_expansion": "3 variants",
    "sufficiency_check": "Sufficient",
    "retrieved_chunks": 5
  }
}
```
