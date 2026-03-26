# 🕷️ Universal Agentic Scraping Pipeline

> **"Give an LLM the ability to scrape, learn, and answer — all in one call."**

A universal web scraping pipeline that is **orchestrated by an LLM (MiniMax M2.7)**.
The LLM hits the backend API to scrape any website, clean and store the content,
then query it semantically — all within a single ReAct reasoning loop.

---

## 📌 Project Overview

### Problem
LLMs need up-to-date, domain-specific data — but raw web content is noisy, unstructured,
and hard to consume. Existing solutions like MCP are limited in coverage and slow to update.
Worse, LLMs can't decide on their own *when* to fetch new data or *what's* relevant.

### Solution
An **agentic, self-serve pipeline** where:
1. An LLM (MiniMax M2.7) receives a user query
2. It reasons: "Do I need to scrape? Is data already in DB?"
3. It calls tools: `scrape_page`, `crawl_docs`, `rag_query`, `store_content`
4. It synthesizes a final answer from clean, chunked, embedded content

### Key Features
- 🤖 **LLM-Orchestrated** — MiniMax M2.7 drives the pipeline via ReAct loop
- 🌐 **Universal scraper** — supports News/Blog & Docs/GitHub via Crawl4AI
- 🧹 **Intelligent cleaning** — Crawl4AI + MarkItDown (HTML, PDF, DOCX)
- 🔁 **Deduplication** — MinHash LSH prevents storing duplicate content
- 🔍 **3 Scraping Modes** — on-demand fetch, full crawl, RAG query from DB
- 📊 **Dashboard** — monitor jobs, manage sources, test queries
- 🔄 **Dev/Prod DB strategy** — local for dev, cloud for production
- 📝 **Smart logging** — Loguru with colorized output and file rotation
- 🔄 **Auto retry** — Tenacity handles flaky scraping with exponential backoff

---

## 🏗️ System Architecture

### 3 Mode Operasi

```
╔══════════════════════════════════════════════════════════════╗
║                   MODE 1 — Scrape on Demand                 ║
║                                                              ║
║  LLM → POST /api/scrape/fetch { url }                       ║
║      ← { markdown, title, chunks }                          ║
║                                                              ║
║  Kapan: URL baru, belum ada di DB, butuh konten real-time   ║
╚══════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════╗
║                   MODE 2 — Full Crawl                       ║
║                                                              ║
║  LLM → POST /api/scrape/crawl { base_url, depth }           ║
║      ← { pages: [{url, markdown}], total, chunks_stored }   ║
║                                                              ║
║  Kapan: Ingest seluruh dokumentasi (docs.react.dev, dll)    ║
╚══════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════╗
║                   MODE 3 — RAG Query                        ║
║                                                              ║
║  LLM → POST /api/query { q, top_k }                         ║
║      ← { results: [{content, score, url}] }                 ║
║                                                              ║
║  Kapan: Data sudah tersimpan, tinggal cari yang relevan     ║
╚══════════════════════════════════════════════════════════════╝
```

