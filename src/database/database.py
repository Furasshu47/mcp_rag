from src.core.config.settings import settings
from pymongo import AsyncMongoClient
from src.core.logging.logger import logger

uri = settings.DATABASE_URI
try:
    client = AsyncMongoClient(uri)

except Exception as e:
    logger.error(f"Failed to connect to database. Error:{e}")

db= client.proj1
documents_collection= db["documents"]
