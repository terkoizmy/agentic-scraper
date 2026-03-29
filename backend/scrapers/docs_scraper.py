from crawl4ai import AsyncWebCrawler
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from core.exceptions import ScraperError
from scrapers.base import BaseScraper, ScrapeResult
from scrapers.crawl_config import DOCS_MARKDOWN_GENERATOR


class DocsScraper(BaseScraper):
    """Scraper for documentation sites and GitHub repositories.

    Supports both single-page scrape and recursive multi-page crawl
    with configurable depth and page limit.
    """

    def __init__(self, depth: int = 2, max_pages: int = 50) -> None:
        self._depth = depth
        self._max_pages = max_pages

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    async def scrape(self, url: str) -> ScrapeResult:
        """Scrape a single documentation page and return clean Markdown.

        Args:
            url: The target docs page URL.
        """
        logger.info("DocsScraper: scraping {}", url)
        try:
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(
                    url=url,
                    markdown_generator=DOCS_MARKDOWN_GENERATOR,
                )
        except Exception as exc:
            raise ScraperError(f"Crawl4AI failed for docs URL '{url}': {exc}") from exc

        fit_md = result.markdown.fit_markdown if result.markdown else ""
        if not fit_md:
            raise ScraperError(f"No markdown extracted from docs URL '{url}'")

        title = result.metadata.get("title") if result.metadata else None
        return ScrapeResult(url=url, markdown=fit_md, title=title)

    async def crawl_all(self, base_url: str) -> list[ScrapeResult]:
        """Recursively crawl all internal pages from a base URL.

        Stops when max_pages is reached or the queue is exhausted.
        Failed individual pages are logged and skipped — not a fatal error.

        Args:
            base_url: Starting URL for the crawl.

        Returns:
            List of ScrapeResults for all successfully scraped pages.
        """
        logger.info(
            "DocsScraper: crawling {} (depth={}, max={})",
            base_url, self._depth, self._max_pages,
        )
        visited: set[str] = set()
        queue: list[tuple[str, int]] = [(base_url, 0)]
        results: list[ScrapeResult] = []

        async with AsyncWebCrawler() as crawler:
            while queue and len(results) < self._max_pages:
                current_url, current_depth = queue.pop(0)

                if current_url in visited:
                    continue
                visited.add(current_url)

                try:
                    result = await crawler.arun(
                        url=current_url,
                        markdown_generator=DOCS_MARKDOWN_GENERATOR,
                    )
                except Exception as exc:
                    logger.warning("DocsScraper: skipping '{}' — {}", current_url, exc)
                    continue

                fit_md = result.markdown.fit_markdown if result.markdown else ""
                if not fit_md:
                    continue

                title = result.metadata.get("title") if result.metadata else None
                results.append(ScrapeResult(url=current_url, markdown=fit_md, title=title))
                logger.debug("DocsScraper: ({}/{}) {}", len(results), self._max_pages, current_url)

                if current_depth < self._depth and result.links:
                    for link in result.links.get("internal", []):
                        link_url = link.get("href", "")
                        if link_url and link_url not in visited:
                            queue.append((link_url, current_depth + 1))

        logger.success("DocsScraper: crawled {} pages from {}", len(results), base_url)
        return results