### Full Agentic Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      USER / APP                             │
│   "Jelaskan semua API hooks di React 19"                    │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│            AGENT BRAIN — MiniMax M2.7                       │
│                                                             │
│  ReAct Loop:                                                │
│  [Reason]  → "Apakah React 19 hooks sudah ada di DB?"      │
│  [Act]     → call: rag_query("React 19 hooks")             │
│  [Observe] → "Tidak ada / score rendah → perlu scrape"     │
│  [Reason]  → "Perlu crawl docs.react.dev"                  │
│  [Act]     → call: crawl_docs("https://react.dev", depth=2)│
│  [Observe] → "47 halaman di-scrape, 312 chunks tersimpan"  │
│  [Reason]  → "Sekarang bisa query relevan"                 │
│  [Act]     → call: rag_query("React 19 hooks", top_k=8)   │
│  [Output]  → Synthesize → Final answer untuk user          │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                 SCRAPING AGENT LAYER                        │
│                                                             │
│   ┌──────────────────────┐   ┌────────────────────────┐    │
│   │   News / Blog        │   │   Docs / GitHub        │    │
│   │   Crawl4AI           │   │   Crawl4AI             │    │
│   │   + Jina Reader      │   │   + GitHub API         │    │
│   │   (fallback)         │   │   (fallback)           │    │
│   └──────────┬───────────┘   └──────────┬─────────────┘    │
│              └──────────────┬────────────┘                  │
│                   Tenacity (auto retry + backoff)            │
└────────────────────────────┬────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                  CLEANING PIPELINE                          │
│                                                             │
│  1. Crawl4AI → clean Markdown (HTML content)               │
│  2. MarkItDown → convert PDF / DOCX / other formats        │
│  3. Normalize format (date, author, url)                    │
│  4. Language detection (langdetect)                         │
│  5. Deduplication — MinHash LSH (datasketch)               │
│  6. Chunk text — LangChain RecursiveCharacterTextSplitter   │
└────────────────────────────┬────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                  EMBEDDING LAYER                            │
│            Ollama local — bge-m3 model                      │
│     Multilingual, 567M params, fits 4GB VRAM                │
└────────────────────────────┬────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                   STORAGE LAYER                             │
│                                                             │
│   ┌──────────────────────┐   ┌────────────────────────┐    │
│   │  PostgreSQL           │   │  ChromaDB (dev)        │    │
│   │  Local Docker (dev)  │   │  Qdrant Cloud (prod)   │    │
│   │  Supabase (prod)     │   │                        │    │
│   │  - sources           │   │  - embeddings          │    │
│   │  - documents         │   │  - vector search       │    │
│   │  - scrape_jobs       │   │                        │    │
│   └──────────────────────┘   └────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Folder Structure

### Frontend — Next.js 14

```
frontend/
├── app/
│   ├── layout.tsx                    # Root layout
│   ├── page.tsx                      # Dashboard — overview & stats
│   ├── sources/
│   │   ├── page.tsx                  # List all scraping sources
│   │   └── add/
│   │       └── page.tsx              # Add new source form
│   ├── jobs/
│   │   ├── page.tsx                  # Scraping job history & status
│   │   └── [id]/
│   │       └── page.tsx              # Job detail & logs
│   ├── playground/
│   │   └── page.tsx                  # RAG query test interface
│   └── agent/
│       └── page.tsx                  # ← NEW: Chat with Agent (MiniMax M2.7)
│
├── components/
│   ├── ui/                           # shadcn/ui base components
│   ├── layout/
│   │   ├── sidebar.tsx
│   │   └── header.tsx
│   ├── sources/
│   ├── jobs/
│   ├── playground/
│   ├── dashboard/
│   └── agent/
│       ├── chat-bubble.tsx           # ← NEW: Agent message bubble
│       ├── chat-input.tsx            # ← NEW: User message input
│       └── tool-call-trace.tsx       # ← NEW: Show which tools LLM called
│
├── lib/
│   ├── api.ts
│   └── utils.ts
│
├── types/
│   └── index.ts
│
├── .env.local
├── next.config.ts
├── tailwind.config.ts
└── package.json
```

### Backend — Python FastAPI

```
backend/
├── main.py                           # FastAPI app entry point
│
├── api/
│   ├── __init__.py
│   ├── sources.py                    # CRUD for scraping sources
│   ├── scrape.py                     # Trigger scraping (manual)
│   ├── jobs.py                       # Get job history & status
│   ├── query.py                      # RAG query endpoint
│   └── agent.py                      # ← NEW: POST /api/agent/ask
│
├── agent/                            # ← NEW: LLM Orchestration Layer
│   ├── __init__.py
│   ├── brain.py                      # MiniMax M2.7 client + ReAct loop
│   ├── tools.py                      # Tool implementations (scrape, embed, query)
│   ├── tool_registry.py              # Register & dispatch tools to LLM
│   └── memory.py                     # Short-term conversation memory
│
├── scrapers/
│   ├── __init__.py
│   ├── base.py                       # Abstract BaseScraper class
│   ├── router.py                     # Auto-detect & route to scraper
│   ├── news_scraper.py               # Crawl4AI scraper for news/blog
│   ├── docs_scraper.py               # Crawl4AI scraper for docs/GitHub
│   └── jina_scraper.py               # Jina Reader fallback scraper
│
├── pipeline/
│   ├── __init__.py
│   ├── cleaner.py                    # Crawl4AI + MarkItDown cleaning
│   ├── deduplicator.py               # MinHash LSH (datasketch)
│   ├── chunker.py                    # LangChain RecursiveTextSplitter
│   └── embedder.py                   # Ollama bge-m3 embeddings
│
├── db/
│   ├── __init__.py
│   ├── postgres.py                   # PostgreSQL client (asyncpg)
│   └── vector.py                     # ChromaDB (dev) / Qdrant (prod)
│
├── scheduler/
│   ├── __init__.py
│   └── cron.py                       # APScheduler cron jobs
│
├── models/
│   ├── __init__.py
│   └── schemas.py                    # Pydantic v2 request/response models
│
├── core/
│   ├── __init__.py
│   ├── config.py                     # Settings from .env (pydantic-settings)
│   └── logger.py                     # Loguru setup with file rotation
│
├── logs/                             # Auto-created by Loguru
├── .env
├── requirements.txt
└── docker-compose.yml
```

