from crawl4ai import AsyncWebCrawler
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from core.exceptions import ScraperError
from scrapers.base import BaseScraper, ScrapeResult
from scrapers.crawl_config import NEWS_MARKDOWN_GENERATOR


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
                result = await crawler.arun(
                    url=url,
                    markdown_generator=NEWS_MARKDOWN_GENERATOR,
                )
        except Exception as exc:
            logger.error(
                "NewsScraper: Crawl4AI failed for '{}'. "
                "Exception type: {}, Exception message: {}, Trace: {}",
                url, type(exc).__name__, str(exc), repr(exc)
            )
            raise ScraperError(f"Crawl4AI failed for '{url}': {exc}") from exc

        fit_md = result.markdown.fit_markdown if result.markdown else ""
        if not fit_md:
            logger.warning("NewsScraper: No markdown extracted from '{}'. Result: {}", url, result)
            raise ScraperError(f"No markdown extracted from '{url}'")

        title = result.metadata.get("title") if result.metadata else None
        logger.success("NewsScraper: {} chars extracted from {}", len(fit_md), url)
        return ScrapeResult(url=url, markdown=fit_md, title=title)
