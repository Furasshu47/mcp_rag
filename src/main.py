from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.core.config.settings import settings
from src.api.router import api_router
from src.database import database

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.connect_to_mongo()
    yield
    database.close_mongo_connection()
    

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan
)


# Including API router
app.include_router(api_router, prefix=settings.API_V1_STR)