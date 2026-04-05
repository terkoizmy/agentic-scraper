import asyncio
import datetime
from datetime import timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger

from api.scrape import _run_pipeline
from db import postgres
from models.schemas import JobStatus, JobTrigger
from pipeline import cleaner
from scrapers import router as scraper_router

_scheduler = AsyncIOScheduler()


async def execute_scheduled_scrape(source_id: str, url: str) -> None:
    """Background task to scrape a URL and track it as a scheduled job."""
    job_id = await postgres.create_job(trigger=JobTrigger.SCHEDULED, source_id=source_id)
    
    try:
        raw = await scraper_router.scrape_with_fallback(url)
        cleaned = cleaner.clean_scrape_result(raw)
        chunks_stored, is_dupe = await _run_pipeline(
            cleaned.url, cleaned.markdown, cleaned.title, cleaned.language, source_id=source_id
        )
        
        await postgres.finish_job(
            job_id=job_id, 
            status=JobStatus.DONE, 
            chunks_stored=chunks_stored, 
            dupes_skipped=1 if is_dupe else 0
        )
        await postgres.update_source(source_id, {"last_scraped_at": datetime.datetime.now(timezone.utc)})
        logger.success("Scheduled scrape completed for '{}'", url)
        
    except Exception as exc:
        logger.error("Scheduled scrape failed for '{}': {}", url, exc)
        await postgres.finish_job(job_id, JobStatus.FAILED, 0, 0, error=str(exc))


async def sync_jobs() -> None:
    """Read all active sources and schedule them if not already scheduled."""
    try:
        sources = await postgres.list_sources()
        _scheduler.remove_all_jobs()
        
        count = 0
        for src in sources:
            if src.get("is_active") and src.get("schedule_hours"):
                _scheduler.add_job(
                    execute_scheduled_scrape,
                    IntervalTrigger(hours=src["schedule_hours"]),
                    id=f"scrape_{src['id']}",
                    args=[src["id"], src["url"]],
                    replace_existing=True,
                )
                count += 1
                
        logger.info("Synced {} scheduled jobs from database", count)
    except Exception as exc:
        logger.error("Failed to sync scheduled jobs: {}", exc)


def start_scheduler() -> None:
    """Start the APScheduler async scheduler and sync jobs."""
    _scheduler.start()
    logger.info("APScheduler started")
    asyncio.create_task(sync_jobs())


def stop_scheduler() -> None:
    """Gracefully shut down the scheduler."""
    _scheduler.shutdown(wait=False)
    logger.info("APScheduler stopped")
