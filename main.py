import asyncio
import nest_asyncio

from agno.agent import Agent
from agno.tools import tool
from agno.storage.sqlite import SqliteStorage
from agno.vectordb.lancedb import LanceDb
from agno.document.base import Document
from agno.knowledge.document import DocumentKnowledgeBase
from agno.embedder.openai import OpenAIEmbedder
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
from agno.tools.mcp import MCPTools

from alice.model.llm import ds_chat_model, ds_reasoning_model
from alice.db import sqlite_db_path, lance_db
# from alice.data_source.agno_doc import agno_kb
from alice.tool.crawl4ai import crawl4ai_server_url

# Create a storage backend using the Sqlite database
storage = SqliteStorage(
    # store sessions in the ai.sessions table
    table_name="agent_sessions",
    # db_file: Sqlite database file
    db_file=sqlite_db_path,
)

fun_facts = """
- Earth is the third planet from the Sun and the only known astronomical object to support life.
- Approximately 71% of Earth's surface is covered by water, with the Pacific Ocean being the largest.
- The Earth's atmosphere is composed mainly of nitrogen (78%) and oxygen (21%), with traces of other gases.
- Earth rotates on its axis once every 24 hours, leading to the cycle of day and night.
- The planet has one natural satellite, the Moon, which influences tides and stabilizes Earth's axial tilt.
- Earth's tectonic plates are constantly shifting, leading to geological activities like earthquakes and volcanic eruptions.
- The highest point on Earth is Mount Everest, standing at 8,848 meters (29,029 feet) above sea level.
- The deepest part of the ocean is the Mariana Trench, reaching depths of over 11,000 meters (36,000 feet).
- Earth has a diverse range of ecosystems, from rainforests and deserts to coral reefs and tundras.
- The planet's magnetic field protects life by deflecting harmful solar radiation and cosmic rays.
"""

# Load documents from the data/docs directory
documents = [Document(content=fun_facts)]

vector_db = lance_db
# Create a knowledge base with the loaded documents
# knowledge_base = DocumentKnowledgeBase(
#     documents=documents,
#     vector_db=vector_db,
# )
# Load the knowledge base
# knowledge_base.load(recreate=False)

# Initialize memory.v2
memory = Memory(
    # Use any model for creating memories
    model=ds_chat_model,
    db=SqliteMemoryDb(table_name="user_memories", db_file=sqlite_db_path),
)


@tool(show_result=True, stop_after_tool_call=True)
def add_number(a: int, b:int) -> int:
    """Calculate sum of two numbers"""
    return a+b

async def main():
    async with MCPTools(
        url=crawl4ai_server_url,
        transport="streamable-http",
        timeout_seconds=30,
    ) as mcp_tools:
        agent = Agent(
            model=ds_reasoning_model,
            tools=[mcp_tools],
            markdown=True,
            storage=storage,
            # knowledge=agno_kb,
            # knowledge=knowledge_base,
            # add_references=True,
            # Store memories in a database
            memory=memory,
            # Give the Agent the ability to update memories
            enable_agentic_memory=True,
            # OR - Run the MemoryManager after each response
            enable_user_memories=True,
            # Add the chat history to the messages
            add_history_to_messages=True,
            # Number of history runs
            num_history_runs=3,
        )
        # User ID for the memory
        user_id = "gkzhb@example.com"
        # agent.print_response(
        #     'I am gkzhb, a frontend engineer. I like programming and playing games.',
        #     stream=True,
        #     user_id=user_id,
        # )
        await agent.aprint_response(
            '抓取网页 https://docs.agno.com/tools/mcp/transports/streamable_http 并总结网页内容',
            stream=True,
            user_id=user_id,
        )
        # memories = memory.get_user_memories(user_id=user_id)
        # print(f"Memories about me: {len(memories)}")
        # print(memories[1])


if __name__ == "__main__":
    asyncio.run(main())
