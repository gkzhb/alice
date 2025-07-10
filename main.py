from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.litellm import LiteLLM
from agno.tools import tool
from agno.storage.sqlite import SqliteStorage

# Create a storage backend using the Sqlite database
storage = SqliteStorage(
    # store sessions in the ai.sessions table
    table_name="agent_sessions",
    # db_file: Sqlite database file
    db_file="data/dev/sessions.db",
)

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
    )
    agent.print_response('计算 55+24', stream=True)


if __name__ == "__main__":
    main()
