"""
Vector Store
============
Handles saving and loading the FAISS index to/from disk.
Abstracts FAISS so it can be swapped for Pinecone in v2
by only changing this file.

Usage:
    from app.rag.vector_store import save_index, load_index
    save_index(vectorstore)
    vs = load_index()
"""

from functools import lru_cache
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from app.core.config import PathConfig
from app.rag.embeddings import get_embeddings


def save_index(vectorstore: FAISS) -> None:
    """Persist FAISS index to data/vector_db/."""
    PathConfig.VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(PathConfig.VECTOR_DB_DIR))
    print(f"  💾 FAISS index saved → {PathConfig.VECTOR_DB_DIR}")


@lru_cache(maxsize=1)
def load_index() -> FAISS:
    """
    Load FAISS index from disk. Cached — loads only once per process.
    Raises RuntimeError with clear instructions if index doesn't exist.
    """
    if not PathConfig.VECTOR_DB_DIR.exists() or \
       not (PathConfig.VECTOR_DB_DIR / "index.faiss").exists():
        raise RuntimeError(
            "FAISS index not found.\n"
            "Run ingestion first:\n"
            "  python scripts/ingest_documents.py"
        )

    embeddings = get_embeddings()
    vectorstore = FAISS.load_local(
        str(PathConfig.VECTOR_DB_DIR),
        embeddings,
        allow_dangerous_deserialization=True,  # safe — we built this index
    )
    print("✅ FAISS index loaded from disk")
    return vectorstore


def index_exists() -> bool:
    """Check whether a FAISS index has been built yet."""
    return (PathConfig.VECTOR_DB_DIR / "index.faiss").exists()