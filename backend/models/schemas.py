import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ── Enums ─────────────────────────────────────────────────────────────────────

class SourceType(str, Enum):
    NEWS = "news"
    DOCS = "docs"
    GITHUB = "github"


class JobTrigger(str, Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    AGENT = "agent"


class JobStatus(str, Enum):
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


# ── Source Schemas ─────────────────────────────────────────────────────────────

class SourceCreate(BaseModel):
    url: str
    name: str
    source_type: SourceType
    schedule_hours: Optional[int] = None


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    source_type: Optional[SourceType] = None
    schedule_hours: Optional[int] = None
    is_active: Optional[bool] = None


class SourceResponse(BaseModel):
    id: uuid.UUID
    url: str
    name: str
    source_type: SourceType
    schedule_hours: Optional[int]
    last_scraped_at: Optional[datetime]
    is_active: bool
    created_at: datetime


# ── Scrape Schemas ─────────────────────────────────────────────────────────────

class FetchRequest(BaseModel):
    url: str


class FetchResponse(BaseModel):
    url: str
    title: Optional[str] = None
    markdown: str
    chunk_count: int
    language: Optional[str] = None


class CrawlRequest(BaseModel):
    base_url: str
    depth: int = Field(default=2, ge=1, le=5)
    max_pages: int = Field(default=50, ge=1, le=200)


class CrawlResponse(BaseModel):
    base_url: str
    pages_crawled: int
    chunks_stored: int
    dupes_skipped: int
    job_id: uuid.UUID


class StoreRequest(BaseModel):
    url: str
    markdown: str
    title: Optional[str] = None


class StoreResponse(BaseModel):
    url: str
    chunks_stored: int
    is_duplicate: bool


# ── Job Schemas ────────────────────────────────────────────────────────────────

class JobResponse(BaseModel):
    id: uuid.UUID
    source_id: Optional[uuid.UUID] = None
    trigger: JobTrigger
    status: JobStatus
    chunks_stored: int
    dupes_skipped: int
    started_at: datetime
    finished_at: Optional[datetime] = None
    error: Optional[str] = None


# ── RAG Query Schemas ──────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    q: str
    top_k: int = Field(default=5, ge=1, le=20)
    source_type: Optional[SourceType] = None
    language: Optional[str] = None


class QueryResult(BaseModel):
    content: str
    score: float
    url: str
    title: Optional[str] = None
    language: Optional[str] = None


class QueryResponse(BaseModel):
    query: str
    results: list[QueryResult]


# ── Agent Schemas ──────────────────────────────────────────────────────────────

class AgentAskRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ToolCallRecord(BaseModel):
    tool: str
    args: dict
    result: dict


class AgentAskResponse(BaseModel):
    answer: str
    tool_calls: list[ToolCallRecord]
    session_id: str


class WebSearchRequest(BaseModel):
    query: str
    max_results: int = Field(default=5, ge=1, le=20)


class WebSearchResponse(BaseModel):
    query: str
    results: list[dict]


class DeepResearchRequest(BaseModel):
    query: str
    complexity: str = "medium"
    deep_crawl: bool = False


class DeepResearchResponse(BaseModel):
    status: str
    confidence: float
    rag_results: list[QueryResult]
    websites_searched: int
    websites_scraped: int
    total_chunks_stored: int
    deep_crawl_results: dict[str, CrawlResponse] = {}
