from mcp.server.fastmcp import FastMCP

from src.services.vector_store.vector_store_ops import vector_store

mcp = FastMCP("RAG")

@mcp.tool()
def retrieve(question: str):
    """
    Accepts a question and retrieves the context for it using RAG from documents uploaded to the vector store
    """
    retrieved_docs = vector_store.similarity_search(question, k=5)
    return f'Context: {retrieved_docs}'


if __name__ == "__main__":
    mcp.run(transport="stdio")