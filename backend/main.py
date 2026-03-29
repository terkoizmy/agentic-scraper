import asyncio
import sys

# Playwright requires ProactorEventLoop on Windows to spawn browser subprocesses.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import agent, jobs, query, scrape, sources
from core.logger import setup_logger
from db import postgres
from scheduler.cron import start_scheduler, stop_scheduler

setup_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown lifecycle for DB pool and scheduler."""
    await postgres.init_pool()
    start_scheduler()
    yield
    stop_scheduler()
    await postgres.close_pool()


app = FastAPI(
    title="Agentic Scraper API",
    description="LLM-orchestrated universal web scraping pipeline",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sources.router, prefix="/api/sources", tags=["Sources"])
app.include_router(scrape.router, prefix="/api/scrape", tags=["Scraping"])
app.include_router(jobs.router, prefix="/api/scrape", tags=["Jobs"])
app.include_router(query.router, prefix="/api", tags=["RAG Query"])
app.include_router(agent.router, prefix="/api/agent", tags=["Agent"])


@app.get("/")
def root():
    return {"status": "ok", "message": "Agentic Scraper API is running"}


if __name__ == "__main__":
    import uvicorn
    # Run programmatically so the ProactorEventLoopPolicy takes precedence.
    # IMPORTANT: reload=False is required on Windows so Uvicorn doesn't spawn
    # a separate worker process that resets the event loop to SelectorEventLoop.
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
