"""
Retriever
=========
Queries the FAISS index and returns the most relevant Document chunks.
Also provides a helper to format chunks into a clean prompt context string.

Usage:
    from app.rag.retriever import retrieve, format_context
    docs    = retrieve("how do assets work?")
    context = format_context(docs)
"""

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from app.core.config import RAGConfig
from app.rag.vector_store import load_index


def retrieve(query: str, top_k: int = RAGConfig.TOP_K) -> list[Document]:
    """
    Embed the query and return top-k most semantically similar chunks.

    Args:
        query:  The user's question
        top_k:  Number of chunks to return (default from RAGConfig)

    Returns:
        List of Document objects with .page_content and .metadata
    """
    vectorstore: FAISS = load_index()
    docs = vectorstore.similarity_search(query, k=top_k)
    return docs


def retrieve_with_scores(
    query: str, top_k: int = RAGConfig.TOP_K
) -> list[tuple[Document, float]]:
    """
    Same as retrieve() but also returns cosine similarity scores.
    Useful for debugging retrieval quality during development.
    """
    vectorstore: FAISS = load_index()
    return vectorstore.similarity_search_with_score(query, k=top_k)


def format_context(docs: list[Document]) -> str:
    """
    Format retrieved chunks into a clean context block
    to inject into the LLM system prompt.
    """
    parts = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source_file", "book")
        page   = doc.metadata.get("page", "?")
        parts.append(
            f"[Source {i} — {source}, page {page}]\n"
            f"{doc.page_content.strip()}"
        )
    return "\n\n---\n\n".join(parts)


def get_source_labels(docs: list[Document]) -> list[str]:
    """Short source labels for each retrieved chunk."""
    return [
        f"{doc.metadata.get('source_file', 'book')} "
        f"p.{doc.metadata.get('page', '?')}"
        for doc in docs
    ]