---

## 🛠️ Tech Stack

### Frontend

| Technology | Version | Purpose |
|---|---|---|
| Next.js | 14 (App Router) | React framework |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 3.x | Utility-first styling |
| shadcn/ui | latest | UI component library |
| Recharts | 2.x | Charts & stats visualization |
| TanStack Query | 5.x | Server state management |
| Axios | 1.x | HTTP client |

### Backend Core

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11 | Runtime (conda: `agentic-scraper`) |
| FastAPI | 0.111+ | Web framework |
| Uvicorn | latest | ASGI server |
| Pydantic | v2 | Data validation & schemas |
| pydantic-settings | 2.x | Config management from .env |

### 🤖 Agent / LLM Layer

| Technology | Version | Purpose |
|---|---|---|
| **MiniMax M2.7** | API (cloud) | Agent Brain — reasoning, tool-calling, answer synthesis |
| **httpx** | 0.27.0 | Async HTTP client to call MiniMax API |
| OpenAI-compatible SDK | latest | MiniMax exposes OpenAI-compatible endpoint |

> **Catatan:** MiniMax M2.7 diakses via API (bukan model lokal). Tidak perlu download file model.
> Konfigurasi via `MINIMAX_API_KEY` + `MINIMAX_GROUP_ID` di `.env`.

### Scraping & Cleaning

| Technology | Version | Why We Use It |
|---|---|---|
| **Crawl4AI** | 0.4.0 | Replaces Playwright + Trafilatura + BS4. Outputs clean LLM-ready Markdown. |
| **MarkItDown** | 0.1.0 | Microsoft library — converts PDF, DOCX, Excel, PowerPoint to Markdown. |
| **Jina Reader** | HTTP API | Zero-install fallback. `GET r.jina.ai/{url}` returns instant clean Markdown. |
| httpx | 0.27.0 | Async HTTP client for Jina Reader & MiniMax API calls |

### Pipeline & RAG

| Technology | Version | Why We Use It |
|---|---|---|
| LangChain | 0.2.0 | Text splitting, RAG utilities |
| langchain-text-splitters | 0.2.0 | RecursiveCharacterTextSplitter for smart chunking |
| langchain-community | 0.2.0 | Community integrations |
| **datasketch** | 1.6.5 | MinHash LSH deduplication |
| **langdetect** | 1.0.9 | Detects content language per document |

### Resilience & Observability

| Technology | Version | Why We Use It |
|---|---|---|
| **tenacity** | 8.3.0 | Auto-retry with exponential backoff |
| **loguru** | 0.7.2 | Colorized, structured logging with file rotation |
| APScheduler | 3.10.4 | In-process cron scheduler |

### Database & Embedding

| Technology | Environment | Purpose |
|---|---|---|
| PostgreSQL 16 (Docker) | Local Dev | Sources, documents, job history |
| Supabase | Production | Managed PostgreSQL cloud |
| ChromaDB | Local Dev | Vector store — zero config, file-based |
| **Qdrant Cloud** | Production | Vector store — free tier, high performance |
| **bge-m3 via Ollama** | Both | Multilingual embedding, 567M params, ~2.5GB VRAM |

---

## 💡 Library Highlights

### Crawl4AI — Core Scraper
```python
from crawl4ai import AsyncWebCrawler

async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(url="https://example.com")
    print(result.markdown)  # Clean, LLM-ready Markdown
```

