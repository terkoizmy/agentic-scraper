from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger

_CHUNK_SIZE = 1000
_CHUNK_OVERLAP = 200

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=_CHUNK_SIZE,
    chunk_overlap=_CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def _manual_split(text: str) -> list[str]:
    """Fallback: sliding-window split when LangChain returns empty unexpectedly."""
    stride = _CHUNK_SIZE - _CHUNK_OVERLAP
    return [
        text[i : i + _CHUNK_SIZE]
        for i in range(0, len(text), stride)
        if text[i : i + _CHUNK_SIZE].strip()
    ]


def split_into_chunks(text: str) -> list[str]:
    """Split a document into overlapping chunks for embedding and retrieval.

    Uses semantic separators (paragraph → sentence → word) to keep
    chunks meaningful rather than cutting mid-sentence.

    Args:
        text: Full document text to split.

    Returns:
        List of text chunks, each ≤ _CHUNK_SIZE characters.
    """
    if not text.strip():
        logger.warning("Chunker: received empty text, skipping")
        return []

    chunks = _splitter.split_text(text)

    if not chunks:
        logger.warning("Chunker: LangChain returned [] for {} chars, using manual fallback", len(text))
        chunks = _manual_split(text)

    logger.debug("Chunker: {} chunks produced from {} chars", len(chunks), len(text))
    return chunks
