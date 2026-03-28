import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from core.exceptions import ScraperError
from scrapers.base import BaseScraper, ScrapeResult

_JINA_BASE_URL = "https://r.jina.ai"
_REQUEST_TIMEOUT = 30


class JinaScraper(BaseScraper):
    """Fallback scraper using the Jina Reader public API.

    Zero-config: sends GET r.jina.ai/{url} and receives clean Markdown.
    Used when Crawl4AI fails after all retries.
    """

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    async def scrape(self, url: str) -> ScrapeResult:
        """Fetch a page via Jina Reader and return clean Markdown.

        Args:
            url: The original target URL (NOT the Jina prefixed URL).
        """
        jina_url = f"{_JINA_BASE_URL}/{url}"
        logger.info("JinaScraper: fetching {}", jina_url)

        try:
            async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT) as client:
                response = await client.get(jina_url, headers={"Accept": "text/markdown"})
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ScraperError(
                f"Jina Reader HTTP {exc.response.status_code} for '{url}'"
            ) from exc
        except httpx.RequestError as exc:
            raise ScraperError(f"Jina Reader request error for '{url}': {exc}") from exc

        markdown = response.text.strip()
        if not markdown:
            raise ScraperError(f"Jina Reader returned empty content for '{url}'")

        logger.success("JinaScraper: {} chars fetched from {}", len(markdown), url)
        return ScrapeResult(url=url, markdown=markdown)
