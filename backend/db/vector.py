from typing import Optional

import chromadb
from chromadb import Collection
from chromadb.config import Settings
from loguru import logger

from core.config import settings
from core.exceptions import VectorStoreError

COLLECTION_NAME = "documents"

_client: Optional[chromadb.HttpClient] = None
_collection: Optional[Collection] = None


def _get_client() -> chromadb.HttpClient:
    global _client
    if _client is None:
        _client = chromadb.HttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port,
            settings=Settings(anonymized_telemetry=False),
        )
    return _client


def get_collection() -> Collection:
    """Return the ChromaDB documents collection, creating it if it does not exist."""
    global _collection
    if _collection is None:
        client = _get_client()
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("ChromaDB collection '{}' ready", COLLECTION_NAME)
    return _collection


def add_chunks(
    chunk_ids: list[str],
    chunks: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict],
) -> None:
    """Upsert text chunks with their precomputed embeddings into ChromaDB.

    Args:
        chunk_ids: Unique string IDs for each chunk (e.g. '{url}::chunk::{i}').
        chunks: Raw text content per chunk.
        embeddings: Precomputed embedding vectors (one per chunk).
        metadatas: Metadata dicts with keys like url, title, language.
    """
    if not chunks:
        return
    try:
        collection = get_collection()
        collection.upsert(
            ids=chunk_ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        logger.debug("Stored {} chunks in ChromaDB", len(chunks))
    except Exception as exc:
        raise VectorStoreError(f"Failed to upsert chunks into ChromaDB: {exc}") from exc


def update_chunks_title(url: str, new_title: str) -> int:
    """Update title metadata for all chunks matching the given URL.

    Returns the number of chunks updated.
    """
    try:
        collection = get_collection()
        results = collection.get(where={"url": url}, include=["metadatas"])

        if not results or not results.get("ids"):
            return 0

        chunk_ids = results["ids"]
        old_metadatas = results.get("metadatas", [])

        new_metadatas = []
        for meta in old_metadatas:
            updated = dict(meta)
            updated["title"] = new_title
            new_metadatas.append(updated)

        collection.update(
            ids=chunk_ids,
            metadatas=new_metadatas,
        )
        logger.debug("Updated title to '{}' for {} chunks", new_title, len(chunk_ids))
        return len(chunk_ids)
    except Exception as exc:
        raise VectorStoreError(f"Failed to update chunks title in ChromaDB: {exc}") from exc


def query_similar(
    query_embedding: list[float],
    top_k: int = 5,
    where_filter: Optional[dict] = None,
) -> dict:
    """Perform a semantic similarity search using a precomputed query embedding.

    Args:
        query_embedding: Embedding vector for the query text.
        top_k: Number of top results to return.
        where_filter: Optional ChromaDB metadata filter clause.

    Returns:
        Raw ChromaDB query result dict with keys: documents, distances, metadatas.
    """
    _EMPTY_RESULT = {"documents": [[]], "distances": [[]], "metadatas": [[]]}

    try:
        collection = get_collection()

        # ChromaDB raises if n_results > total items in collection
        total_count = collection.count()
        logger.debug("ChromaDB collection count: {}", total_count)
        if total_count == 0:
            return _EMPTY_RESULT

        actual_top_k = min(top_k, total_count)

        # Only pass `where` if a filter is actually specified — passing where=None
        # in some chromadb versions causes unexpected behavior
        query_kwargs: dict = {
            "query_embeddings": [query_embedding],
            "n_results": actual_top_k,
            "include": ["documents", "distances", "metadatas"],
        }
        if where_filter:
            query_kwargs["where"] = where_filter

        return collection.query(**query_kwargs)

    except Exception as exc:
        raise VectorStoreError(f"ChromaDB similarity query failed: {exc}") from exc

