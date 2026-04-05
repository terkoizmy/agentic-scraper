import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from loguru import logger

from core.exceptions import EmbeddingError, ScraperError, VectorStoreError
from db import postgres, vector
from models.schemas import (
    CrawlRequest,
    CrawlResponse,
    FetchRequest,
    FetchResponse,
    JobStatus,
    JobTrigger,
    StoreRequest,
    StoreResponse,
)
from pipeline import chunker, cleaner, deduplicator, embedder
from scrapers import router as scraper_router
from scrapers.docs_scraper import DocsScraper

router = APIRouter()


async def _run_pipeline(
    url: str,
    markdown: str,
    title: Optional[str],
    language: Optional[str],
    source_id: Optional[uuid.UUID] = None,
) -> tuple[int, bool]:
    """Execute the full dedup → chunk → embed → store pipeline on clean Markdown.

    Returns:
        (chunks_stored, is_duplicate) tuple.
    """
    logger.debug("Pipeline [1/5] hash check for '{}'", url)
    content_hash = deduplicator.compute_content_hash(markdown)

    if await postgres.document_hash_exists(content_hash):
        logger.warning("Pipeline: exact duplicate skipped for '{}'", url)
        return 0, True

    logger.debug("Pipeline [2/5] near-dup check for '{}'", url)
    if deduplicator.is_near_duplicate(markdown, url):
        return 0, True

    logger.debug("Pipeline [3/5] chunking {} chars", len(markdown))
    chunks = chunker.split_into_chunks(markdown)
    if not chunks:
        logger.error("Pipeline: chunker returned 0 chunks for '{}' ({} chars)", url, len(markdown))
        return 0, False

    logger.debug("Pipeline [4/5] embedding {} chunks", len(chunks))
    embeddings = await embedder.embed_batch(chunks)
    chunk_ids = [f"{url}::chunk::{i}" for i in range(len(chunks))]
    metadatas = [
        {"url": url, "title": title or "", "language": language or ""}
        for _ in chunks
    ]

    logger.debug("Pipeline [5/5] storing to ChromaDB + PostgreSQL")
    vector.add_chunks(chunk_ids, chunks, embeddings, metadatas)

    await postgres.insert_document(
        url=url,
        content=markdown,
        content_hash=content_hash,
        chunk_count=len(chunks),
        source_id=source_id,
        title=title,
        language=language,
    )

    logger.success("Pipeline: stored {} chunks for '{}'", len(chunks), url)
    return len(chunks), False



@router.post("/fetch", response_model=FetchResponse)
async def fetch_page(body: FetchRequest):
    """Scrape a single URL, process through the full pipeline, and return results."""
    try:
        raw = await scraper_router.scrape_with_fallback(body.url)
    except ScraperError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))

    cleaned = cleaner.clean_scrape_result(raw)

    try:
        chunk_count, _ = await _run_pipeline(
            cleaned.url, cleaned.markdown, cleaned.title, cleaned.language
        )
    except (EmbeddingError, VectorStoreError) as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    return FetchResponse(
        url=cleaned.url,
        title=cleaned.title,
        markdown=cleaned.markdown,
        chunk_count=chunk_count,
        language=cleaned.language,
    )


@router.post("/crawl", response_model=CrawlResponse)
async def crawl_docs(body: CrawlRequest):
    """Crawl a documentation site from base_url and store all discovered pages."""
    job_id = await postgres.create_job(trigger=JobTrigger.MANUAL)
    doc_scraper = DocsScraper(depth=body.depth, max_pages=body.max_pages)

    try:
        raw_pages = await doc_scraper.crawl_all(body.base_url)
    except Exception as exc:
        logger.error("Fatal exception during crawl: {}", exc)
        await postgres.finish_job(job_id, JobStatus.FAILED, 0, 0, error=str(exc))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    total_chunks = 0
    total_dupes = 0

    for raw_page in raw_pages:
        cleaned = cleaner.clean_scrape_result(raw_page)
        try:
            chunks_stored, is_dupe = await _run_pipeline(
                cleaned.url, cleaned.markdown, cleaned.title, cleaned.language
            )
            total_chunks += chunks_stored
            if is_dupe:
                total_dupes += 1
        except (EmbeddingError, VectorStoreError) as exc:
            logger.error("Pipeline failed for '{}': {}", cleaned.url, exc)

    await postgres.finish_job(job_id, JobStatus.DONE, total_chunks, total_dupes)

    return CrawlResponse(
        base_url=body.base_url,
        pages_crawled=len(raw_pages),
        chunks_stored=total_chunks,
        dupes_skipped=total_dupes,
        job_id=job_id,
    )


@router.post("/store", response_model=StoreResponse)
async def store_content(body: StoreRequest):
    """Store raw Markdown directly into the pipeline without re-scraping the URL."""
    try:
        chunks_stored, is_duplicate = await _run_pipeline(body.url, body.markdown, body.title, None)
    except (EmbeddingError, VectorStoreError) as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))

    return StoreResponse(url=body.url, chunks_stored=chunks_stored, is_duplicate=is_duplicate)