### MarkItDown — Multi-format Converter
```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("document.pdf")
print(result.text_content)  # Clean Markdown output
```

### MiniMax M2.7 — Agent Brain (Tool Calling)
```python
import httpx

async def call_minimax(messages: list, tools: list):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.minimax.chat/v1/text/chatcompletion_v2",
            headers={
                "Authorization": f"Bearer {settings.minimax_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "MiniMax-Text-01",  # atau M2.7 alias
                "messages": messages,
                "tools": tools,             # Tool definitions
                "tool_choice": "auto"
            }
        )
    return response.json()
```

### datasketch — Content Deduplication
```python
from datasketch import MinHash, MinHashLSH

lsh = MinHashLSH(threshold=0.8, num_perm=128)
# Artikel mirip dari URL berbeda → otomatis di-skip
```

### tenacity — Auto Retry
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
async def scrape_with_retry(url: str):
    return await crawler.arun(url)
```

### loguru — Smart Logging
```python
from loguru import logger

logger.info("Scraping {url}", url=url)
logger.success("Stored {n} chunks", n=chunk_count)
logger.warning("Duplicate skipped: {url}", url=url)
logger.error("Failed: {err}", err=str(e))
```

---

## 🔄 Scraper Fallback Strategy

```
URL diterima
     ↓
Crawl4AI (primary)
     ↓ gagal / timeout?
Jina Reader (fallback)
     ↓ gagal?
Tenacity retry (max 3x, exponential backoff)
     ↓ masih gagal?
Log error via Loguru → job status = 'failed'
     ↓
