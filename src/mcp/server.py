from mcp.server.fastmcp import FastMCP

from src.services.vector_store.vector_store_ops import vector_store
from src.core.logging.logger import logger

mcp = FastMCP("RAG")

@mcp.tool()
async def retrieve(question: str):
    """
    Accepts a question and retrieves the context for it using RAG from documents uploaded to the vector store
    """
    logger.info("Retrieving documents...")
    retrieved_docs = vector_store.similarity_search(question, k=5)
    logger.info("Retrieved documents, sending context to agent...")
    return f'Context: {retrieved_docs}'

@mcp.tool()
async def dummy_tool():
    """
    Returns a dummy response
    """
    return ("Okay dummy, the tool is working")


if __name__ == "__main__":
    logger.info("Starting MCP Server")
    mcp.run(transport="stdio")