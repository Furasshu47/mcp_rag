from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from typing import Dict
import asyncio

from src.core.config.settings import settings
from src.core.logging.logger import logger


async def embed_and_store(pdf_path: str, metadata: Dict):
    """
    Accepts a PDF path, converts it to embedding and stores it in a vector database
    Args:
        pdf_path (str) : THe path to the PDF to be processed
        metadata (dict) : Metadata related to teh PDF document
    """
    logger.info(f"Metadata:  {metadata}")
    
    #Loading the PDF
    loader = PyMuPDFLoader(pdf_path)
    data = await asyncio.to_thread(loader.load)
    

    #Splitting the document into text chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    all_splits = await asyncio.to_thread(text_splitter.split_documents, data)

    #Injecting custom metadata
    for doc in all_splits:
        doc.metadata.update(metadata)

    #Declaring the embedding model
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    #Instantiating the vector store
    vector_store = Chroma(
    collection_name="documents_colelction",
    embedding_function=embeddings,
    persist_directory="./document_vector_db",
    )

    #Adding chunks to the vector store
    await vector_store.aadd_documents(all_splits)

    logger.info(f"Successfully added {metadata["filename"]} to vector store")


