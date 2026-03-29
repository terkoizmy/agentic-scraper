"""Shared Crawl4AI configuration helpers.

Centralises markdown generator and content filter settings so that all
scrapers produce consistently clean output without duplicating config.
"""

from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator


def make_markdown_generator(
    threshold: float = 0.45,
    min_word_threshold: int = 10,
) -> DefaultMarkdownGenerator:
    """Return a DefaultMarkdownGenerator with PruningContentFilter applied.

    PruningContentFilter scores each content block by text density
    (ratio of text to HTML markup). Blocks below *threshold* — typically
    sidebars, navigation menus, and footers — are discarded before the
    markdown is generated, leaving only the substantive article body.

    Args:
        threshold: Density cut-off [0–1]. Blocks below this are pruned.
        min_word_threshold: Blocks with fewer words are always removed.
    """
    content_filter = PruningContentFilter(
        threshold=threshold,
        threshold_type="fixed",
        min_word_threshold=min_word_threshold,
    )
    return DefaultMarkdownGenerator(content_filter=content_filter)


# Ready-to-use generators for common scraping scenarios

# General docs — aggressive pruning to strip heavy navbars
DOCS_MARKDOWN_GENERATOR = make_markdown_generator(threshold=0.45, min_word_threshold=10)

# News / articles — slightly more lenient to keep author bios / pull-quotes
NEWS_MARKDOWN_GENERATOR = make_markdown_generator(threshold=0.40, min_word_threshold=8)
