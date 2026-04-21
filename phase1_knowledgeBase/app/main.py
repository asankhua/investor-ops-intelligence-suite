"""
Phase 1 Backend: Pillar A - Self-RAG Knowledge Base
FastAPI application for RAG query endpoint with 6-bullet response format.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
from dotenv import load_dotenv

# Load environment variables from root folder
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

from services.self_rag import SelfRAGPipeline
from utils.pii_masker import PIIMasker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Investor Intelligence Suite - Phase 1",
    description="Self-RAG Knowledge Base API (Pillar A)",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pii_masker = PIIMasker()
rag_pipeline: Optional[SelfRAGPipeline] = None
rag_init_error: Optional[str] = None

# Pydantic Models
class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    fund_name: Optional[str] = None

class SourceCitation(BaseModel):
    chunk_id: str
    document: str
    preview: str
    score: float
    source_url: Optional[str] = None

class SelfRAGDebug(BaseModel):
    query_expansion: str
    sufficiency_check: str
    retrieved_chunks: int

class QueryResponse(BaseModel):
    query: str
    bullets: List[Dict[str, Any]]  # {"text": str, "sources": List[str]}
    citations: List[SourceCitation]
    self_rag: SelfRAGDebug
    sources_used: Optional[List[str]] = None
    self_rag_loops: Optional[int] = None
    query_variants: Optional[List[str]] = None
    structured_citations: Optional[List[Dict[str, Any]]] = None

class FundSearchResponse(BaseModel):
    funds: List[Dict[str, Any]]
    count: int


def _ensure_rag_pipeline() -> Optional[SelfRAGPipeline]:
    """Lazy-init RAG pipeline when needed by query/index endpoints."""
    global rag_pipeline, rag_init_error

    if rag_pipeline is not None:
        return rag_pipeline

    try:
        from services.embeddings import BGEEmbedder
        from services.vector_store import PineconeStore

        embedder = BGEEmbedder()
        vector_store = PineconeStore(dimension=embedder.get_dimension())
        rag_pipeline = SelfRAGPipeline(embedder=embedder, vector_store=vector_store)
        rag_init_error = None
        logger.info("RAG pipeline initialized successfully")
        return rag_pipeline
    except Exception as e:
        rag_init_error = str(e)
        logger.error(f"RAG pipeline init failed: {rag_init_error}")
        return None


@app.on_event("startup")
async def startup_event():
    """Strict startup: Phase 1 is unhealthy unless full RAG stack initializes."""
    pipeline = _ensure_rag_pipeline()
    if pipeline is None:
        raise RuntimeError(
            f"RAG pipeline initialization failed. Check Pinecone/OpenRouter/BGE setup. Error: {rag_init_error}"
        )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "phase": 1,
        "pillar": "A",
        "rag_ready": rag_pipeline is not None,
        "rag_init_error": rag_init_error,
    }

# Main RAG query endpoint
@app.post("/api/v1/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    Self-RAG query endpoint with 6-bullet response format and source citations.
    """
    try:
        pipeline = _ensure_rag_pipeline()
        if pipeline is None:
            raise HTTPException(
                status_code=503,
                detail=(
                    "RAG pipeline is not initialized. Please verify Pinecone and embedding setup, "
                    "then restart Phase 1 backend."
                ),
            )

        # Mask PII in query
        masked_query = pii_masker.mask(request.query)
        logger.info(f"Query received (PII masked): {masked_query[:50]}...")
        
        # Execute Self-RAG pipeline
        result = await pipeline.query(
            query=masked_query,
            top_k=request.top_k,
            fund_name=request.fund_name
        )
        
        return QueryResponse(
            query=request.query,
            bullets=result["bullets"],
            citations=result["citations"],
            self_rag=result["self_rag"],
            sources_used=result.get("sources_used"),
            self_rag_loops=result.get("self_rag_loops"),
            query_variants=result.get("query_variants"),
            structured_citations=result.get("structured_citations"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

# Fund list endpoint
@app.get("/api/v1/funds/search", response_model=FundSearchResponse)
async def search_funds(query: Optional[str] = None):
    """
    Search available funds in the knowledge base.
    """
    try:
        pipeline = _ensure_rag_pipeline()
        if pipeline is None:
            raise HTTPException(
                status_code=503,
                detail="RAG pipeline is not initialized. Fund search requires Phase 1 RAG services.",
            )
        funds = await pipeline.search_funds(query or "")
        return FundSearchResponse(funds=funds, count=len(funds))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fund search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Sources endpoint
@app.get("/api/v1/sources")
async def get_sources():
    """
    Get all available document sources.
    """
    try:
        pipeline = _ensure_rag_pipeline()
        if pipeline is None:
            raise HTTPException(
                status_code=503,
                detail="RAG pipeline is not initialized. Sources endpoint requires Phase 1 RAG services.",
            )
        sources = await pipeline.get_sources()
        return {"sources": sources}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sources retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Index documents endpoint (for initial setup)
@app.post("/api/v1/index")
async def index_documents():
    """
    Index all documents from data/ragData into Pinecone.
    """
    try:
        pipeline = _ensure_rag_pipeline()
        if pipeline is None:
            raise HTTPException(
                status_code=503,
                detail="RAG pipeline is not initialized. Cannot index documents without Pinecone/embedding setup.",
            )
        result = await pipeline.index_documents()
        return {
            "status": "success",
            "indexed": result["count"],
            "message": f"Successfully indexed {result['count']} chunks"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Indexing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
