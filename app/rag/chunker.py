"""
Chunker
=======
Splits raw LangChain Documents into smaller overlapping chunks
suitable for embedding and retrieval.

Uses RecursiveCharacterTextSplitter which tries to split on:
  paragraph → sentence → word → character  (in that order)
This preserves semantic meaning as much as possible.

Usage:
    from app.rag.chunker import split_documents
    chunks = split_documents(docs)
"""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import RAGConfig


def split_documents(docs: list[Document]) -> list[Document]:
    """
    Split a list of Documents into overlapping chunks.

    Args:
        docs: Raw pages from loader.py

    Returns:
        List of smaller Document chunks ready for embedding
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=RAGConfig.CHUNK_SIZE,
        chunk_overlap=RAGConfig.CHUNK_OVERLAP,
        separators=RAGConfig.SEPARATORS,
        length_function=len,
        add_start_index=True,   # adds char offset to metadata for debugging
    )

    chunks = splitter.split_documents(docs)

    print(
        f"  ✂️  {len(docs)} pages → {len(chunks)} chunks "
        f"(size={RAGConfig.CHUNK_SIZE}, overlap={RAGConfig.CHUNK_OVERLAP})"
    )
    return chunks