from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import sources, scrape, jobs, query, agent
from scheduler.cron import start_scheduler
from core.config import settings

app = FastAPI(
    title="Agentic Scraper API",
    description="LLM-orchestrated universal web scraping pipeline",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sources.router, prefix="/api/sources", tags=["Sources"])
app.include_router(scrape.router, prefix="/api/scrape", tags=["Scraping"])
app.include_router(jobs.router, prefix="/api/scrape", tags=["Jobs"])
app.include_router(query.router, prefix="/api", tags=["RAG Query"])
app.include_router(agent.router, prefix="/api/agent", tags=["Agent"])

@app.on_event("startup")
async def startup():
    start_scheduler()

@app.get("/")
def root():
    return {"status": "ok", "message": "Agentic Scraper API is running"}
