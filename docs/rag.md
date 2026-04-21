# RAG Architecture - Smart-Sync Knowledge Base (Pillar A)

## Overview

The RAG (Retrieval-Augmented Generation) system powers Pillar A: Smart-Sync Knowledge Base using **Self-RAG (Self-Reflective RAG)** architecture. The system merges Mutual Fund FAQ (M1) with Fee Explainer (M1.1) for unified search with source citations, featuring query expansion, sufficiency checking, and controlled re-retrieval.

## Why Self-RAG for Mutual Fund Content

Self-RAG is particularly effective for mutual fund information because:

### 1. **Factual Accuracy with Source Citations**
- Mutual fund data (NAV, expense ratios, exit loads) requires 100% accuracy
- Self-RAG retrieves from authoritative sources (M1 FAQ, M1.1 Fee Explainer) with explicit citations
- Users can verify claims like "Exit load is 1.0%" against the original source

### 2. **Handling Varied User Queries**
- Same question asked different ways: "Why charged exit load?" vs "ELSS redemption fee?"
- Query expansion generates 2-3 variants automatically, ensuring comprehensive retrieval
- Dense retrieval with OpenRouter embeddings captures semantic similarity across phrasings

### 3. **Multi-Source Knowledge Merging**
- M1 (FAQ): General fund information, returns, risk profiles
- M1.1 (Fee Explainer): Specific fee structures, exit load rules, expense breakdowns
- Unified search across both sources with source attribution in responses

### 4. **Self-Correction for Incomplete Retrieval**
- If initial retrieval misses key information (e.g., missing exit load details), sufficiency check detects this
- System automatically re-retrieves with expanded query (max 1 loop)
- Ensures responses are based on complete information, not partial matches

### 5. **Structured, Digestible Responses**
- Financial queries demand clarity: 6-bullet constraint prevents information overload
- JSON schema enforcement ensures consistent formatting
- No hallucinated investment advice - strictly source-based answers

