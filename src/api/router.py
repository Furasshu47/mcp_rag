from fastapi import APIRouter
from src.api.v1.endpoints import documents

api_router = APIRouter()
api_router.include_router(documents.router, prefix='/documents')
