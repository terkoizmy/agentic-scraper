class ScraperError(Exception):
    """Raised when a scraper fails to fetch content from a URL."""


class DuplicateContentError(Exception):
    """Raised when content is a near-duplicate of existing stored content."""


class EmbeddingError(Exception):
    """Raised when generating embeddings via Ollama fails."""


class VectorStoreError(Exception):
    """Raised when an operation on the vector store (ChromaDB/Qdrant) fails."""


class DatabaseError(Exception):
    """Raised when a PostgreSQL database operation fails."""

class AgentError(Exception):
    """Raised when the LLM orchestrator loop encounters a critical error."""
