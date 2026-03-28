from crawl4ai import AsyncWebCrawler
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from core.exceptions import ScraperError
from scrapers.base import BaseScraper, ScrapeResult


class NewsScraper(BaseScraper):
    """Scraper for news articles and blog posts.

    Uses Crawl4AI to extract clean LLM-ready Markdown from a single page.
    Retries up to 3 times with exponential backoff on transient failures.
    """

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    async def scrape(self, url: str) -> ScrapeResult:
        """Scrape a single news/blog URL and return clean Markdown.

        Args:
            url: The target article or blog page URL.
        """
        logger.info("NewsScraper: scraping {}", url)
        try:
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(url=url)
        except Exception as exc:
            raise ScraperError(f"Crawl4AI failed for '{url}': {exc}") from exc

        if not result.markdown:
            raise ScraperError(f"No markdown extracted from '{url}'")

        title = result.metadata.get("title") if result.metadata else None
        logger.success("NewsScraper: {} chars extracted from {}", len(result.markdown), url)
        return ScrapeResult(url=url, markdown=result.markdown, title=title)
