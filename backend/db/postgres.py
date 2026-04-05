import uuid
from typing import Optional

import asyncpg
from asyncpg import Pool
from loguru import logger

from core.config import settings
from core.exceptions import DatabaseError
from models.schemas import JobStatus, JobTrigger, SourceType

_pool: Optional[Pool] = None

_CREATE_TABLES_SQL = """
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS sources (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url             TEXT UNIQUE NOT NULL,
    name            TEXT NOT NULL,
    source_type     TEXT NOT NULL,
    schedule_hours  INT DEFAULT NULL,
    last_scraped_at TIMESTAMPTZ,
    is_active       BOOLEAN DEFAULT true,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS documents (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id    UUID REFERENCES sources(id) ON DELETE CASCADE,
    url          TEXT NOT NULL,
    title        TEXT,
    content      TEXT NOT NULL,
    language     TEXT,
    scraped_at   TIMESTAMPTZ DEFAULT NOW(),
    chunk_count  INT DEFAULT 0,
    content_hash TEXT,
    metadata     JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS scrape_jobs (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id     UUID REFERENCES sources(id) ON DELETE CASCADE,
    trigger       TEXT NOT NULL,
    status        TEXT NOT NULL,
    chunks_stored INT DEFAULT 0,
    dupes_skipped INT DEFAULT 0,
    started_at    TIMESTAMPTZ DEFAULT NOW(),
    finished_at   TIMESTAMPTZ,
    error         TEXT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS agent_sessions (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id   TEXT NOT NULL,
    user_message TEXT NOT NULL,
    tool_calls   JSONB DEFAULT '[]',
    final_answer TEXT,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);
"""


async def init_pool() -> None:
    """Initialize the asyncpg connection pool and ensure all tables exist."""
    global _pool
    _pool = await asyncpg.create_pool(settings.database_url, min_size=2, max_size=10)
    async with _pool.acquire() as conn:
        await conn.execute(_CREATE_TABLES_SQL)
    logger.info("PostgreSQL pool initialized, tables ensured")


async def close_pool() -> None:
    """Gracefully close the connection pool on application shutdown."""
    global _pool
    if _pool is not None:
        await _pool.close()
        logger.info("PostgreSQL pool closed")


async def _get_pool() -> Pool:
    if _pool is None:
        raise DatabaseError("Connection pool not initialized. Call init_pool() first.")
    return _pool


# ── Sources ────────────────────────────────────────────────────────────────────

async def list_sources() -> list[dict]:
    """Return all sources ordered by creation date descending."""
    pool = await _get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM sources ORDER BY created_at DESC")
    return [dict(r) for r in rows]


async def get_source_by_id(source_id: uuid.UUID) -> Optional[dict]:
    """Return a single source by UUID, or None if not found."""
    pool = await _get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM sources WHERE id = $1", source_id)
    return dict(row) if row else None


async def create_source(
    url: str,
    name: str,
    source_type: SourceType,
    schedule_hours: Optional[int] = None,
) -> dict:
    """Insert a new source and return the created record."""
    pool = await _get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO sources (url, name, source_type, schedule_hours)
            VALUES ($1, $2, $3, $4)
            RETURNING *
            """,
            url, name, source_type.value, schedule_hours,
        )
    return dict(row)


async def update_source(source_id: uuid.UUID, fields: dict) -> Optional[dict]:
    """Update specified fields on a source. Only provided (non-None) keys are updated."""
    if not fields:
        return await get_source_by_id(source_id)

    set_clause = ", ".join(f"{key} = ${i + 2}" for i, key in enumerate(fields))
    values = list(fields.values())
    pool = await _get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            f"UPDATE sources SET {set_clause} WHERE id = $1 RETURNING *",
            source_id, *values,
        )
    return dict(row) if row else None


async def delete_source(source_id: uuid.UUID) -> bool:
    """Delete a source by UUID. Returns True if a row was deleted."""
    pool = await _get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM sources WHERE id = $1", source_id)
    return result == "DELETE 1"


# ── Documents ──────────────────────────────────────────────────────────────────

async def document_hash_exists(content_hash: str) -> bool:
    """Return True if a document with this exact content hash is already stored."""
    pool = await _get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id FROM documents WHERE content_hash = $1", content_hash
        )
    return row is not None


async def insert_document(
    url: str,
    content: str,
    content_hash: str,
    chunk_count: int,
    source_id: Optional[uuid.UUID] = None,
    title: Optional[str] = None,
    language: Optional[str] = None,
) -> uuid.UUID:
    """Persist a scraped document record and return its UUID."""
    pool = await _get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO documents
                (source_id, url, title, content, language, chunk_count, content_hash)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id
            """,
            source_id, url, title, content, language, chunk_count, content_hash,
        )
    return row["id"]


async def list_documents_without_title() -> list[dict]:
    """Return all documents where title is NULL or empty."""
    pool = await _get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, url, content FROM documents WHERE title IS NULL OR title = ''"
        )
    return [dict(r) for r in rows]


async def update_document_title(doc_id: uuid.UUID, title: str) -> None:
    """Update the title of a document."""
    pool = await _get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE documents SET title = $1 WHERE id = $2",
            title, doc_id,
        )


# ── Scrape Jobs ────────────────────────────────────────────────────────────────

async def create_job(
    trigger: JobTrigger,
    source_id: Optional[uuid.UUID] = None,
) -> uuid.UUID:
    """Create a new scrape job with 'running' status and return its UUID."""
    pool = await _get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO scrape_jobs (source_id, trigger, status)
            VALUES ($1, $2, $3)
            RETURNING id
            """,
            source_id, trigger.value, JobStatus.RUNNING.value,
        )
    return row["id"]


async def finish_job(
    job_id: uuid.UUID,
    status: JobStatus,
    chunks_stored: int,
    dupes_skipped: int,
    error: Optional[str] = None,
) -> None:
    """Mark a job as done/failed with final statistics."""
    pool = await _get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE scrape_jobs
            SET status = $2, chunks_stored = $3, dupes_skipped = $4,
                error = $5, finished_at = NOW()
            WHERE id = $1
            """,
            job_id, status.value, chunks_stored, dupes_skipped, error,
        )


async def list_jobs() -> list[dict]:
    """Return all scrape jobs ordered by start time descending."""
    pool = await _get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM scrape_jobs ORDER BY started_at DESC")
    return [dict(r) for r in rows]


async def get_job_by_id(job_id: uuid.UUID) -> Optional[dict]:
    """Return a single scrape job by UUID, or None if not found."""
    pool = await _get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM scrape_jobs WHERE id = $1", job_id)
    return dict(row) if row else None


# ── Agent Sessions ─────────────────────────────────────────────────────────────

async def save_agent_session(
    session_id: str,
    user_message: str,
    tool_calls: list[dict],
    final_answer: str,
) -> None:
    """Persist a completed agent session for audit trail and replay."""
    import json
    pool = await _get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO agent_sessions (session_id, user_message, tool_calls, final_answer)
            VALUES ($1, $2, $3, $4)
            """,
            session_id, user_message, json.dumps(tool_calls, default=str), final_answer,
        )

