"""
RAG Engine — In-memory vector store using OpenAI embeddings + cosine similarity
No Pinecone needed for demo. Drop-in replacement later.
"""

import os
import math
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ── In-memory vector store ──────────────────────────────────────────────────
_chunks: list[str] = []
_embeddings: list[list[float]] = []
_is_loaded = False


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
    """Split text into overlapping word-based chunks."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk.strip():
            chunks.append(chunk.strip())
        i += chunk_size - overlap
    return chunks


def _embed(texts: list[str]) -> list[list[float]]:
    """Batch embed texts using OpenAI."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    return [item.embedding for item in response.data]


def load_documents(file_paths: list[str]) -> None:
    """Load, chunk, and embed documents into memory."""
    global _chunks, _embeddings, _is_loaded

    if _is_loaded:
        return

    print("📚 Loading documents into RAG system...")
    all_chunks = []

    for path in file_paths:
        if not os.path.exists(path):
            print(f"  ⚠️  File not found: {path}")
            continue
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        chunks = _chunk_text(text)
        all_chunks.extend(chunks)
        print(f"  ✅ {path} → {len(chunks)} chunks")

    if not all_chunks:
        print("  ❌ No chunks created. Check document paths.")
        return

    print(f"🔗 Embedding {len(all_chunks)} chunks...")
    # Batch in groups of 100 to avoid API limits
    batch_size = 100
    all_embeddings = []
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i : i + batch_size]
        all_embeddings.extend(_embed(batch))
        print(f"  Embedded {min(i + batch_size, len(all_chunks))}/{len(all_chunks)}")

    _chunks = all_chunks
    _embeddings = all_embeddings
    _is_loaded = True
    print(f"✅ RAG system ready — {len(_chunks)} chunks loaded.")


def retrieve(query: str, top_k: int = 4) -> list[str]:
    """Retrieve top-k most relevant chunks for a query."""
    if not _is_loaded or not _chunks:
        return []

    query_embedding = _embed([query])[0]
    scores = [_cosine_similarity(query_embedding, emb) for emb in _embeddings]
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    return [_chunks[i] for i in top_indices]
