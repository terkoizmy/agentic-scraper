from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    app_env: str = "development"

    # PostgreSQL
    database_url: str = "postgresql://postgres:password@localhost:5432/scraper_db"

    # ChromaDB (dev)
    chroma_host: str = "localhost"
    chroma_port: int = 8001

    # Qdrant (prod)
    qdrant_url: str = ""
    qdrant_api_key: str = ""

    # Ollama (Embedding)
    ollama_base_url: str = "http://localhost:11434"
    ollama_embed_model: str = "bge-m3"
    ollama_api_key: str | None = None

    # Supabase (prod)
    supabase_url: str = ""
    supabase_key: str = ""

    # MiniMax Agent Brain
    minimax_api_key: str = ""
    minimax_group_id: str = ""
    minimax_model: str = "MiniMax-Text-01"
    minimax_base_url: str = "https://api.minimax.chat/v1"
    agent_max_iterations: int = 10
    agent_temperature: float = 0.2

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/scraper.log"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra environment variables

settings = Settings()
