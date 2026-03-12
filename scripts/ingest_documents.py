"""
Ingest Documents
================
Run this once to build the FAISS vector index from your PDF(s).

Usage:
    python scripts/ingest_documents.py

Place your book PDF in data/raw/ before running.
"""

import sys
from pathlib import Path

# Add project root to path so app/ imports work
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.rag.engine import run_ingestion

if __name__ == "__main__":
    run_ingestion()