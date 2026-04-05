# Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React + Vite)               │
│   Dashboard │ Web Sources Manager │ Agent Chat UI        │
└────────────────────────┬────────────────────────────────┘
                         │ REST API
┌────────────────────────▼────────────────────────────────┐
│               BACKEND (FastAPI + Python)                 │
│                                                          │
│  ┌───────────────────────────────────┐                   │
│  │      MiniMax M2.7 ReAct Agent     │                   │
│  │  ┌────────────┬─────────────────┐ │                   │
│  │  │ Tool: RAG  │ Tool: Web Search │ │                   │
│  │  │ Query      │ (DuckDuckGo)    │ │                   │
│  │  ├────────────┼─────────────────┤ │                   │
│  │  │ Tool: Scrape Page            │ │                   │
│  │  │ Tool: Crawl Docs             │ │                   │
│  │  │ Tool: Store Content          │ │                   │
│  │  └──────────────────────────────┘ │                   │
│  └───────────────────────────────────┘                   │
│                                                          │
│  ┌──────────────┐   ┌──────────────────────────────────┐ │
│  │   Scrapers   │   │        Pipeline                  │ │
│  │ - Playwright │   │  Cleaner → Chunker → Embedder    │ │
│  │ - Jina.ai    │   └──────────────────────────────────┘ │
│  └──────────────┘                                        │
└──────────┬─────────────────────────┬────────────────────┘
           │                         │
┌──────────▼──────┐       ┌──────────▼──────┐
│   PostgreSQL    │       │    ChromaDB      │
│  (Jobs, Sources │       │ (Vector Embeddings│
│   Documents)   │       │  Semantic Search) │
└─────────────────┘       └──────────────────┘
```

---

## ReAct Agent Flow

```
1. brain.run_agent()      → Main orchestrator
2. memory.py              → Session state management
3. tool_registry.py       → Tool dispatcher
4. tools.py               → Tool definitions for LLM
```

### Agent Tools

| Tool | Purpose |
|------|---------|
| `rag_query` | Semantic search over stored vector DB content |
| `scrape_page` | Scrape a single URL |
| `crawl_docs` | Crawl documentation site (depth=2) |
| `store_content` | Store raw Markdown to vector DB |
| `web_search` | DuckDuckGo search |
| `deep_research` | Deep thinking pipeline for code-related queries |

---

## Scraping Pipeline

```
URL → Router → Scraper → Cleaner → Dedup → Chunk → Embed → ChromaDB + PostgreSQL
```

### Pipeline Components

| Component | Description |
|---|---|
| `cleaner.py` | Remove HTML, scripts, CSS, navigation noise |
| `chunker.py` | Split text into semantic chunks |
| `embedder.py` | Generate embeddings via MiniMax API |
| `deduplicator.py` | Exact & near-duplicate detection |

---

## Database Schema (PostgreSQL)

- **sources** — Web sources with scheduling
- **documents** — Scraped content with hashes
- **scrape_jobs** — Job tracking (status, chunks, dupes)
- **agent_sessions** — Conversation history for audit

---

## Key Files

| Path | Purpose |
|---|---|
| `backend/agent/brain.py` | ReAct loop - LLM calls, tool execution |
| `backend/agent/memory.py` | Session state, message formatting |
| `backend/agent/tool_registry.py` | Tool name → handler mapping |
| `backend/api/scrape.py` | `/api/scrape/*` endpoints + pipeline |
| `backend/pipeline/` | cleaner, chunker, embedder, deduplicator |
| `backend/db/postgres.py` | PostgreSQL operations |
| `backend/db/vector.py` | ChromaDB operations |
| `frontend/src/pages/` | agent, dashboard, sources pages |
