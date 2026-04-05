"""
Backfill titles for existing documents that are missing them.

Priority:
1. Extract from first H1 heading in content
2. Fallback to URL path

Usage:
    python scripts/backfill_titles.py
"""
import asyncio
import re
from urllib.parse import urlparse


async def main():
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from db import postgres, vector
    from pipeline.cleaner import _extract_title_from_url

    await postgres.init_pool()

    documents = await postgres.list_documents_without_title()
    print(f"Found {len(documents)} documents without titles")

    if not documents:
        print("Nothing to backfill")
        return

    def _extract_title_from_content(content: str) -> str | None:
        lines = content.split('\n')
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('# '):
                return stripped[2:].strip()
        return None

    updated = 0
    for doc in documents:
        doc_id = doc["id"]
        url = doc["url"]
        content = doc["content"] or ""

        title = _extract_title_from_content(content)
        if not title:
            title = _extract_title_from_url(url)

        print(f"Updating doc {doc_id}: '{url}' -> '{title}'")

        await postgres.update_document_title(doc_id, title)
        vector.update_chunks_title(url, title)
        updated += 1

    print(f"\nBackfill complete: {updated} documents updated")
    await postgres.close_pool()


if __name__ == "__main__":
    asyncio.run(main())