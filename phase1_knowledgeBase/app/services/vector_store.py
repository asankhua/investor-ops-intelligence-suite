"""
Pinecone Vector Store Service
Handles vector storage and retrieval with metadata.
"""
import os
from typing import List, Dict, Any, Optional
import logging
from pinecone import Pinecone, ServerlessSpec

logger = logging.getLogger(__name__)

class PineconeStore:
    """
    Pinecone vector database client for storing and retrieving document embeddings.
    """
    
    def __init__(self, dimension: Optional[int] = None):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.environment = os.getenv("PINECONE_ENVIRONMENT")
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "investor-kb")
        self.namespace = os.getenv("PINECONE_NAMESPACE", "pillar-a")
        self.dimension = dimension or int(os.getenv("EMBEDDING_DIMENSION", "3072"))
        self.index = None
        self._init_pinecone()
    
    def _init_pinecone(self):
        """Initialize Pinecone client and connect to index."""
        try:
            pc = Pinecone(api_key=self.api_key)
            
            # Create index if it doesn't exist
            indexes = pc.list_indexes()
            existing = indexes.names() if hasattr(indexes, "names") else [idx["name"] for idx in indexes]
            if self.index_name not in existing:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                # Use env if provided, otherwise sensible defaults.
                cloud = os.getenv("PINECONE_CLOUD", "aws")
                region = os.getenv("PINECONE_REGION", "us-east-1")
                pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec=ServerlessSpec(cloud=cloud, region=region),
                )
            
            self.index = pc.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Pinecone initialization error: {e}")
            raise
    
    def upsert(self, vectors: List[Dict[str, Any]], namespace: Optional[str] = None):
        """
        Upsert vectors to Pinecone.
        
        Args:
            vectors: List of dicts with 'id', 'values', 'metadata'
            namespace: Pinecone namespace
        """
        try:
            target_ns = namespace or self.namespace
            self.index.upsert(vectors=vectors, namespace=target_ns)
            logger.info(f"Upserted {len(vectors)} vectors to namespace: {target_ns}")
        except Exception as e:
            logger.error(f"Upsert error: {e}")
            raise
    
    def query(
        self, 
        vector: List[float], 
        top_k: int = 5, 
        namespace: Optional[str] = None,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Query vectors from Pinecone.
        
        Args:
            vector: Query embedding vector
            top_k: Number of results to return
            namespace: Pinecone namespace
            filter_dict: Metadata filter
            
        Returns:
            List of matches with id, score, and metadata
        """
        try:
            target_ns = namespace or self.namespace
            result = self.index.query(
                vector=vector,
                top_k=top_k,
                namespace=target_ns,
                include_metadata=True,
                filter=filter_dict
            )
            
            matches = []
            for match in result.get("matches", []):
                matches.append({
                    "id": match.get("id"),
                    "score": match.get("score", 0.0),
                    "metadata": match.get("metadata", {})
                })
            
            return matches
            
        except Exception as e:
            logger.error(f"Query error: {e}")
            raise
    
    def delete(self, ids: List[str], namespace: Optional[str] = None):
        """Delete vectors by ID."""
        try:
            target_ns = namespace or self.namespace
            self.index.delete(ids=ids, namespace=target_ns)
            logger.info(f"Deleted {len(ids)} vectors from namespace: {target_ns}")
        except Exception as e:
            logger.error(f"Delete error: {e}")
            raise
    
    def fetch(self, ids: List[str], namespace: Optional[str] = None) -> Dict[str, Any]:
        """Fetch vectors by ID."""
        try:
            target_ns = namespace or self.namespace
            return self.index.fetch(ids=ids, namespace=target_ns)
        except Exception as e:
            logger.error(f"Fetch error: {e}")
            raise
    
    def get_stats(self, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Get index statistics."""
        try:
            stats = self.index.describe_index_stats()
            return {
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "total_vector_count": stats.total_vector_count,
                "namespaces": stats.namespaces
            }
        except Exception as e:
            logger.error(f"Stats error: {e}")
            raise
