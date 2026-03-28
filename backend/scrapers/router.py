from urllib.parse import urlparse

from loguru import logger
from tenacity import RetryError

from core.exceptions import ScraperError
from scrapers.base import BaseScraper, ScrapeResult
from scrapers.docs_scraper import DocsScraper
from scrapers.jina_scraper import JinaScraper
from scrapers.news_scraper import NewsScraper

_DOCS_HOST_PREFIXES = {"docs.", "developer.", "dev.", "wiki.", "api."}
_GITHUB_HOSTNAME = "github.com"


def _is_docs_url(url: str) -> bool:
    """Return True if the URL looks like a documentation or GitHub page."""
    hostname = urlparse(url).hostname or ""
    if hostname == _GITHUB_HOSTNAME:
        return True
    return any(hostname.startswith(prefix) for prefix in _DOCS_HOST_PREFIXES)


def select_scraper(url: str) -> BaseScraper:
    """Choose the optimal primary scraper based on URL structure."""
    if _is_docs_url(url):
        logger.debug("ScraperRouter: {} → DocsScraper", url)
        return DocsScraper()
    logger.debug("ScraperRouter: {} → NewsScraper", url)
    return NewsScraper()


async def scrape_with_fallback(url: str) -> ScrapeResult:
    """Scrape a URL using the best-fit scraper, falling back to JinaScraper on failure.

    Strategy:
        1. Select primary scraper by URL heuristic.
        2. On ScraperError, retry with JinaScraper.
        3. Raise ScraperError if both fail.

    Args:
        url: The target URL to scrape.
    """
    primary = select_scraper(url)
    try:
        return await primary.scrape(url)
    except (ScraperError, RetryError) as primary_error:
        logger.warning("Primary scraper failed for '{}': {}. Falling back to Jina.", url, primary_error)

    try:
        return await JinaScraper().scrape(url)
    except (ScraperError, RetryError) as fallback_error:
        raise ScraperError(
            f"All scrapers failed for '{url}'. Last error: {fallback_error}"
        ) from fallback_error
