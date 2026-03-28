from typing import Optional

from fastapi import APIRouter, HTTPException, status
from loguru import logger

from core.exceptions import EmbeddingError, VectorStoreError
from db import vector
from models.schemas import QueryRequest, QueryResponse, QueryResult, SourceType
from pipeline import embedder

router = APIRouter()


def _build_where_filter(source_type: Optional[SourceType], language: Optional[str]) -> Optional[dict]:
    """Build a ChromaDB metadata filter from optional query parameters.

    Returns None if no filters are specified (no where clause needed).
    """
    conditions: dict = {}
    if source_type:
        conditions["source_type"] = {"$eq": source_type.value}
    if language:
        conditions["language"] = {"$eq": language}
    return conditions if conditions else None


@router.post("/query", response_model=QueryResponse)
async def rag_query(body: QueryRequest):
    """Perform a semantic RAG search over all stored document chunks."""
    try:
        query_embedding = await embedder.embed_text(body.q)
    except EmbeddingError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    where_filter = _build_where_filter(body.source_type, body.language)

    try:
        raw = vector.query_similar(query_embedding, top_k=body.top_k, where_filter=where_filter)
    except VectorStoreError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    documents = raw.get("documents", [[]])[0]
    distances = raw.get("distances", [[]])[0]
    metadatas = raw.get("metadatas", [[]])[0]

    results = [
        QueryResult(
            content=doc,
            score=round(1.0 - dist, 4),  # Convert cosine distance → similarity score
            url=meta.get("url", ""),
            title=meta.get("title") or None,
            language=meta.get("language") or None,
        )
        for doc, dist, meta in zip(documents, distances, metadatas)
    ]

    logger.info("RAG query '{}' → {} results", body.q[:60], len(results))
    return QueryResponse(query=body.q, results=results)
