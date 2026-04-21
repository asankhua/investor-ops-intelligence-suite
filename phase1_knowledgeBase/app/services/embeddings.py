"""OpenRouter embeddings service used by Phase 1 RAG."""

import os
import logging
from typing import List, Union
from openai import OpenAI

logger = logging.getLogger(__name__)


class BGEEmbedder:
    """
    Embedding wrapper backed by OpenRouter's embeddings endpoint.
    Class name is preserved to avoid broader refactors.
    """

    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL", "openai/text-embedding-3-large")
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.dimension = int(os.getenv("EMBEDDING_DIMENSION", "3072"))
        self.client = None
        self._init_client()

    def _init_client(self):
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required for embeddings")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        logger.info(f"Embedding client initialized with model: {self.model_name}")

    def embed(self, texts: Union[str, List[str]]) -> List[List[float]]:
        if isinstance(texts, str):
            texts = [texts]
        if not texts:
            return []

        response = self.client.embeddings.create(model=self.model_name, input=texts)
        return [item.embedding for item in response.data]

    def embed_query(self, query: str) -> List[float]:
        return self.embed(query)[0]

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        return self.embed(documents)

    def get_dimension(self) -> int:
        return self.dimension
