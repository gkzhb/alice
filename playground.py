# import asyncio
from agno.agent import Agent
from agno.team import Team
from agno.playground import Playground
from agno.storage.sqlite import SqliteStorage
# from agno.tools.duckduckgo import DuckDuckGoTools
# from agno.tools.yfinance import YFinanceTools
from alice.model.llm import ds_chat_model, ds_reasoning_model

agent_storage: str = "data/dev/playground-agents.db"

web_agent = Agent(
    name="Web Agent",
    model=ds_chat_model,
    tools=[],
    instructions=["Always include sources"],
    # Store the agent sessions in a sqlite database
    storage=SqliteStorage(table_name="web_agent", db_file=agent_storage),
    # Adds the current date and time to the instructions
    add_datetime_to_instructions=True,
    # Adds the history of the conversation to the messages
    add_history_to_messages=True,
    # Number of history responses to add to the messages
    num_history_responses=5,
    # Adds markdown formatting to the messages
    markdown=True,
)
team = Team(members=[web_agent])
playground = Playground(agents=[web_agent], teams=[team])
app = playground.get_app()

if __name__ == "__main__":
    playground.serve("playground:app", reload=True)