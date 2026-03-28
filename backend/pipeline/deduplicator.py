import hashlib

from datasketch import MinHash, MinHashLSH
from loguru import logger

_NUM_PERMUTATIONS = 128
_SIMILARITY_THRESHOLD = 0.8

# In-memory LSH index for near-duplicate detection.
# Acceptable for development; would need persistence (e.g. Redis) in production.
_lsh: MinHashLSH = MinHashLSH(threshold=_SIMILARITY_THRESHOLD, num_perm=_NUM_PERMUTATIONS)


def compute_content_hash(text: str) -> str:
    """Return a SHA-256 hex digest of the text for exact deduplication in PostgreSQL."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _build_minhash(text: str) -> MinHash:
    """Build a MinHash from lowercased word tokens for near-duplicate detection."""
    minhash = MinHash(num_perm=_NUM_PERMUTATIONS)
    for word in text.lower().split():
        minhash.update(word.encode("utf-8"))
    return minhash


def is_near_duplicate(text: str, doc_id: str) -> bool:
    """Check if text is a near-duplicate of any previously indexed content.

    Also registers the text in the LSH index if it is NOT a duplicate,
    so future documents can match against it.

    Args:
        text: Document text to check.
        doc_id: Unique key for this document (e.g. URL string).

    Returns:
        True if a near-duplicate is found, False otherwise.
    """
    minhash = _build_minhash(text)
    matches = _lsh.query(minhash)

    if matches:
        logger.warning("Deduplicator: near-duplicate of '{}' skipped (matches: {})", doc_id, matches)
        return True

    try:
        _lsh.insert(doc_id, minhash)
    except ValueError:
        # Key already in LSH — not a new duplicate, just already registered
        pass

    return False
