# API Reference

## Agent Endpoints

### `POST /api/agent/ask`
Chat dengan agen AI.

**Request:**
```json
{
  "message": "Explain how async/await works in Python",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "response": "Async/await is a way to handle asynchronous...",
  "session_id": "abc-123",
  "tool_calls": [
    {"tool": "rag_query", "input": {"query": "..."}},
    {"tool": "scrape_page", "input": {"url": "..."}}
  ]
}
```

---

### `POST /api/agent/search`
Test endpoint web search langsung.

**Request:**
```json
{
  "query": "python async await tutorial"
}
```

**Response:**
```json
{
  "results": [
    {"title": "...", "url": "...", "snippet": "..."}
  ]
}
```

---

## Agent Settings

### `GET /api/settings/agent`
Get current thinking settings.

**Response:**
```json
{
  "thinking_enabled": false,
  "max_tokens": 1024
}
```

---

### `PATCH /api/settings/agent`
Update thinking settings (runtime toggle).

**Request:**
```json
{
  "thinking_enabled": true
}
```

---

## Scraping

### `POST /api/scrape/fetch`
Scrape satu halaman URL.

**Request:**
```json
{
  "url": "https://example.com/page"
}
```

**Response:**
```json
{
  "job_id": "job-123",
  "status": "completed",
  "content": "# Markdown content...",
  "title": "Page Title"
}
```

---

### `POST /api/scrape/crawl`
Crawl entire documentation/website.

**Request:**
```json
{
  "url": "https://docs.example.com",
  "max_depth": 2
}
```

---

### `POST /api/scrape/store`
Simpan Markdown langsung ke database.

**Request:**
```json
{
  "url": "https://example.com/article",
  "content": "# Markdown content...",
  "title": "Article Title"
}
```

---

### `GET /api/scrape/jobs`
Daftar scraping jobs terbaru.

---

## RAG Query & Sources

### `POST /api/query`
Semantic search ke Vector DB.

**Request:**
```json
{
  "query": "how does async await work",
  "top_k": 5
}
```

**Response:**
```json
{
  "results": [
    {
      "content": "...",
      "url": "https://...",
      "score": 0.85
    }
  ]
}
```

---

### `GET /api/sources/`
Daftar web sources terdaftar.

### `POST /api/sources/`
Tambah web source baru.

**Request:**
```json
{
  "url": "https://docs.example.com",
  "name": "Example Docs",
  "schedule": "0 */6 * * *"
}
```
