from fastapi import APIRouter, status
from typing import List, Dict, Any

router = APIRouter(tags=['Documents'])

router.post('/upload', response_model=List[Dict[str, Any]], status_code=status.HTTP_201_CREATED)

