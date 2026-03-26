# 🚀 Setup Guide — Agentic Scraper

> Setup lengkap dari nol: Git → Docker DB → Folder Structure → Install Dependencies

---

## Checklist Prerequisites

Pastikan sudah terinstall sebelum mulai:

- [ ] Git
- [ ] Docker Desktop (untuk PostgreSQL + ChromaDB)
- [ ] Miniconda / Anaconda (conda env `agentic-scraper` sudah ada ✅)
- [ ] Node.js 18+ & npm (untuk frontend)
- [ ] Ollama (untuk embedding model bge-m3)

---

## Step 1 — Git Remote Setup

```bash
# Di dalam folder agentic-scraper yang sudah ada
git init
git remote add origin https://github.com/terkoizmy/agentic-scraper.git
git add .
git commit -m "chore: initial project structure"
git branch -M main
git push -u origin main
```

---

## Step 2 — Buat Folder Structure

Jalankan script ini di PowerShell dari root folder:

```powershell
# Backend folders
New-Item -ItemType Directory -Force -Path backend/api
New-Item -ItemType Directory -Force -Path backend/agent
New-Item -ItemType Directory -Force -Path backend/scrapers
New-Item -ItemType Directory -Force -Path backend/pipeline
New-Item -ItemType Directory -Force -Path backend/db
New-Item -ItemType Directory -Force -Path backend/scheduler
New-Item -ItemType Directory -Force -Path backend/models
New-Item -ItemType Directory -Force -Path backend/core
New-Item -ItemType Directory -Force -Path backend/logs

# Frontend folders
New-Item -ItemType Directory -Force -Path frontend/app/sources/add
New-Item -ItemType Directory -Force -Path frontend/app/jobs
New-Item -ItemType Directory -Force -Path frontend/app/playground
New-Item -ItemType Directory -Force -Path frontend/app/agent
New-Item -ItemType Directory -Force -Path frontend/components/ui
New-Item -ItemType Directory -Force -Path frontend/components/layout
New-Item -ItemType Directory -Force -Path frontend/components/agent
New-Item -ItemType Directory -Force -Path frontend/lib
New-Item -ItemType Directory -Force -Path frontend/types
```

---

## Step 3 — Setup Docker (PostgreSQL + ChromaDB)

Pastikan Docker Desktop sudah running, lalu:

```bash
# Dari root folder agentic-scraper
docker-compose up -d
```

Cek apakah container berjalan:

```bash
docker ps
```

Expected output:
```
CONTAINER ID   IMAGE                    PORTS
xxxx           postgres:16              0.0.0.0:5432->5432/tcp
xxxx           chromadb/chroma:latest   0.0.0.0:8001->8000/tcp
```

---

## Step 4 — Setup Backend

```bash
# Aktifkan conda env
conda activate agentic-scraper

# Masuk ke folder backend
cd backend

# Install semua dependencies
pip install -r ../requirements.txt

# Install Playwright chromium (untuk Crawl4AI)
playwright install chromium

# Buat file .env dari template
copy .env.example .env
```

Lalu edit `backend/.env` dan isi:
- `MINIMAX_API_KEY` → dari dashboard MiniMax
- `MINIMAX_GROUP_ID` → dari dashboard MiniMax

---

## Step 5 — Pull Embedding Model (Ollama)

```bash
# Install Ollama dulu jika belum: https://ollama.com
ollama pull bge-m3
```

---

## Step 6 — Jalankan Backend

```bash
# Dari folder backend (conda agentic-scraper aktif)
uvicorn main:app --reload --port 8000
```

Test di browser: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Step 7 — Setup Frontend

```bash
cd frontend
npm install
copy .env.local.example .env.local
npm run dev
```

Open: [http://localhost:3000](http://localhost:3000)

---

## Status Checklist

| Step | Status |
|---|---|
| Git remote setup | ⬜ |
| Folder structure created | ⬜ |
| Docker DB running | ⬜ |
| Backend dependencies installed | ⬜ |
| Playwright chromium installed | ⬜ |
| `.env` configured | ⬜ |
| bge-m3 model pulled | ⬜ |
| Backend running | ⬜ |
| Frontend running | ⬜ |
