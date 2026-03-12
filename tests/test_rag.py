"""
Tests — RAG Pipeline
====================
Tests for chunker, loader, and retriever logic.
Uses mocks so no OpenAI API calls are made.
"""

import pytest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document

from app.rag.chunker import split_documents
from app.rag.retriever import format_context, get_source_labels


# ── Chunker tests ─────────────────────────────────────────────────────────────

def make_doc(text: str, page: int = 1) -> Document:
    return Document(page_content=text, metadata={"page": page, "source_file": "test.pdf"})


def test_split_documents_returns_chunks():
    long_text = "This is a sentence about money. " * 50
    docs = [make_doc(long_text)]
    chunks = split_documents(docs)
    assert len(chunks) > 1, "Long document should be split into multiple chunks"


def test_split_documents_preserves_metadata():
    docs = [make_doc("Short text about budgeting.", page=5)]
    chunks = split_documents(docs)
    for chunk in chunks:
        assert chunk.metadata.get("source_file") == "test.pdf"


def test_split_documents_empty_input():
    chunks = split_documents([])
    assert chunks == []


# ── Retriever / formatter tests ───────────────────────────────────────────────

def test_format_context_structure():
    docs = [
        Document(page_content="Assets put money in your pocket.", metadata={"source_file": "rdpd.pdf", "page": 12}),
        Document(page_content="Liabilities take money out.", metadata={"source_file": "rdpd.pdf", "page": 15}),
    ]
    context = format_context(docs)
    assert "Source 1" in context
    assert "Source 2" in context
    assert "page 12" in context
    assert "Assets put money" in context


def test_format_context_empty():
    assert format_context([]) == ""


def test_get_source_labels():
    docs = [
        Document(page_content="...", metadata={"source_file": "rdpd.pdf", "page": 5}),
    ]
    labels = get_source_labels(docs)
    assert labels == ["rdpd.pdf p.5"]