Tampilkan di Dashboard UI
```

---

## 🤖 Agent Tool Definitions

Tools yang bisa dipanggil MiniMax M2.7 via function calling:

```python
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "scrape_page",
            "description": "Scrape satu halaman URL dan kembalikan konten bersih dalam format Markdown",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL halaman yang ingin di-scrape"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "crawl_docs",
            "description": "Crawl semua halaman dari sebuah dokumentasi atau website, lalu simpan ke database",
            "parameters": {
                "type": "object",
                "properties": {
                    "base_url": {"type": "string", "description": "URL awal/base dokumentasi"},
                    "depth":    {"type": "integer", "description": "Kedalaman crawling (default: 2)"},
                    "max_pages":{"type": "integer", "description": "Maksimum halaman yang di-crawl (default: 50)"}
                },
                "required": ["base_url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rag_query",
            "description": "Cari konten yang relevan di database menggunakan semantic search",
            "parameters": {
                "type": "object",
                "properties": {
                    "query":  {"type": "string",  "description": "Query pencarian natural language"},
                    "top_k":  {"type": "integer", "description": "Jumlah hasil yang dikembalikan (default: 5)"},
                    "language": {"type": "string","description": "Filter bahasa: 'id' atau 'en' (opsional)"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "store_content",
            "description": "Simpan konten Markdown ke database (embed + store ke vector DB)",
            "parameters": {
                "type": "object",
                "properties": {
                    "url":      {"type": "string", "description": "URL sumber konten"},
                    "markdown": {"type": "string", "description": "Konten Markdown yang akan disimpan"}
                },
                "required": ["url", "markdown"]
            }
        }
    }
]
```

---

## 🗃️ Database Schema

```sql
-- Sources: websites to monitor
CREATE TABLE sources (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url             TEXT UNIQUE NOT NULL,
    name            TEXT NOT NULL,
    source_type     TEXT NOT NULL CHECK (source_type IN ('news', 'docs', 'github')),
    schedule_hours  INT DEFAULT NULL,
    last_scraped_at TIMESTAMPTZ,
    is_active       BOOLEAN DEFAULT true,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Documents: scraped & cleaned content
CREATE TABLE documents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id       UUID REFERENCES sources(id) ON DELETE CASCADE,
    url             TEXT NOT NULL,
    title           TEXT,
    content         TEXT NOT NULL,
    author          TEXT,
    language        TEXT,
    published_at    TIMESTAMPTZ,
    scraped_at      TIMESTAMPTZ DEFAULT NOW(),
    chunk_count     INT DEFAULT 0,
    content_hash    TEXT,
    metadata        JSONB DEFAULT '{}'
);

-- Scrape Jobs: history & monitoring
CREATE TABLE scrape_jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id       UUID REFERENCES sources(id) ON DELETE CASCADE,
    trigger         TEXT NOT NULL CHECK (trigger IN ('manual', 'scheduled', 'agent')),
    status          TEXT NOT NULL CHECK (status IN ('running', 'done', 'failed')),
    chunks_stored   INT DEFAULT 0,
    dupes_skipped   INT DEFAULT 0,
    started_at      TIMESTAMPTZ DEFAULT NOW(),
    finished_at     TIMESTAMPTZ,
    error           TEXT DEFAULT NULL
);

-- Agent Sessions: conversation & tool call history
CREATE TABLE agent_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      TEXT NOT NULL,
    user_message    TEXT NOT NULL,
    tool_calls      JSONB DEFAULT '[]',   -- [{tool, args, result}]
    final_answer    TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🌐 API Endpoints

```
Sources
GET    /api/sources              List all sources
POST   /api/sources              Add new source
PATCH  /api/sources/:id          Update source config
DELETE /api/sources/:id          Delete source

Scraping (dapat dipanggil langsung atau oleh Agent)
POST   /api/scrape/fetch         Scrape 1 halaman → return Markdown
POST   /api/scrape/crawl         Crawl semua halaman → store ke DB
POST   /api/scrape/store         Simpan Markdown ke DB
GET    /api/scrape/jobs          Get all job history
GET    /api/scrape/jobs/:id      Get specific job detail

RAG Query
POST   /api/query
Body: {
  "q":            "string",     Natural language query
  "top_k":        5,            Number of results (default: 5)
  "source_type":  "docs",       Optional filter by type
  "language":     "id"          Optional filter by language
}

Agent (NEW)
POST   /api/agent/ask
Body: {
  "message":     "Jelaskan semua hooks di React 19",
  "session_id":  "optional-session-uuid"
}
Response: {
  "answer":      "string",
  "tool_calls":  [{tool, args, result}],
  "session_id":  "uuid"
}
```

---

## ⚙️ Environment Variables

### Frontend `.env.local`
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend `.env`
```env
# App
APP_ENV=development

# PostgreSQL (local dev)
DATABASE_URL=postgresql://postgres:password@localhost:5432/scraper_db

# ChromaDB (local dev)
CHROMA_HOST=localhost
CHROMA_PORT=8001

# Qdrant (production)
QDRANT_URL=https://xxx.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key

# Ollama (Embedding)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBED_MODEL=bge-m3

# Supabase (production)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_supabase_key

# ─── MiniMax Agent Brain ───────────────────────────
MINIMAX_API_KEY=your_minimax_api_key
MINIMAX_GROUP_ID=your_minimax_group_id
MINIMAX_MODEL=MiniMax-Text-01
MINIMAX_BASE_URL=https://api.minimax.chat/v1
AGENT_MAX_ITERATIONS=10
AGENT_TEMPERATURE=0.2
# ───────────────────────────────────────────────────

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/scraper.log
```

---

## 🐳 Docker Compose (Local Dev)

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: scraper_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - chroma_data:/chroma/chroma

volumes:
  postgres_data:
  chroma_data:
```

---

## 📦 requirements.txt

```
# Web Framework
fastapi==0.111.0
uvicorn[standard]==0.30.0
pydantic==2.7.0
pydantic-settings==2.3.0

# Scraping
crawl4ai==0.4.0
markitdown==0.1.0
httpx==0.27.0

# Pipeline & RAG
langchain==0.2.0
langchain-text-splitters==0.2.0
langchain-community==0.2.0

# Deduplication & Language
datasketch==1.6.5
langdetect==1.0.9

# Resilience & Logging
tenacity==8.3.0
loguru==0.7.2

# Database
asyncpg==0.29.0
chromadb==0.5.0
qdrant-client==1.9.0

# Embedding
ollama==0.2.0

# Scheduler
apscheduler==3.10.4

# Utils
python-dotenv==1.0.1
openai==1.30.0          # OpenAI-compatible SDK untuk MiniMax API
```

---

## 🚀 Getting Started

```bash
# 1. Clone repo
git clone https://github.com/yourusername/agentic-scraper
cd agentic-scraper

# 2. Create & activate conda environment
conda activate agentic-scraper

# 3. Pull embedding model (Ollama)
ollama pull bge-m3

# 4. Start local databases
docker-compose up -d

# 5. Setup backend
cd backend
pip install -r requirements.txt
playwright install chromium     # required by Crawl4AI
cp .env.example .env
# → Isi MINIMAX_API_KEY dan MINIMAX_GROUP_ID di .env
uvicorn main:app --reload

# 6. Setup frontend
cd ../frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## 📅 Development Roadmap

```
Week 1 — Core Pipeline
  ✅ Project setup & Docker
  ✅ Conda env: agentic-scraper (Python 3.11)
  ✅ Crawl4AI NewsScraper + DocsScraper
  ✅ MarkItDown for non-HTML formats
  ✅ Deduplication with datasketch MinHash
  ✅ Embedder with bge-m3 (Ollama)
  ✅ ChromaDB vector store
  ✅ PostgreSQL schema & queries
  ✅ Loguru logging + tenacity retry
  ✅ Basic FastAPI endpoints (fetch, crawl, store, query)

Week 2 — Agent Layer
  ⬜ MiniMax M2.7 client (brain.py)
  ⬜ Tool definitions & registry (tools.py, tool_registry.py)
  ⬜ ReAct loop implementation
  ⬜ POST /api/agent/ask endpoint
  ⬜ Session memory (memory.py)
  ⬜ agent_sessions DB table

Week 3 — Full Feature & UI
  ⬜ Jina Reader fallback scraper
  ⬜ APScheduler cron jobs
  ⬜ Next.js dashboard UI
  ⬜ Agent chat UI (chat-bubble, tool-call-trace)
  ⬜ Source & job monitoring UI

Week 4 — Polish & Deploy
  ⬜ RAG Playground UI
  ⬜ Switch to Qdrant cloud (prod)
  ⬜ Deploy: Vercel (FE) + Railway (BE)
  ⬜ README + demo GIF
  ⬜ Edge case handling & tests
```

---

## 🧠 Model Reference

### Embedding — bge-m3 (via Ollama)

| Spec | Detail |
|---|---|
| Parameters | 567M |
| Languages | 100+ (including Bahasa Indonesia) |
| VRAM usage | ~2.5GB |
| Install | `ollama pull bge-m3` |

### Agent Brain — MiniMax M2.7

| Spec | Detail |
|---|---|
| Tipe | Cloud API (bukan model lokal) |
| Akses | Via `MINIMAX_API_KEY` + `MINIMAX_GROUP_ID` |
| Endpoint | `https://api.minimax.chat/v1/text/chatcompletion_v2` |
| Kompatibilitas | OpenAI-compatible (tool calling supported) |
| Fungsi | Orchestrate tools, reasoning (ReAct), synthesize answers |

---

## 📊 Penilaian Arsitektur

| Kriteria | Nilai | Catatan |
|---|---|---|
| **Clarity of Purpose** | ⭐⭐⭐⭐⭐ | Tujuan jelas: LLM-orchestrated scraper |
| **Tech Stack Fit** | ⭐⭐⭐⭐⭐ | Semua library dipilih dengan alasan kuat |
| **Agentic Design** | ⭐⭐⭐⭐☆ | ReAct loop solid, bisa dikembangkan ke multi-agent |
| **Scalability** | ⭐⭐⭐⭐☆ | Dev/Prod DB split sudah dipikirkan |
| **Observability** | ⭐⭐⭐⭐⭐ | Loguru + job tracking + agent session log |
| **Developer Experience** | ⭐⭐⭐⭐☆ | Conda env + Docker + .env sudah rapi |
| **Risiko** | ⭐⭐⭐☆☆ | MiniMax API latency bisa jadi bottleneck di ReAct loop |

### Saran Perbaikan
- **Token budget**: Tambahkan batas maksimum token per ReAct iteration untuk menghindari biaya meledak
- **Caching**: Cache hasil `rag_query` yang sama dalam 1 session agar tidak hit vector DB berulang
- **Streaming**: Pertimbangkan streaming response dari `/api/agent/ask` agar UX terasa real-time

---

*Built with ❤️ as a portfolio project for Podifi application — Bandung, 2026*
*Stack: Next.js 14 · FastAPI · Crawl4AI · MarkItDown · MiniMax M2.7 · bge-m3 · ChromaDB · Qdrant · PostgreSQL*
