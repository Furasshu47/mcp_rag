from fastapi import APIRouter, status, Depends, UploadFile, File, HTTPException, Form, Query
from typing import List, Dict, Any, Annotated, Optional
from pymongo import AsyncMongoClient
from datetime import datetime, date, timedelta
import tempfile
import os

from src.database import database
from src.core.logging.logger import logger
from src.services.object_store import storage
from src.services.vector_store import vector_store_ops

router = APIRouter(tags=['Documents'])

db_dependency= Annotated[AsyncMongoClient, Depends(database.get_db)]

@router.post('/upload', response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def upload_documents(db: db_dependency, document: UploadFile = File(...,  description="The PDF file to be uploaded."), expiry: Optional[str] = Form(None)):
    """
    Receives a PDF file and metadata related to it. Stores the file in AWS/R2 bucket and the metadata in MongoDB.
    """
    logger.info(f"Endpoint '/upload': Processing file '{document.filename}'.")

    #Check if the file is a PDF
    if not document.filename.endswith(".pdf"):
        logger.warning(f"Endpoint '/extract-asbestos-data/': Invalid file type received: '{document.filename}'.")
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only PDF files are accepted."
        )
    
    #Converting expiry date to timedate object
    try:
        if expiry:
            expiry_date = date.fromisoformat(expiry)
        else:
            # Default: 1 year from today
            expiry_date = date.today() + timedelta(days=365)

        # Convert date to datetime with time set to 00:00:00
        expiry_dt = datetime.combine(expiry_date, datetime.min.time())
    except ValueError:
        logger.error("Invalid date format")
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD (e.g., 2027-07-30)")

    #Converting the pdf bytes to temp pdf file
    pdf_bytes = await document.read()
    temp_pdf_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(pdf_bytes)
            temp_pdf_path = temp_pdf.name

        #Uploading file to object store
        await storage.upload_file(temp_pdf_path, 'mcp_rag/', filename=document.filename)

        metadata= {
            "filename" : document.filename,
            "expiry date": expiry_dt.isoformat()
            }
        
        #Embedding and storing in vector database
        await vector_store_ops.embed_and_store(temp_pdf_path, metadata)
        
        #Uploading metadata to MongoDB
        result = await db["documents_collection"].insert_one(metadata)
        if (result.acknowledged):
            logger.info("Metadata stored successfully")
        else:
            logger.info("Metadata could not be stored")



    except Exception as e:
        logger.error(f"Error during file upload: {e}", exc_info=True)
        return {"errors": str(e)}
    
    finally:
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            try:
                os.remove(temp_pdf_path)
                logger.debug(f"Temporary file deleted: {temp_pdf_path}")
            except OSError as e:
                logger.error(f"Error deleting temporary file {temp_pdf_path}: {e}")


    

    return {
        "filename": document.filename,
        "expiry_datetime": expiry_dt.isoformat()
    }

@router.delete('/delete', status_code=status.HTTP_204_NO_CONTENT)
async def upload_documents(db: db_dependency, filename: Annotated[str | None, Query(min_length=1)]):
    """
    Receives a PDF file name and deleted the entry for that file name.
    """
    logger.info(f"Endpoint '/delete': Deleting file '{filename}'.")
    try:
        #Deleting from object store
        await storage.delete_file(('mcp_rag/'+filename))

        #Deleting from vector store
        await vector_store_ops.delete_by_filename(filename)

        #Deleting metadata from MongoDB
        filter = { "filename" : filename }
        try:
            logger.info("Deleting the file metadata from MongoDB")
            result= await db["documents_collection"].delete_many(filter)
            if (result.acknowledged):
                logger.info("Successfukky deleted instance from MongoDB")
        except Exception as e:
            logger.error(f"Failed to delete file metadata from MongoDB, Error: {e}")

    except Exception as e:
        logger.error(f"Error while trying to delete {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file. Error: {e}")

    logger.info(f"All existing instances of named {filename} have been deleted")

