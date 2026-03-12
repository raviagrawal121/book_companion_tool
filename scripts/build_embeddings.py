"""
Build Embeddings
================
Rebuilds ONLY the embeddings and FAISS index from already-chunked data.
Useful when you want to test a different embedding model without re-chunking.

For a full re-ingestion (new PDFs), use ingest_documents.py instead.

Usage:
    python scripts/build_embeddings.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.rag.loader import load_pdfs
from app.rag.chunker import split_documents
from app.rag.embeddings import get_embeddings
from app.rag.vector_store import save_index
from langchain_community.vectorstores import FAISS


def rebuild_embeddings():
    print("\n🔄 Rebuilding embeddings...\n")

    docs   = load_pdfs()
    chunks = split_documents(docs)

    print(f"\n🔗 Embedding {len(chunks)} chunks...")
    embeddings  = get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)

    save_index(vectorstore)
    print(f"\n✅ Done — {len(chunks)} chunks re-embedded and saved.\n")


if __name__ == "__main__":
    rebuild_embeddings()