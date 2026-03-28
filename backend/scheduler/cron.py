from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

_scheduler = AsyncIOScheduler()


def start_scheduler() -> None:
    """Start the APScheduler async scheduler.

    Scheduled jobs for periodic scraping will be registered here
    once the source configuration system is complete.
    """
    _scheduler.start()
    logger.info("APScheduler started (no cron jobs registered yet)")


def stop_scheduler() -> None:
    """Gracefully shut down the scheduler."""
    _scheduler.shutdown(wait=False)
    logger.info("APScheduler stopped")