### Content Benefits
| Challenge | How Self-RAG Solves It |
|-----------|----------------------|
| **Multiple fund variants** | Semantic chunking groups by topic (fees, returns, risk) not just fund name |
| **Numeric comparisons** | Metadata filtering: `{"exit_load": {"$lte": 1.0}}` for "funds with low exit load" |
| **Evolving NAV data** | Retrieved from latest scraped data in `chunks.json` |
| **Regulatory compliance** | Guardrails prevent investment advice; citations enable verification |
| **User trust** | Source tags [M1/M1.1] let users see where each fact comes from |

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PILLAR A: SELF-RAG ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  UNIFIED SEARCH UI (React/Vanilla JS/HTML-CSS)                   │   │
│  │  ┌──────────────┐  ┌──────────────────────────────────────┐  │   │
│  │  │ Query Input  │  │ Response (6 bullets + Citations)     │  │   │
│  │  │              │  │ [Source: M1] [Source: M1.1]          │  │   │
│  │  └──────────────┘  └──────────────────────────────────────┘  │   │
│  └────────────────────┬──────────────────────────────────────────┘   │
│                       │                                                 │
│  ┌────────────────────▼──────────────────────────────────────────┐   │
│  │  SELF-RAG PIPELINE (LangChain + LangGraph)                     │   │
│  │                                                                 │   │
│  │  ┌─────────────────────────────────────────────────────────────┐ │   │
│  │  │ 1. QUERY EXPANSION (GPT-4o-mini)                            │ │   │
│  │  │    User: "Why charged exit load?"                          │ │   │
│  │  │    Variants: ["ELSS exit load rules", "mutual fund          │ │   │
│  │  │              redemption fees", "exit load holding period"] │ │   │
│  │  └─────────────────────────────────────────────────────────────┘ │   │
│  │                              ↓                                    │   │
│  │  ┌─────────────────────────────────────────────────────────────┐ │   │
│  │  │ 2. DENSE RETRIEVAL (Pinecone + OpenRouter embeddings)       │ │   │
│  │  │    ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │ │   │
│  │  │    │  M1 Chunks  │  │ M1.1 Chunks │  │ Metadata Filter │  │ │   │
│  │  │    │ (Semantic)  │  │ (Headers)   │  │ (source, etc.)  │  │ │   │
│  │  │    └─────────────┘  └─────────────┘  └─────────────────┘  │ │   │
│  │  └─────────────────────────────────────────────────────────────┘ │   │
│  │                              ↓                                    │   │
│  │  ┌─────────────────────────────────────────────────────────────┐ │   │
│  │  │ 3. SUFFICIENCY CHECK (GPT-4o-mini)                           │ │   │
│  │  │    "Do retrieved chunks answer: Why was I charged?"         │ │   │
│  │  │    • YES → Continue to generation                          │ │   │
│  │  │    • NO  → Expand query → Re-retrieve (max 1 loop)         │ │   │
│  │  └─────────────────────────────────────────────────────────────┘ │   │
│  │                              ↓                                    │   │
│  │  ┌─────────────────────────────────────────────────────────────┐ │   │
│  │  │ 4. RESPONSE GENERATION (GPT-4o via OpenRouter)              │ │   │
│  │  │    • System: "Answer using ONLY provided sources"            │ │   │
│  │  │    • Format: 6 bullets max, JSON schema enforced           │ │   │
│  │  │    • Guardrails: No investment advice, no PII                │ │   │
│  │  │    • Citations: [Source: M1], [Source: M1.1]               │ │   │
│  │  └─────────────────────────────────────────────────────────────┘ │   │
│  │                                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Key Design Patterns

### Self-RAG (Self-Reflective RAG)
LLM evaluates retrieved chunk sufficiency before generation. If chunks are insufficient, system re-expands query and re-retrieves (max 1 loop) for quality assurance.

### Query Expansion
LLM generates 2-3 semantically similar query variants from user input to improve retrieval coverage (e.g., "exit load" → "redemption fee", "holding period").

### Dense Retrieval with Metadata Filtering
Pinecone vector search using OpenRouter embeddings (`openai/text-embedding-3-large`), combined with metadata filters for source (M1/M1.1), exit_load, expense_ratio, and AUM ranges.

### Source Tagging
Add metadata `{"source": "M1"}` or `{"source": "M1.1"}` during document indexing; retriever returns tagged chunks for citation.

### 6-Bullet Constraint
Enforced via GPT-4o `response_format={"type": "json_object"}` with strict JSON schema:
```json
{
  "bullets": ["string"],
  "sources_used": ["M1"|"M1.1"],
  "citations": [{"bullet_index": 0, "source": "M1", "doc_id": "..."}]
}
```

## Self-RAG Implementation

```python
from openai import OpenAI
from langchain_pinecone import PineconeVectorStore
from openai import OpenAI
from langchain_experimental.text_splitter import SemanticChunker

# Initialize OpenRouter client (for GPT-4o access)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="${OPENROUTER_API_KEY}"
)

# Embeddings: OpenRouter embeddings endpoint
embedding_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="${OPENROUTER_API_KEY}"
)
EMBEDDING_MODEL = "openai/text-embedding-3-large"

# Vector DB: Pinecone with metadata filtering
vectorstore = PineconeVectorStore(
    index_name="fund-docs",
    embedding=embeddings,
    namespace="pillar-a"
)

# Self-RAG Pipeline
def self_rag_query(user_query: str):
    # Step 1: Query Expansion
    expansion_prompt = f"Generate 2-3 variants of: {user_query}"
    variants = generate_query_variants(expansion_prompt)
    
    # Step 2: Dense Retrieval with metadata filter
    all_chunks = []
    for variant in variants:
        chunks = vectorstore.similarity_search(
            variant,
            k=10,
            filter={"source": {"$in": ["M1", "M1.1"]}}
        )
        all_chunks.extend(chunks)
    
    # Deduplicate and get top 10
    unique_chunks = deduplicate_chunks(all_chunks)[:10]
    
    # Step 3: Sufficiency Check (GPT-4o-mini - cheap)
    sufficiency = check_sufficiency(unique_chunks, user_query)
    
    # Step 4: Re-retrieve if needed (max 1 loop)
    if not sufficiency["sufficient"]:
        expanded_query = sufficiency["expanded_query"]
        more_chunks = vectorstore.similarity_search(expanded_query, k=10)
        unique_chunks = (unique_chunks + more_chunks)[:10]
    
    # Step 5: Generate (GPT-4o via OpenRouter - quality)
    response = generate_6_bullets(unique_chunks, user_query)
    return response
```

## Chunking Strategy

| Source | Strategy | Chunk Size | Overlap | Rationale |
|--------|----------|------------|---------|-----------|
| **M1 (Fund Factsheets)** | **Semantic Chunker** (LLM-based) | 300-500 tokens | 50 tokens | Atomic fact units for Self-RAG reflection; each chunk is a complete thought (fund identity, performance, or fees) |
| **M1.1 (Fee Explainer)** | `MarkdownHeaderTextSplitter` | N/A (header-based) | N/A | Fee logic is hierarchical; preserves structure (## Headers, ### Sub-headers) |

### Implementation

```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain.text_splitter import MarkdownHeaderTextSplitter
# NOTE: Current backend uses structured JSON chunking from data/ragData and
# writes pre-chunked output to data/chunking/chunks.json.
# `embeddings` below is a placeholder embedding backend used by SemanticChunker.
embeddings = YourEmbeddingBackend()

# M1: Semantic chunking - atomic fact units
m1_splitter = SemanticChunker(
    embeddings=embeddings,
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=85
)

# Extract structured text from JSON for chunking
def extract_fund_text(json_data):
    return f"""
    Fund: {json_data['name']}
    NAV: {json_data['overview']['nav']}
    Returns 1Y: {json_data['overview']['returns_1y']}
    Returns 3Y: {json_data['overview']['returns_3y']}
    Expense Ratio: {json_data['overview']['expense_ratio']}
    Exit Load: {json_data['overview']['exit_load']}
    Lock-in: {json_data['overview']['lock_in']}
    """

# Chunk and add metadata for Pinecone filtering
for json_file in rag_data:
    text = extract_fund_text(json_file)
    chunks = m1_splitter.create_documents([text])
    
    for chunk in chunks:
        chunk.metadata.update({
            "source": "M1",
            "fund_name": json_file['name'],
            "exit_load": float(json_file['overview']['exit_load'].replace('%', '')),
            "expense_ratio": float(json_file['overview']['expense_ratio'].replace('%', '')),
            "aum_cr": parse_aum(json_file['overview']['aum']),
            "risk": json_file['overview']['risk']
        })

# M1.1: Header-based for fee explainer
m1_1_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[("##", "Header 2"), ("###", "Header 3")]
)

fee_chunks = m1_1_splitter.split_text(fee_explainer_markdown)
for chunk in fee_chunks:
    chunk.metadata["source"] = "M1.1"
    chunk.metadata["doc_type"] = "fee_explainer"
```

## Tech Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **RAG Architecture** | **Self-RAG (Self-Reflective)** | Quality assurance via sufficiency checking; max 1 re-retrieval loop |
| **Retrieval Strategy** | Dense Retrieval + Query Expansion + Metadata Filtering | Pinecone dense search with expanded queries and numeric filters |
| **RAG Pipeline** | LangChain + LangGraph (v0.2+) | Self-RAG orchestration, citation tracking, agent workflows |
| **Vector DB** | **Pinecone** | Cloud-native, advanced metadata filtering, LangChain native integration |
| **Embeddings** | **OpenRouter `openai/text-embedding-3-large`** | Managed API embeddings, production-friendly, 3072-dim |
| **LLM (Generation)** | **OpenRouter (GPT-4o)** | Reliable JSON mode for 6-bullet constraint; model routing support |
| **LLM (Reflection)** | **OpenRouter (GPT-4o-mini)** | Cost-effective for Self-RAG sufficiency checks |
| **Alternative (Voice)** | **Groq** | Low-latency option for voice agent integration |

## API Specification

```python
class KnowledgeBaseAPI:
    def query(self, question: str) -> UnifiedResponse:
        """
        Args:
            question: User question (may span M1 + M1.1)
        
        Returns:
            UnifiedResponse:
                - bullets: List[dict] (max 6, each `{text, sources}`)
                - citations: List[SourceTag]
                - sources_used: List[str]  # ["M1", "M1.1"]
                - self_rag_loop_count: int  # 0 or 1 (re-retrieval indicator)
        """
```

## Project Structure

```
src/pillar_a/
├── __init__.py
├── self_rag.py           # Self-RAG orchestrator (LangGraph)
├── query_expansion.py    # LLM-based query variant generation
├── sufficiency_check.py  # GPT-4o-mini reflection step
├── retrievers.py         # M1 + M1.1 Pinecone retrievers
├── response_generator.py # 6-bullet formatter (GPT-4o)
└── vector_stores.py      # Pinecone management with metadata
```

## Dependencies

```txt
# RAG Dependencies (Self-RAG + Pinecone)
langchain>=0.3.0
langchain-openai>=0.2.0
langchain-community>=0.3.0
langchain-pinecone>=0.1.0
langchain-experimental>=0.3.0
langgraph>=0.2.0
pinecone-client>=3.0.0
tiktoken>=0.8.0

# OpenRouter integration (for GPT-4o access)
openai>=1.0.0

# Optional local embedding stack (legacy/offline experiments)
# sentence-transformers>=3.0.0
# transformers>=4.35.0

# Optional: Local vector DB for dev
# chromadb>=0.5.0  # Uncomment for local testing
```

## Data Flow (Self-RAG Pipeline)

```
User Query → Query Expansion (GPT-4o-mini) → Dense Retrieval (Pinecone + OpenRouter embeddings)
                                                    ↓
                              ┌─────────────────────┼─────────────────────┐
                              ▼                     ▼                     ▼
                        M1 Fund Data            M1.1 Fee Logic         Metadata Filter
                        (Semantic Chunks)       (Header Chunks)        (source, exit_load, etc.)
                              │                     │
                              └─────────────────────┴─────────────────────┘
                                                    ↓
                                        Top 10 Unique Chunks
                                                    ↓
                              Sufficiency Check (GPT-4o-mini)
                                                    ↓
                              ┌─────────────────────────────────────────┐
                              ▼                                         ▼
                        Sufficient?                                  Insufficient?
                              │                                         │
                              ↓                                         ↓
                    Generate 6 Bullets                         Expand Query
                    (GPT-4o via OpenRouter)                      ↓
                                                    Re-retrieve (max 1 loop)
                                                    ↓
                                    Unified Response (6 bullets + citations)
```

📄 **Wireframes & Frontend Implementation**: See [wireframe.md](wireframe.md) Section 2: Pillar A - RAG Chat UI for complete wireframe layouts and frontend implementations (React, Vanilla JS, HTML/CSS).

## Backend API for Frontend

**FastAPI Backend (for React/Vanilla JS frontends)**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class QueryRequest(BaseModel):
    query: str
    user_id: Optional[str] = None

class Citation(BaseModel):
    bullet_index: int
    source: str  # "M1" or "M1.1"
    doc_id: str

class QueryResponse(BaseModel):
    bullets: List[dict]  # [{"text": str, "sources": List[str]}], max 6
    sources_used: List[str]  # e.g., ["M1", "M1.1"]
    citations: List[Citation]
    self_rag_loops: int  # 0 or 1 (re-retrieval count)
    query_variants: List[str]  # Expanded query variants used
    structured_citations: List[dict]  # [{"bullet_index", "source", "doc_id"}]

@app.post("/api/v1/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process Self-RAG query and return response with citations.
    
    Pipeline:
    1. Query Expansion (GPT-4o-mini)
    2. Dense Retrieval (Pinecone + OpenRouter embeddings)
    3. Sufficiency Check (GPT-4o-mini)
    4. Re-retrieve if needed (max 1 loop)
    5. Generate 6 bullets (GPT-4o via OpenRouter)
    """
    # Implementation
    return QueryResponse(
        bullets=["..."],
        sources_used=["M1", "M1.1"],
        citations=[...],
        self_rag_loops=0,  # or 1 if re-retrieval occurred
        query_variants=["exit load rules", "redemption fees"]
    )

@app.get("/api/v1/funds/search")
async def search_funds(query: Optional[str] = None):
    """
    Search available mutual funds for Pillar A Fund List panel.
    Supports wireframe.md Section 2 - Fund List search functionality.
    """
    # Search fund names from M1/M1.1 metadata
    return {
        "funds": [
            {"name": "HDFC Top 100", "category": "Large Cap"},
            {"name": "SBI Blue Chip", "category": "Large Cap"},
            # ... filtered results
        ],
        "total": 150,
        "query": query
    }
```

## Development Details

### Pinecone Setup & Configuration

**Index Creation**:
```python
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="${PINECONE_API_KEY}")

# Create index (dimension must match configured embedding model)
pc.create_index(
    name="fund-docs",
    dimension=3072,
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)

# Metadata schema for filtering
metadata_config = {
    "source": ["M1", "M1.1"],
    "fund_name": "string",
    "exit_load": "float",        # For $lte/$gte filters
    "expense_ratio": "float",
    "aum_cr": "float",
    "risk": "string"
}
```

**Namespace Strategy**:
- `namespace="pillar-a"` for all fund docs
- Single namespace simplifies queries; use metadata filters for source separation

### Embeddings Setup (Current: OpenRouter API)

**Local Caching**:
```python
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# Test embedding dimension
sample_embedding = client.embeddings.create(
    model=os.getenv("EMBEDDING_MODEL", "openai/text-embedding-3-large"),
    input=["test"]
).data[0].embedding
assert len(sample_embedding) == int(os.getenv("EMBEDDING_DIMENSION", "3072"))
```

**Legacy Alternative** (optional local embeddings):
```python
# Local BGE embedding setup can be used for offline experiments,
# but current production path uses OpenRouter embeddings.
```

### OpenRouter Integration

**Client Configuration**:
```python
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    default_headers={
        "HTTP-Referer": "https://your-app.com",  # Required by OpenRouter
        "X-Title": "Investor Intelligence Suite"
    }
)

# Cost tracking per request
def track_cost(response):
    usage = response.usage
    cost = calculate_openrouter_cost(
        model="openai/gpt-4o",
        input_tokens=usage.prompt_tokens,
        output_tokens=usage.completion_tokens
    )
    logger.info(f"Request cost: ${cost:.4f}")
```

**JSON Mode Enforcement**:
```python
# 6-bullet response with strict schema
response = client.chat.completions.create(
    model="openai/gpt-4o",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT_6_BULLETS},
        {"role": "user", "content": f"Context: {chunks}\n\nQuestion: {query}"}
    ],
    response_format={
        "type": "json_object"
    },
    temperature=0.1,  # Low temp for consistent formatting
    max_tokens=500
)

result = json.loads(response.choices[0].message.content)
assert len(result["bullets"]) <= 6, "Must not exceed 6 bullets"
```

### Query Expansion Implementation

**Variant Generation**:
```python
QUERY_EXPANSION_PROMPT = """Generate 2-3 alternative phrasings of the user's question to improve search coverage.
Focus on financial terminology variations.

User question: {query}

Return JSON format:
{{
    "variants": [
        "original question",
        "alternative phrasing 1",
        "alternative phrasing 2"
    ]
}}"""

def generate_query_variants(query: str) -> List[str]:
    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",  # Cheap for this task
        messages=[{
            "role": "user",
            "content": QUERY_EXPANSION_PROMPT.format(query=query)
        }],
        response_format={"type": "json_object"},
        temperature=0.3
    )
    
    result = json.loads(response.choices[0].message.content)
    return result["variants"][:3]  # Max 3 variants
```

**Example Expansions**:
| Original | Variants Generated |
|----------|-------------------|
| "Why was I charged exit load?" | "ELSS exit load rules", "mutual fund redemption fees", "exit load holding period" |
| "Best fund for 5 years?" | "5 year investment fund", "long term mutual fund returns", "5Y performance funds" |

### Sufficiency Check Implementation

**Reflection Logic**:
```python
SUFFICIENCY_PROMPT = """Evaluate if the retrieved chunks sufficiently answer the user's question.

Question: {question}
Retrieved Chunks:
{chunks}

Respond in JSON:
{{
    "sufficient": true/false,
    "reason": "brief explanation",
    "missing_info": "what information is missing (if insufficient)",
    "expanded_query": "improved search query to find missing info (if insufficient)"
}}"""

def check_sufficiency(chunks: List[Document], query: str) -> Dict:
    chunks_text = "\n---\n".join([c.page_content for c in chunks])
    
    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": SUFFICIENCY_PROMPT.format(
                question=query,
                chunks=chunks_text
            )
        }],
        response_format={"type": "json_object"},
        temperature=0.1
    )
    
    return json.loads(response.choices[0].message.content)
```

**Max 1 Re-retrieval**:
```python
MAX_RAG_LOOPS = 1

def self_rag_with_limit(query: str) -> Tuple[Response, int]:
    loops = 0
    chunks = initial_retrieval(query)
    
    while loops < MAX_RAG_LOOPS:
        sufficiency = check_sufficiency(chunks, query)
        
        if sufficiency["sufficient"]:
            break
            
        # Re-retrieve with expanded query
        expanded_query = sufficiency.get("expanded_query", query)
        new_chunks = retrieve(expanded_query)
        chunks = deduplicate(chunks + new_chunks)[:10]
        loops += 1
    
    response = generate_response(chunks, query)
    return response, loops
```

### Semantic Chunker Configuration

**Optimal Parameters for Fund Data**:
```python
from langchain_experimental.text_splitter import SemanticChunker

m1_splitter = SemanticChunker(
    embeddings=embeddings,
    # Percentile determines breakpoint sensitivity
    # 85 = more chunks (smaller, atomic)
    # 95 = fewer chunks (larger, more context)
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=85,
    # Additional config
    min_chunk_size=100,    # Minimum tokens per chunk
    max_chunk_size=500     # Maximum tokens per chunk
)

# For fund data, we want atomic facts:
# - "Fund Identity + NAV"
# - "Performance Metrics" 
# - "Fee Structure"
# - "Investment Details"
```

### Sample Data Available

Pre-chunked fund data available in `data/chunking/chunks.json`:
- Semantically organized by `chunk_type`: `overview`, `returns`, `fees`, `min_investment`, `risk`
- Each chunk has: `id`, `text`, `scheme_id`, `scheme_name`, `tags`, `source_url`
- Extracted from 8 HDFC funds (Defence, Flexi Cap, Focused, Mid Cap, Small Cap, etc.)

**Chunk Structure**:
```json
{
  "id": "44452031-8e77-4c81-aaea-b37fd4f8e339",
  "text": "HDFC Mid Cap Fund – Overview\nSource: https://www.indmoney.com/...\n\nAs on 27 Feb 2026, the NAV of HDFC Mid Cap Fund is ₹223.96...",
  "scheme_id": "hdfc-mid-cap-fund-direct-plan-growth-option-3097",
  "scheme_name": "HDFC Mid Cap Fund",
  "source_url": "https://www.indmoney.com/mutual-funds/hdfc-mid-cap-fund-direct-plan-growth-option-3097",
  "chunk_type": "overview",
  "tags": ["overview", "fund-info"],
  "scraped_at": "2026-03-02T14:34:40.342657Z",
  "embedding_index": 0
}
```

### Chunk Ingestion into Pinecone

**Direct ingestion from pre-chunked data**:
```python
import json
from langchain.schema import Document

def load_chunks_to_pinecone(chunks_json_path: str = "data/chunking/chunks.json"):
    """Load pre-chunked data into Pinecone vector store."""
    
    with open(chunks_json_path) as f:
        chunks_data = json.load(f)
    
    documents = []
    for chunk in chunks_data:
        # Extract numeric values for metadata filtering
        metadata = {
            "source": "M1",
            "scheme_id": chunk["scheme_id"],
            "scheme_name": chunk["scheme_name"],
            "chunk_type": chunk["chunk_type"],
            "tags": chunk["tags"],
            # Parse expense ratio and exit load from text if present
            "expense_ratio": extract_expense_ratio(chunk["text"]),
            "exit_load": extract_exit_load(chunk["text"]),
            "chunk_id": chunk["id"]
        }
        
        doc = Document(
            page_content=chunk["text"],
            metadata=metadata
        )
        documents.append(doc)
    
    # Batch add to Pinecone
    vectorstore.add_documents(documents)
    print(f"✓ Ingested {len(documents)} chunks into Pinecone")
    
    # Chunk distribution by type
    from collections import Counter
    type_counts = Counter([c["chunk_type"] for c in chunks_data])
    print("Chunk types:", dict(type_counts))
    # Output: {'overview': 8, 'returns': 8, 'fees': 8, 'min_investment': 8, 'risk': 8}

def extract_expense_ratio(text: str) -> float:
    """Extract expense ratio from chunk text."""
    import re
    match = re.search(r'expense ratio.*?([\d.]+)%', text, re.IGNORECASE)
    return float(match.group(1)) if match else 0.0

def extract_exit_load(text: str) -> float:
    """Extract exit load from chunk text."""
    import re
    match = re.search(r'exit load.*?([\d.]+)%', text, re.IGNORECASE)
    return float(match.group(1)) if match else 0.0

# Run ingestion
if __name__ == "__main__":
    load_chunks_to_pinecone()
```

**Alternative: Raw fund JSONs**

If you need to regenerate chunks, raw data is also available in `data/ragData/`:
- 8 fund JSON files with `overview` containing NAV, returns, AUM, fees, risk
- Use `SemanticChunker` to create semantic chunks from these
- See previous section for chunking configuration

**Chunk Type Distribution**:
| Type | Count | Description |
|------|-------|-------------|
| `overview` | 8 | NAV, benchmark, AUM, inception |
| `returns` | 8 | Performance data, returns since inception |
| `fees` | 8 | Expense ratio, exit load |
| `min_investment` | 8 | SIP/lumpsum minimums |
| `risk` | 8 | Risk profile, turnover |
| **Total** | **~40** | Ready for embedding & retrieval |

### Cost Optimization

**Per-Request Cost Breakdown**:
| Step | Model | Input Tokens | Output Tokens | Cost |
|------|-------|--------------|---------------|------|
| Query Expansion | GPT-4o-mini | ~50 | ~100 | $0.000075 |
| Sufficiency Check | GPT-4o-mini | ~2000 | ~100 | $0.000315 |
| Generation | GPT-4o | ~2500 | ~300 | $0.00725 |
| **Total** | | | | **~$0.008/request** |

**Budget Controls**:
```python
# Monthly cost cap
MAX_MONTHLY_COST = 50.0  # USD
cost_tracker = CostTracker(limit=MAX_MONTHLY_COST)

@cost_tracker.track
def self_rag_query(query: str):
    if cost_tracker.current > MAX_MONTHLY_COST:
        raise CostLimitExceeded("Monthly budget exhausted")
    # ... implementation
```

### Error Handling

**Retrieval Failures**:
```python
def safe_retrieve(query: str, filter_dict: Dict) -> List[Document]:
    try:
        results = vectorstore.similarity_search(
            query, 
            k=10,
            filter=filter_dict
        )
        if not results:
            logger.warning(f"No results for query: {query}")
            return []
        return results
    except Exception as e:
        logger.error(f"Pinecone error: {e}")
        # Fallback: return empty, let sufficiency check handle it
        return []
```

**JSON Parse Failures**:
```python
import json
from json import JSONDecodeError

def safe_json_parse(response_text: str) -> Optional[Dict]:
    try:
        return json.loads(response_text)
    except JSONDecodeError:
        # Try to extract JSON from markdown code blocks
        import re
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass
        logger.error(f"Failed to parse JSON: {response_text[:100]}...")
        return None
```

### Testing Checklist

**Pre-Production**:
- [ ] OpenRouter embeddings output expected configured dimensions (default 3072)
- [ ] Pinecone index created with cosine metric
- [ ] Sample data ingested from `data/ragData/` (8 HDFC fund JSONs)
- [ ] Metadata filters work (test: `{"exit_load": {"$lte": 1.0}}`)
- [ ] Query expansion returns 2-3 variants
- [ ] Sufficiency check correctly identifies insufficient chunks
- [ ] 6-bullet JSON schema always valid
- [ ] Source citations present [Source: M1/M1.1]
- [ ] Cost per query <$0.01
- [ ] Max 1 re-retrieval loop enforced
- [ ] Fallback responses for empty retrieval
- [ ] Data sync scheduler configured (GitHub Actions cron)
- [ ] Data freshness indicator displays "Last updated" timestamp

---

## Data Sync Scheduler Architecture

### GitHub Actions Weekly Cron

**Workflow** (`.github/workflows/sync-fund-data.yml`):
```yaml
name: Sync Fund Data Weekly

on:
  schedule:
    # Run every Sunday at 2:00 AM UTC
    - cron: '0 2 * * 0'
  workflow_dispatch:  # Manual trigger

jobs:
  sync-and-update:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Fetch latest fund data
        env:
          SCRAPE_API_KEY: ${{ secrets.SCRAPE_API_KEY }}
        run: |
          python scripts/fetch_fund_data.py --output data/ragData/
      
      - name: Regenerate chunks
        run: |
          python scripts/generate_chunks.py \
            --input data/ragData/ \
            --output data/chunking/chunks.json
      
      - name: Sync to Pinecone
        env:
          PINECONE_API_KEY: ${{ secrets.PINECONE_API_KEY }}
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
        run: |
          python scripts/sync_to_pinecone.py \
            --chunks data/chunking/chunks.json \
            --index fund-docs \
            --namespace pillar-a
      
      - name: Update freshness timestamp
        run: |
          echo "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > data/last_sync.txt
      
      - name: Commit and push
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add data/chunking/chunks.json data/last_sync.txt
          git diff --quiet && git diff --staged --quiet || git commit -m "Weekly data sync: $(date +%Y-%m-%d)"
          git push
```

### Delta Sync Logic

**Only update changed funds** to minimize API calls:
```python
# scripts/sync_to_pinecone.py
import json
from datetime import datetime
from pinecone import Pinecone
from langchain.schema import Document

def sync_chunks_to_pinecone(chunks_path: str, index_name: str, namespace: str):
    """Sync chunks with delta update and freshness tracking."""
    
    # Load new chunks
    with open(chunks_path) as f:
        new_chunks = json.load(f)
    
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(index_name)
    
    # Get existing chunk IDs from Pinecone
    existing_stats = index.describe_index_stats()
    # Query for existing IDs logic here...
    
    # Find changed chunks (compare hash or timestamp)
    changed_chunks = []
    for chunk in new_chunks:
        chunk_hash = hash(chunk["text"])
        # Check if chunk changed or is new
        if not chunk_exists_in_pinecone(chunk["id"], index, namespace):
            changed_chunks.append(chunk)
    
    if not changed_chunks:
        print("✓ No changes detected, skipping sync")
        return
    
    # Delete old versions, insert new
    if changed_chunks:
        ids_to_delete = [c["id"] for c in changed_chunks]
        index.delete(ids=ids_to_delete, namespace=namespace)
        
        # Add new documents
        documents = [Document(page_content=c["text"], metadata={...}) 
                    for c in changed_chunks]
        vectorstore.add_documents(documents)
    
    # Update sync timestamp in metadata
    sync_time = datetime.utcnow().isoformat()
    index.update_metadata(namespace=namespace, metadata={"last_sync": sync_time})
    
    print(f"✓ Synced {len(changed_chunks)} changed chunks at {sync_time}")

def chunk_exists_in_pinecone(chunk_id: str, index, namespace: str) -> bool:
    """Check if chunk exists in Pinecone."""
    try:
        result = index.fetch(ids=[chunk_id], namespace=namespace)
        return len(result.vectors) > 0
    except:
        return False
```

### Alternative Schedulers

| Scheduler | Use Case | Complexity |
|-----------|----------|------------|
| **GitHub Actions** | Free for public repos, simple cron | Low |
| **AWS Lambda + EventBridge** | Production scale, serverless | Medium |
| **Airflow** | Complex pipelines, dependencies | High |
| **Render/ Railway cron** | Hosted backend with built-in scheduler | Low |

**Recommended**: GitHub Actions for MVP (free, version controlled), migrate to AWS Lambda for production scaling.

---

## Data Freshness Indicator

### Backend: Expose Sync Metadata

**Add to API Response**:
```python
from datetime import datetime
from pathlib import Path

# Read last sync timestamp
def get_data_freshness() -> dict:
    """Get data freshness metadata."""
    last_sync_file = Path("data/last_sync.txt")
    
    if last_sync_file.exists():
        last_sync = last_sync_file.read_text().strip()
        last_sync_dt = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
        days_since_sync = (datetime.utcnow() - last_sync_dt).days
        
        status = "fresh" if days_since_sync <= 7 else "stale" if days_since_sync <= 14 else "outdated"
        
        return {
            "last_sync": last_sync,
            "days_since_sync": days_since_sync,
            "status": status,
            "next_scheduled_sync": get_next_cron_date("0 2 * * 0").isoformat()
        }
    
    return {
        "last_sync": None,
        "days_since_sync": None,
        "status": "unknown",
        "next_scheduled_sync": None
    }

# Update API response model
class QueryResponse(BaseModel):
    bullets: List[dict]  # [{"text": str, "sources": List[str]}]
    sources_used: List[str]
    citations: List[dict]
    self_rag_loops: int
    query_variants: List[str]
    data_freshness: dict  # NEW: Add freshness metadata

@app.post("/api/v1/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    # ... existing Self-RAG logic ...
    
    return QueryResponse(
        bullets=bullets,
        sources_used=sources_used,
        citations=citations,
        self_rag_loops=loops,
        query_variants=variants,
        data_freshness=get_data_freshness()  # Include freshness
    )
```

### Frontend: Display Freshness Badge

**React Component**:
```jsx
const DataFreshnessBadge = ({ freshness }) => {
  if (!freshness?.last_sync) return null;
  
  const { status, days_since_sync, last_sync } = freshness;
  
  const statusConfig = {
    fresh: { color: '#10B981', emoji: '🟢', text: 'Data up to date' },
    stale: { color: '#F59E0B', emoji: '🟡', text: 'Data 1-2 weeks old' },
    outdated: { color: '#EF4444', emoji: '🔴', text: 'Data >2 weeks old' },
    unknown: { color: '#6B7280', emoji: '⚪', text: 'Sync status unknown' }
  };
  
  const config = statusConfig[status] || statusConfig.unknown;
  
  return (
    <div className="freshness-badge" style={{ borderColor: config.color }}>
      <span style={{ color: config.color }}>{config.emoji}</span>
      <span className="freshness-text">{config.text}</span>
      <span className="freshness-detail">
        Last updated: {days_since_sync === 0 ? 'Today' : `${days_since_sync} days ago`}
        ({new Date(last_sync).toLocaleDateString()})
      </span>
    </div>
  );
};
```

**CSS Styles**:
```css
.freshness-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-left: 3px solid;
  background: #f8f9fa;
  border-radius: 4px;
  margin-bottom: 16px;
  font-size: 0.9rem;
}

.freshness-text {
  font-weight: 500;
}

.freshness-detail {
  color: #666;
  font-size: 0.8rem;
  margin-left: auto;
}
```

**Vanilla JS Implementation**:
```javascript
function renderFreshnessBadge(freshness) {
  if (!freshness?.last_sync) return '';
  
  const configs = {
    fresh: { color: '#10B981', emoji: '🟢' },
    stale: { color: '#F59E0B', emoji: '🟡' },
    outdated: { color: '#EF4444', emoji: '🔴' }
  };
  
  const cfg = configs[freshness.status] || configs.fresh;
  const days = freshness.days_since_sync;
  const date = new Date(freshness.last_sync).toLocaleDateString();
  
  return `
    <div class="freshness-badge" style="border-color: ${cfg.color}">
      <span style="color: ${cfg.color}">${cfg.emoji}</span>
      <span>${days === 0 ? 'Updated today' : `Updated ${days} days ago`}</span>
      <span class="freshness-detail">${date}</span>
    </div>
  `;
}
```

### Freshness States

| Status | Days Since Sync | Color | Action |
|--------|----------------|-------|--------|
| 🟢 **Fresh** | ≤ 7 days | Green | None |
| 🟡 **Stale** | 8-14 days | Amber | Warning banner |
| 🔴 **Outdated** | > 14 days | Red | Alert + manual refresh option |
| ⚪ **Unknown** | No sync recorded | Gray | Show sync pending |

### Wireframe: RAG Chat with Freshness Indicator

```
┌─────────────────────────────────────────────────────────────────────────┐
│  📊 Smart-Sync Knowledge Base                                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  🟢 Data up to date                                                     │
│  Last updated: 2 days ago (Mar 18, 2026)                               │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 🔍 Search Query Input                                           │   │
│  │ ┌─────────────────────────────────────────────────────────┐    │   │
│  │ │ "What is the exit load for HDFC Mid Cap Fund?"         │ 🔍 │   │
│  │ └─────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 📄 Response (6 Bullets + Citations)                            │   │
│  │ ...                                                             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## References

1. [LangChain RAG Best Practices](https://python.langchain.com/docs/use_cases/question_answering/)
2. [LangGraph Agentic RAG](https://langchain-ai.github.io/langgraph/how-tos/agentic-rag/)
3. [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard) - Embedding model rankings
