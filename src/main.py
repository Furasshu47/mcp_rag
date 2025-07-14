from fastapi import FastAPI

from src.core.config.settings import settings
from src.api.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION
)

# Including API router
app.include_router(api_router, prefix=settings.API_V1_STR)