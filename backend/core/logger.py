import logging
import sys
from loguru import logger
from core.config import settings

class EndpointFilter(logging.Filter):
    """Filter out logs containing specific endpoint paths from uvicorn access logs."""
    def filter(self, record: logging.LogRecord) -> bool:
        # Ignore logs for the agent status polling endpoint.
        return "/api/agent/status/" not in record.getMessage()

def setup_logger():
    """Configure loguru to output to stdout and file, and filter specific uvicorn access logs."""
    logger.remove()

    # Apply filter to uvicorn access logger to silence polling logs.
    logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

    # Console handler (colorized)
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
        colorize=True,
    )

    # File handler (rotation)
    logger.add(
        settings.log_file,
        level=settings.log_level,
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} - {message}",
    )

    return logger


