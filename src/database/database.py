from src.core.config.settings import settings
from pymongo import AsyncMongoClient
from src.core.logging.logger import logger

client: AsyncMongoClient= None
db= None

uri = settings.DATABASE_URI

async def connect_to_mongo():
    global client, db
    try:
        client = AsyncMongoClient(uri)
        db = client["proj1"]
        logger.info("Connected to MongoDB.")
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        raise

async def close_mongo_connection():
    if client:
        await client.close()
        logger.info("Closed MongoDB connection.")

def get_db() -> AsyncMongoClient:
    if db is None:
        raise RuntimeError("Database has not been initialized.")
    return db


