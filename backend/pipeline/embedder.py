import asyncio

from loguru import logger
from ollama import AsyncClient

from core.config import settings
from core.exceptions import EmbeddingError

_client = AsyncClient(host=settings.ollama_base_url)


async def embed_text(text: str) -> list[float]:
    """Generate an embedding vector for a single text using Ollama bge-m3.

    Args:
        text: The text to embed.

    Returns:
        A list of floats representing the embedding vector.

    Raises:
        EmbeddingError: If the Ollama API call fails.
    """
    try:
        response = await _client.embeddings(
            model=settings.ollama_embed_model,
            prompt=text,
        )
        return response["embedding"]
    except Exception as exc:
        raise EmbeddingError(f"Ollama embedding failed: {exc}") from exc


async def embed_batch(texts: list[str]) -> list[list[float]]:
    """Embed multiple text chunks concurrently via asyncio.gather.

    Args:
        texts: List of text strings to embed.

    Returns:
        List of embedding vectors in the same order as inputs.
    """
    logger.debug("Embedder: embedding {} chunks via {}", len(texts), settings.ollama_embed_model)
    return list(await asyncio.gather(*[embed_text(text) for text in texts]))
