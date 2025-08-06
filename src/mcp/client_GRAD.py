from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore
from langmem import create_manage_memory_tool, create_search_memory_tool
import asyncio
import gradio as gr
from src.core.config.settings import settings
from src.core.logging.logger import logger

server_params = StdioServerParameters(
    command="python",
    args=["-m", "src.mcp.server"],
)

# Global store to maintain memory across requests
store = InMemoryStore(
    index={
        "dims": 1536,
        "embed": "openai:text-embedding-3-small",
    }
)

async def create_agent_with_tools():
    """Create an agent with MCP tools for each request"""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # Get tools
            tools = await load_mcp_tools(session)
            tools.append(create_manage_memory_tool(namespace=("memories",), store=store))
            tools.append(create_search_memory_tool(namespace=("memories",), store=store))
            
            # Create agent
            agent = create_react_agent("openai:gpt-4o", tools, store=store)
            
            return agent, session

async def chat(message, history):
    """Chat function for Gradio interface"""
    try:
        logger.info(f"Received message: {message}")
        
        # Create agent with tools for this request
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                
                # Get tools
                tools = await load_mcp_tools(session)
                tools.append(create_manage_memory_tool(namespace=("memories",), store=store))
                tools.append(create_search_memory_tool(namespace=("memories",), store=store))
                
                # Create agent
                agent = create_react_agent("openai:gpt-4o", tools, store=store)
                
                # System prompt
                messages = [{"role": "system", "content": "You are an AI assistant that can remember all conversation in memory. Store every message in memory"}]
                
                # Add history
                messages.extend(history)
                
                # Add the latest user message
                messages.append({"role": "user", "content": message})
                
                logger.info("Invoking agent...")
                
                # Get agent response
                agent_response = await agent.ainvoke({
                    "messages": messages
                })
                
                response_content = agent_response['messages'][-1].content
                logger.info(f"Agent response: {response_content}")
                
                return response_content
                
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}"

def main():
    """Main function to set up and run the application"""
    logger.info("Starting RAG MCP Test chat...")
    
    # Create Gradio interface
    demo = gr.ChatInterface(
        chat,
        type='messages',
        title='RAG MCP Test chat',
        description='Upload files (not yet implemented) and ask questions regarding those files',
    )
    
    logger.info("Launching Gradio interface...")
    demo.launch(share=False)

if __name__ == '__main__':
    main()