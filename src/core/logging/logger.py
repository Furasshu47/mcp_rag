import os
from loguru import logger
from src.core.config.settings import settings

# Ensure log directory exists
os.makedirs(settings.LOG_DIR, exist_ok=True)

# Remove default handler (console output) if you only want file output initially
logger.remove()

# Add a handler for writing to a file, rotating daily and keeping old logs
logger.add(
    settings.LOG_FILE_PATH,
    rotation="500 MB",  # Rotate log file when it reaches 500 MB
    retention="30 days", # Keep logs for 30 days
    level="INFO",      # Log messages at INFO level and above
    format="{time} {level} {message}", # Basic format
    enqueue=True       # Use a queue to make logging non-blocking (good for performance)
)

# Logging in console
logger.add(
    lambda msg: print(msg, end=""),
    level="INFO",
    format="<green>{time}</green> <level>{level}</level> <bold>{message}</bold>" # Colored console output
)