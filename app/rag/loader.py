"""
Loader
======
Loads PDF files from the raw data directory into LangChain Documents.
Each page becomes one Document with metadata (source_file, page number).

Usage:
    from app.rag.loader import load_pdfs
    docs = load_pdfs()
"""

from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from app.core.config import PathConfig


def load_pdfs(directory: Path = PathConfig.RAW_DIR) -> list[Document]:
    """
    Load all PDFs from the given directory.
    Returns a flat list of Documents (one per page).
    Raises FileNotFoundError if no PDFs are found.
    """
    pdf_files = list(directory.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files found in: {directory}\n"
            "Add your book PDF to data/raw/ and try again."
        )

    all_docs: list[Document] = []

    for pdf_path in pdf_files:
        print(f"  📄 Loading: {pdf_path.name}")
        loader = PyPDFLoader(str(pdf_path))
        pages  = loader.load()

        # Enrich metadata for traceability in retrieval
        for page in pages:
            page.metadata["source_file"] = pdf_path.name
            page.metadata["page"]        = page.metadata.get("page", 0)

        all_docs.extend(pages)
        print(f"     ↳ {len(pages)} pages loaded")

    print(f"  ✅ Total: {len(all_docs)} pages across {len(pdf_files)} PDF(s)")
    return all_docs