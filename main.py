import os
from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.tools import tool
from agno.storage.sqlite import SqliteStorage
from agno.vectordb.lancedb import LanceDb
from agno.document.base import Document
from agno.knowledge.document import DocumentKnowledgeBase
from agno.embedder.openai import OpenAIEmbedder


# Create a storage backend using the Sqlite database
storage = SqliteStorage(
    # store sessions in the ai.sessions table
    table_name="agent_sessions",
    # db_file: Sqlite database file
    db_file="data/dev/sessions.db",
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

vector_db = LanceDb(
    table_name="recipes",
    uri="data/dev/lancedb",  # You can change this path to store data elsewhere
    embedder=OpenAIEmbedder(
        id='BAAI/bge-m3',
        dimensions=1024,
        api_key=os.getenv('SILICONFLOW_API_KEY'),
        base_url='https://api.siliconflow.cn/v1',
    )
)
# Create a knowledge base with the loaded documents
knowledge_base = DocumentKnowledgeBase(
    documents=documents,
    vector_db=vector_db,
)
# Load the knowledge base
knowledge_base.load(recreate=False)

load_dotenv()

@tool(show_result=True, stop_after_tool_call=True)
def add_number(a: int, b:int) -> int:
    """Calculate sum of two numbers"""
    return a+b

def main():
    agent = Agent(
        model=LiteLLM(
            id='volcengine/deepseek-v3-250324',
            name='DeepSeek V3',
        ),
        tools=[add_number],
        markdown=True,
        storage=storage,
        knowledge=knowledge_base,
        # add_references=True,
    )
    agent.print_response('Ask me about something from the knowledge base about Earth', stream=True)


if __name__ == "__main__":
    main()
