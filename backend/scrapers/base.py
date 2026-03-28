from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ScrapeResult:
    url: str
    markdown: str
    title: Optional[str] = None
    language: Optional[str] = None


class BaseScraper(ABC):
    """Abstract base class for all scraper implementations.

    All subclasses must implement the async `scrape` method.
    """

    @abstractmethod
    async def scrape(self, url: str) -> ScrapeResult:
        """Fetch and return clean Markdown content from the given URL.

        Args:
            url: The target URL to scrape.

        Returns:
            A ScrapeResult containing clean Markdown and optional metadata.
        """
