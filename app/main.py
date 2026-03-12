"""
Money Coach Max — FastAPI Application
======================================
Entry point for the API server.

Run:
    uvicorn app.main:app --reload --port 8000

Docs:
    http://localhost:8000/docs
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import settings
from app.rag.vector_store import load_index, index_exists
from app.api.chat import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: preload FAISS index into memory."""
    print(f"\n🚀 {settings.app_name} v{settings.app_version} starting up...")

    if index_exists():
        load_index()
    else:
        print(
            "\n⚠️  FAISS index not found — RAG retrieval will fail.\n"
            "   Run ingestion first:\n"
            "   python scripts/ingest_documents.py\n"
        )

    yield
    print(f"👋 {settings.app_name} shutting down.")


app = FastAPI(
    title=f"{settings.app_name} API",
    description="RAG-powered financial coaching assistant",
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", tags=["health"])
def health_check():
    return {
        "status":  "running",
        "service": settings.app_name,
        "version": settings.app_version,
        "docs":    "/docs",
    }