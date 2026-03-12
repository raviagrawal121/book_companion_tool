"""
Embeddings
==========
Provides a cached OpenAI embeddings instance.
Centralised here so the model name and API key come from one place.

Usage:
    from app.rag.embeddings import get_embeddings
    embeddings = get_embeddings()
"""

from functools import lru_cache
from langchain_openai import OpenAIEmbeddings

from app.core.settings import settings


@lru_cache(maxsize=1)
def get_embeddings() -> OpenAIEmbeddings:
    """
    Returns a cached OpenAIEmbeddings instance.
    Called during ingestion (batch) and retrieval (single query).
    """
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key,
    )