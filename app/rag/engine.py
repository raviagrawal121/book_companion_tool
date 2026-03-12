"""
RAG Engine
==========
Orchestrates the full ingestion pipeline:
    PDF → load → chunk → embed → FAISS index → save to disk

Called by scripts/ingest_documents.py.
Not imported at runtime — only used during ingestion.

Usage:
    from app.rag.engine import run_ingestion
    run_ingestion()
"""

from langchain_community.vectorstores import FAISS

from app.rag.loader import load_pdfs
from app.rag.chunker import split_documents
from app.rag.embeddings import get_embeddings
from app.rag.vector_store import save_index
from app.core.config import PathConfig


def run_ingestion() -> None:
    """
    Full pipeline: PDF → chunks → FAISS index → disk.

    Steps:
        1. Load all PDFs from data/raw/
        2. Split pages into overlapping chunks
        3. Embed chunks via OpenAI
        4. Build FAISS index
        5. Save index to data/vector_db/
    """
    print("\n🚀 Starting ingestion pipeline...\n")

    # Step 1 — Load
    print("━" * 40)
    print("Step 1 / 4  —  Loading PDFs")
    print("━" * 40)
    docs = load_pdfs()

    # Step 2 — Chunk
    print("\n" + "━" * 40)
    print("Step 2 / 4  —  Chunking documents")
    print("━" * 40)
    chunks = split_documents(docs)

    # Step 3 & 4 — Embed + index
    print("\n" + "━" * 40)
    print(f"Step 3 / 4  —  Embedding {len(chunks)} chunks via OpenAI")
    print("━" * 40)
    print("  (This may take 1–2 minutes for a full book...)")

    embeddings   = get_embeddings()
    vectorstore  = FAISS.from_documents(chunks, embeddings)
    print("  ✅ FAISS index built in memory")

    # Step 4 — Persist
    print("\n" + "━" * 40)
    print("Step 4 / 4  —  Saving index to disk")
    print("━" * 40)
    save_index(vectorstore)

    print(f"""
{'━' * 40}
🎉 Ingestion complete!
   • {len(docs)} pages loaded
   • {len(chunks)} chunks indexed
   • Index saved → {PathConfig.VECTOR_DB_DIR}
   
   Start the API:
     uvicorn app.main:app --reload --port 8000
{'━' * 40}
""")