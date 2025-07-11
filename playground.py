import asyncio
from agno.agent import Agent
from agno.team import Team
from agno.playground import Playground
from agno.storage.sqlite import SqliteStorage
from agno.tools.mcp import MCPTools
# from agno.tools.duckduckgo import DuckDuckGoTools
# from agno.tools.yfinance import YFinanceTools
from alice.model.llm import ds_chat_model, ds_reasoning_model
from alice.tool.crawl4ai import crawl4ai_server_url

agent_storage: str = "data/dev/playground-agents.db"

async def init_playground():
    async with MCPTools(
        url=crawl4ai_server_url,
        transport="streamable-http",
        timeout_seconds=30,
    ) as mcp_tools:
        web_agent = Agent(
            name="Web Agent",
            model=ds_chat_model,
            tools=[mcp_tools],
            instructions=["Always include sources"],
            storage=SqliteStorage(table_name="web_agent", db_file=agent_storage),
            add_datetime_to_instructions=True,
            add_history_to_messages=True,
            num_history_responses=5,
        )
        team = Team(members=[web_agent])
        playground = Playground(agents=[web_agent],teams=[team])
        app = playground.get_app()
        return playground, app

playground, app = asyncio.run(init_playground())

if __name__ == "__main__":
    # playground.serve("playground:app", reload=True)
    playground.serve(app)