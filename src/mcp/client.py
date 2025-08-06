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

async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            #Setting up the storage
            store = InMemoryStore(
            index={
                "dims": 1536,
                "embed": "openai:text-embedding-3-small",
                }
            ) 

            # Get tools
            tools = await load_mcp_tools(session)
            tools.append(create_manage_memory_tool(namespace=("memories",), store=store))
            tools.append(create_search_memory_tool(namespace=("memories",), store=store))
            

            # Create and run the chat loop
            global agent
            agent = create_react_agent("openai:gpt-4.1", tools, store=store)

            demo= gr.ChatInterface(chat,
                                   type= 'messages',
                                   title= 'RAG MCP Test chat',
                                   description= 'Upload files (not yet implemented) and ask questions regarding those files',
                                #    textbox=gr.MultimodalTextbox(file_types=[".pdf", ".txt"]),
                                #    multimodal=True
                                   )
            
            demo.launch()
            # await chat_loop(agent)
            logger.info("Exiting the program...")

            #agent_response = await agent.ainvoke({"messages": "Which pdf documents will be expiriing in 2026?"})

            #print("Agent response:", agent_response['messages'][-1].content)

async def chat_loop(agent):
    while(True):
        human_message= input("Human:")
        if human_message.lower() == "quit":
            break
        agent_response = await agent.ainvoke({
            "messages": [
                {"role": "system", "content": "You are an AI assistant that can remember all conversation in memory. Store every message in memory"},
                {"role": "user", "content": human_message}]
        })
        print("Agent response:", agent_response['messages'][-1].content)

async def chat(message, history):
    # System prompt
    messages = [{"role": "system", "content": "You are an AI assistant that can remember all conversation in memory. Store every message in memory"}]

    # for user_msg, bot_msg in history: # Populating messages list with history
    #     messages.append({"role": "user", "content": user_msg}) 
    #     messages.append({"role": "assistant", "content": bot_msg})
    # messages.append({"role": "user", "content": message})

     # history is a list of dicts like {'role': 'user'/'assistant', 'content': '...'}
    messages.extend(history)

    # Add the latest user message
    messages.append({"role": "user", "content": message})
    agent_response = await agent.ainvoke({
            "messages": messages
    })
    return agent_response['messages'][-1].content

if __name__== '__main__':
    asyncio.run(main())