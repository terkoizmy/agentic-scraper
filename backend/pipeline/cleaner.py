import re
from typing import Optional

from langdetect import detect, LangDetectException
from loguru import logger

from scrapers.base import ScrapeResult


def _detect_language(text: str) -> Optional[str]:
    """Detect the language of a text. Returns None if detection fails."""
    try:
        return detect(text[:2000])
    except LangDetectException:
        return None


def _normalize_whitespace(text: str) -> str:
    """Collapse 3+ consecutive blank lines into 2 and strip outer whitespace."""
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _remove_noise_patterns(text: str) -> str:
    """Remove common web noise like repeated separator lines and heavy markdown links."""
    # Remove separator lines
    text = re.sub(r"^[-=*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    
    # Remove heavy image wrappers e.g., [![Image...](...)](...)
    text = re.sub(r"\[!\[.*?\]\(.*?\)\]\(.*?\)", "", text)
    # Remove standalone images e.g., ![Image...](...)
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    
    # Simplify heavily-nested links in navbars
    # Convert [Text](url) to just Text IF it's in a dense list (basic heuristic)
    text = re.sub(r"^\s*[\*\-]\s*\[([^\]]+)\]\([^\)]+\)\s*$", r"* \1", text, flags=re.MULTILINE)
    
    return text


def clean_scrape_result(result: ScrapeResult) -> ScrapeResult:
    """Normalize and language-detect a raw ScrapeResult.

    Returns a new ScrapeResult with cleaned markdown and detected language.
    Does not mutate the original.

    Args:
        result: Raw ScrapeResult from any scraper.
    """
    cleaned = _remove_noise_patterns(result.markdown)
    cleaned = _normalize_whitespace(cleaned)

    language = _detect_language(cleaned)
    if language:
        logger.debug("Cleaner: language='{}' for {}", language, result.url)

    return ScrapeResult(
        url=result.url,
        markdown=cleaned,
        title=result.title,
        language=language,
    )
