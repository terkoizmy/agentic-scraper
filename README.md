# 🤖 Agentic Scraper

> An intelligent, LLM-orchestrated web scraping and knowledge retrieval system powered by MiniMax M2.7 and a ReAct agent loop.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-blue?logo=react)](https://react.dev/)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-blueviolet)](https://www.trychroma.com/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue?logo=postgresql)](https://www.postgresql.org/)
[![MiniMax](https://img.shields.io/badge/LLM-MiniMax_M2.7-orange)](https://platform.minimax.chat/)

---

## 📖 Overview

**Agentic Scraper** bukan sekadar alat scraping biasa. Ini adalah sistem agen AI yang mampu:

- 🧠 **Berpikir secara mandiri** menggunakan pola ReAct (Reason → Act → Observe)
- 🔍 **Mencari informasi** dari internet secara real-time via DuckDuckGo
- 🕷️ **Merayapi dokumentasi** lengkap sebuah website secara otomatis
- 📚 **Mengingat semuanya** ke dalam Vector Database (ChromaDB) untuk diakses kembali
- 💬 **Menjawab pertanyaan** berdasarkan pengetahuan lokal yang sudah dikumpulkan

Agen AI selalu mengikuti **urutan prioritas yang cerdas**:
1. Cek memory lokal dulu (`rag_query`)
2. Jika kurang → Cari di internet (`web_search`)
3. Baca konten halaman relevan (`scrape_page` / `crawl_docs`)
4. Simpan ke database, lalu jawab si pengguna

---

## 🏗️ Architecture

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

## 🛠️ Tech Stack

### Backend
| Komponen | Teknologi |
|---|---|
| Framework API | FastAPI + Uvicorn |
| LLM Agent | MiniMax M2.7 (Cloud API) |
| Scraper Utama | Playwright (via Crawl4AI) |
| Scraper Fallback | Jina.ai Reader API |
| Vector Database | ChromaDB (lokal) |
| Relational Database | PostgreSQL |
| Embedding Model | MiniMax Text Embedding |
| Web Search | DuckDuckGo (`ddgs`) |
| Task Scheduler | APScheduler |
| Logging | Loguru |
| Retry Logic | Tenacity |

### Frontend
| Komponen | Teknologi |
|---|---|
| Framework | React 19 + Vite |
| Language | TypeScript |
| Styling | Tailwind CSS v4 |
| HTTP Client | Axios |
| Markdown Render | `react-markdown` + `remark-gfm` |
| Math Rendering | KaTeX (`remark-math` + `rehype-katex`) |
| Syntax Highlighting | Prism.js (Tomorrow Dark theme) |
| State Management | React Hooks + localStorage |

---

## ✨ Key Features

### 🧠 Intelligent ReAct Agent
Agen menggunakan pola **Reason → Act → Observe** untuk membuat keputusan multi-langkah. Dengan limit 5 iterasi per sesi, agen mampu menggabungkan beberapa alat secara sinergis untuk menjawab pertanyaan kompleks.

### 🎯 RAG-First Scraping
Agen **selalu memeriksa Vector DB lokal terlebih dahulu** sebelum melakukan scraping. Jika `scrape_page` dipanggil tanpa adanya `rag_query` di session, sistem akan:
1. Auto-redirect ke `web_search` untuk mencari referensi
2. Mengembalikan hasil search untuk direview
3. Baru kemudian mengizinkan `scrape_page`

### 🧮 AI Thinking Mode (Toggleable)
Agen mendukung **reasoning/thinking mode** untukimproved decision-making. Feature ini:
- **Default**: Off (dikontrol via `AGENT_THINKING_ENABLED` env var)
- **Runtime Toggle**: Bisa di-on/off-kan langsung dari Agent Console UI
- **Token Budget**: Small (~1024 tokens default) untuk keep it simple
- **Hybrid Config**: Env var sebagai default, FE toggle untuk runtime override

### 📐 LaTeX Math Rendering
Chat UI mendukung **KaTeX rendering** untuk rumus matematika. Ekspresi seperti:
- Inline: `$E = mc^2$`
- Block: `$$\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}$$`

Akan dirender sebagai formula matematika yang proper, bukan text mentah.

### 🎨 Code Syntax Highlighting
Code blocks memiliki **syntax highlighting warna-warni** menggunakan Prism.js dengan tema Tomorrow Dark - similar to VSCode. Mendukung berbagai bahasa:
- Python, JavaScript, TypeScript
- JSX/TSX, Bash, JSON, SQL, YAML, Markdown

### 🔄 Automatic Knowledge Capture
Setiap halaman yang di-scrape/crawl oleh agen **otomatis tersimpan** ke ChromaDB dan PostgreSQL. Pertanyaan berikutnya tentang topik yang sama akan dijawab dari memori lokal — jauh lebih cepat dan hemat API token.

### 🕸️ Multi-Strategy Scraping
- **Primary**: Playwright (headless browser — mendukung JavaScript-heavy sites)
- **Fallback**: Jina.ai Reader (alternatif cepat jika Playwright gagal)
- **Deduplicator**: Mencegah konten ganda masuk ke database

### 📊 Real-time Dashboard
Dashboard menampilkan statistik langsung: jumlah web sources, total chunks tersimpan, dan riwayat scraping jobs beserta statusnya.

### 💬 Persistent Chat Sessions
Histori percakapan dengan agen disimpan di `localStorage` browser sehingga tidak hilang meski halaman direfresh. Tombol "New Session" tersedia untuk memulai percakapan baru.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL (running instance)
- MiniMax API Key & Group ID

### 1. Clone Repository
```bash
git clone https://github.com/terkoizmy/agentic-scraper.git
cd agentic-scraper
```

### 2. Setup Backend
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Configure environment
cp .env.example .env
# Edit .env and fill in your keys (see Environment Variables section)

# Start backend server
python main.py
```

### 3. Setup Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend akan berjalan di `http://localhost:5173`
Backend API akan berjalan di `http://127.0.0.1:8000`
Swagger Docs tersedia di `http://127.0.0.1:8000/docs`

---

## ⚙️ Environment Variables

Buat file `.env` di dalam folder `backend/` berdasarkan `.env.example`:

```env
# PostgreSQL
POSTGRES_DSN=postgresql://user:password@localhost:5432/agentic_scraper

# MiniMax API (https://platform.minimax.chat/)
MINIMAX_API_KEY=your_api_key_here
MINIMAX_GROUP_ID=your_group_id_here
MINIMAX_BASE_URL=https://ollama.com/v1
MINIMAX_MODEL=minimax-m2.7:cloud

# Agent Configuration
AGENT_MAX_ITERATIONS=5
AGENT_TEMPERATURE=0.3

# Agent Thinking (optional)
AGENT_THINKING_ENABLED=false
AGENT_THINKING_MAX_TOKENS=1024

# Jina.ai (Optional, untuk fallback scraper)
JINA_API_KEY=your_jina_key_here
```

> ⚠️ **Windows Users**: Selalu jalankan backend dengan `python main.py` (BUKAN `uvicorn main:app --reload`). Mode `reload=True` akan merusak Playwright di Windows karena konflik asyncio event loop.

---

## 📁 Project Structure

```
agentic-scraper/
├── backend/
│   ├── agent/
│   │   ├── brain.py          # ReAct loop utama
│   │   ├── memory.py         # Session & system prompt management
│   │   ├── tool_registry.py  # Tool dispatcher & executor
│   │   └── tools.py          # Tool schema definitions (untuk LLM)
│   ├── api/
│   │   ├── agent.py          # /api/agent/ask, /api/agent/search
│   │   ├── query.py          # /api/query (RAG endpoint)
│   │   ├── scrape.py         # /api/scrape/fetch, /crawl, /store
│   │   ├── settings.py       # /api/settings/agent (thinking toggle)
│   │   ├── sources.py        # /api/sources (CRUD)
│   │   └── jobs.py           # /api/scrape/jobs
│   ├── db/
│   │   ├── postgres.py       # PostgreSQL pool & queries
│   │   └── vector.py         # ChromaDB client
│   ├── pipeline/
│   │   ├── cleaner.py        # Markdown noise removal
│   │   ├── chunker.py        # Text splitting
│   │   ├── embedder.py       # Embedding generation
│   │   └── deduplicator.py   # Exact & near-duplicate detection
│   ├── scrapers/
│   │   ├── docs_scraper.py   # Multi-page crawler (Playwright)
│   │   ├── news_scraper.py   # Single-page scraper (Playwright)
│   │   ├── jina_scraper.py   # Jina.ai fallback scraper
│   │   └── router.py         # Fallback routing logic
│   ├── models/
│   │   └── schemas.py        # Pydantic schemas
│   ├── core/
│   │   ├── config.py         # Settings (pydantic-settings)
│   │   ├── exceptions.py     # Domain exceptions
│   │   ├── logger.py         # Loguru setup
│   │   └── settings_state.py # Runtime settings state (thinking toggle)
│   ├── scheduler/
│   │   └── cron.py           # APScheduler setup
│   └── main.py               # FastAPI app entrypoint
│
└── frontend/
    └── src/
        ├── pages/
        │   ├── agent/        # Chat UI + tool trace visualization
        │   ├── dashboard/    # Analytics & job monitoring
        │   └── sources/      # Web sources management
        ├── components/       # Shared UI components
        ├── hooks/            # Custom React hooks (useAgentSettings)
        ├── lib/              # API client (axios)
        └── types/            # TypeScript interfaces
```

---

## 🔌 API Endpoints

### Agent
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/agent/ask` | Chat dengan agen AI |
| `POST` | `/api/agent/search` | Test endpoint web search langsung |

### Agent Settings
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/settings/agent` | Get current thinking settings |
| `PATCH` | `/api/settings/agent` | Update thinking settings (runtime toggle) |

### Scraping
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/scrape/fetch` | Scrape satu halaman URL |
| `POST` | `/api/scrape/crawl` | Crawl seluruh dokumentasi/website |
| `POST` | `/api/scrape/store` | Simpan Markdown langsung ke database |
| `GET` | `/api/scrape/jobs` | Daftar scraping jobs terbaru |

### RAG Query & Sources
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/query` | Semantic search ke Vector DB |
| `GET` | `/api/sources/` | Daftar web sources terdaftar |
| `POST` | `/api/sources/` | Tambah web source baru |

---

## 🗺️ Roadmap & Next Features

### ✅ Phase 1 — Core Infrastructure (Done)
- [x] FastAPI backend dengan pipeline lengkap
- [x] Playwright + Jina.ai dual-scraper
- [x] ChromaDB vector storage
- [x] PostgreSQL job & document tracking
- [x] DeduplicationEngine (exact + near-duplicate)

### ✅ Phase 2 — Agent Intelligence (Done)
- [x] MiniMax M2.7 ReAct agent loop
- [x] Tool: `rag_query`, `scrape_page`, `crawl_docs`, `store_content`
- [x] Tool: `web_search` via DuckDuckGo
- [x] Dynamic system prompt dengan tanggal real-time
- [x] Prioritas: RAG → Web Search → Scrape → Jawab
- [x] **RAG-First Enforcement**: `scrape_page` auto-redirects ke `web_search` jika belum ada `rag_query` di session
- [x] **AI Thinking Mode**: Toggle on/off via API + FE, small token budget (~1K)

### ✅ Phase 3 — Frontend & UX (Done)
- [x] React + Vite frontend
- [x] Dashboard analytics real-time
- [x] Chat UI dengan Markdown rendering
- [x] Tool Call Trace visualization
- [x] Persistent session via localStorage
- [x] **LaTeX Math Rendering**: KaTeX support untuk rumus matematika
- [x] **Agent Settings Toggle**: AI Thinking toggle di Agent Console UI

### 🔮 Phase 4 — Specialist Agents (Planned)

#### ✅ RAG-First Scraping Enforcement (Done)
- [x] Auto-redirect `scrape_page` → `web_search` jika belum ada `rag_query` di session
- [x] Session tracking untuk tool calls
- [x] Helper functions di `agent/memory.py`: `track_tool_call`, `has_rag_query_in_session`

#### ✅ AI Thinking Mode (Done)
- [x] Toggle on/off via Agent Console UI
- [x] Hybrid config: env var (default) + runtime API override
- [x] Small token budget (~1024 tokens)
- [x] Settings state management di `core/settings_state.py`

#### 📝 Code Writer Specialist
Agen khusus yang dapat:
- Generate, refactor, dan debug kode dalam berbagai bahasa
- Membaca konteks dari scraping dokumentasi library resmi terlebih dahulu
- Output dengan code block yang bisa langsung di-copy
- Integrasi dengan tool `store_content` untuk menyimpan snippet kode ke memori

#### 🐙 GitHub Repository Scraper
Kemampuan baru bagi agent untuk:
- Membaca dan menganalisis seluruh struktur repository GitHub
- Mengekstrak konten file kode (`.py`, `.ts`, `.go`, dll.) langsung dari GitHub API
- Indexing kode sumber ke Vector DB agar mudah di-query dengan pertanyaan natural language
- Pemahaman konteks proyek dari `README`, `CONTRIBUTING`, dan docstring

#### 🌐 Memory Sharing Across Models & Users
Fitur kolaborasi knowledge base:
- Ekspor/Impor knowledge dari ChromaDB ke format portabel (JSON / Parquet)
- **Multi-user workspace**: setiap user punya namespace Vector DB sendiri
- **Shared knowledge pool**: admin bisa publish knowledge ke shared pool yang bisa diakses semua user
- Integrasi cloud Vector DB (Qdrant / Pinecone) sebagai pengganti ChromaDB lokal
- Model-agnostic: knowledge yang disimpan bisa di-query oleh model LLM manapun

---

## 🤝 Contributing

Pull requests are welcome! Untuk perubahan besar, silakan buka Issue terlebih dahulu.

Panduan commit message menggunakan [Conventional Commits](https://www.conventionalcommits.org/):
```
feat(agent): add code writer specialist tool
fix(scraper): handle javascript-only pages
docs(readme): update roadmap section
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
