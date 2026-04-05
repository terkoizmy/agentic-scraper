# Roadmap

## Phase 1 — Core Infrastructure ✅

- [x] FastAPI backend dengan pipeline lengkap
- [x] Playwright + Jina.ai dual-scraper
- [x] ChromaDB vector storage
- [x] PostgreSQL job & document tracking
- [x] DeduplicationEngine (exact + near-duplicate)

---

## Phase 2 — Agent Intelligence ✅

- [x] MiniMax M2.7 ReAct agent loop
- [x] Tool: `rag_query`, `scrape_page`, `crawl_docs`, `store_content`
- [x] Tool: `web_search` via DuckDuckGo
- [x] Dynamic system prompt dengan tanggal real-time
- [x] Prioritas: RAG → Web Search → Scrape → Jawab
- [x] **RAG-First Enforcement**: `scrape_page` auto-redirects ke `web_search` jika belum ada `rag_query` di session
- [x] **AI Thinking Mode**: Toggle on/off via API + FE, small token budget (~1K)

---

## Phase 3 — Frontend & UX ✅

- [x] React + Vite frontend
- [x] Dashboard analytics real-time
- [x] Chat UI dengan Markdown rendering
- [x] Tool Call Trace visualization
- [x] Persistent session via localStorage
- [x] **LaTeX Math Rendering**: KaTeX support untuk rumus matematika
- [x] **Agent Settings Toggle**: AI Thinking toggle di Agent Console UI

---

## Phase 4 — Specialist Agents 🔮

### ✅ RAG-First Scraping Enforcement (Done)
- [x] Auto-redirect `scrape_page` → `web_search` jika belum ada `rag_query` di session
- [x] Session tracking untuk tool calls
- [x] Helper functions di `agent/memory.py`: `track_tool_call`, `has_rag_query_in_session`

### ✅ AI Thinking Mode (Done)
- [x] Toggle on/off via Agent Console UI
- [x] Hybrid config: env var (default) + runtime API override
- [x] Small token budget (~1024 tokens)
- [x] Settings state management di `core/settings_state.py`

---

### 📝 Code Writer Specialist (Planned)
Agen khusus yang dapat:
- Generate, refactor, dan debug kode dalam berbagai bahasa
- Membaca konteks dari scraping dokumentasi library resmi terlebih dahulu
- Output dengan code block yang bisa langsung di-copy
- Integrasi dengan tool `store_content` untuk menyimpan snippet kode ke memori

---

### 🐙 GitHub Repository Scraper (Planned)
Kemampuan baru bagi agent untuk:
- Membaca dan menganalisis seluruh struktur repository GitHub
- Mengekstrak konten file kode (`.py`, `.ts`, `.go`, dll.) langsung dari GitHub API
- Indexing kode sumber ke Vector DB agar mudah di-query dengan pertanyaan natural language
- Pemahaman konteks proyek dari `README`, `CONTRIBUTING`, dan docstring

---

### 🌐 Memory Sharing Across Models & Users (Planned)
Fitur kolaborasi knowledge base:
- Ekspor/Impor knowledge dari ChromaDB ke format portabel (JSON / Parquet)
- **Multi-user workspace**: setiap user punya namespace Vector DB sendiri
- **Shared knowledge pool**: admin bisa publish knowledge ke shared pool yang bisa diakses semua user
- Integrasi cloud Vector DB (Qdrant / Pinecone) sebagai pengganti ChromaDB lokal
- Model-agnostic: knowledge yang disimpan bisa di-query oleh model LLM manapun
