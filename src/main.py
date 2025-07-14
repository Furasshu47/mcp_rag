from fastapi import FastAPI
from contextlib import asynccontextmanager
import gc

from src.core.config.settings import settings
from src.api.router import api_router
from src.database import database
from src.services.object_store import storage

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect_to_mongo()
    await storage.connect_to_storage()
    yield
    if database.db != None:
        await database.close_mongo_connection()
    if storage.s3 != None:
        await storage.close_storage_connection()
    gc.collect()
    

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan
)


# Including API router
app.include_router(api_router, prefix=settings.API_V1_STR)