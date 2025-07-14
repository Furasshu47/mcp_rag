from fastapi import APIRouter, status, Depends, UploadFile, File, HTTPException, Form
from typing import List, Dict, Any
from typing import Annotated, Optional
from pymongo import AsyncMongoClient
from datetime import datetime, date, timedelta

from src.database import database
from src.core.logging.logger import logger

router = APIRouter(tags=['Documents'])

db_dependency= Annotated[AsyncMongoClient, Depends(database.get_db)]

@router.post('/upload', response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def upload_documents(db: db_dependency, document: UploadFile = File(...,  description="The PDF file to be uploaded."), expiry: Optional[str] = Form(None)):
    """
    Receives a PDF file and metadata related to it. Stores the file in AWS/R2 bucket and the metadata in MongoDB.
    """
    logger.info(f"Endpoint '/extract-asbestos-data/': Processing file '{document.filename}'.")
    if not document.filename.endswith(".pdf"):
        logger.warning(f"Endpoint '/extract-asbestos-data/': Invalid file type received: '{document.filename}'.")
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only PDF files are accepted."
        )
    try:
        if expiry:
            expiry_date = date.fromisoformat(expiry)
        else:
            # Default: 1 year from today
            expiry_date = date.today() + timedelta(days=365)

        # Convert date to datetime with time set to 00:00:00
        expiry_dt = datetime.combine(expiry_date, datetime.min.time())

    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD (e.g., 2027-07-30)"}

    return {
        "filename": document.filename,
        "expiry_datetime": expiry_dt.isoformat()
    }

