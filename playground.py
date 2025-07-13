from datetime import timedelta
from typing import Union
import asyncio
import nest_asyncio
from urllib.parse import quote

from agno.agent import Agent
from agno.team import Team
from agno.playground import Playground
from agno.storage.sqlite import SqliteStorage
from agno.tools.mcp import MCPTools, StreamableHTTPClientParams
from agno.api.playground import PlaygroundEndpointCreate, create_playground_endpoint
from agno.cli.console import console
from agno.cli.settings import agno_cli_settings
from agno.utils.log import logger

from fastapi import FastAPI
from rich import box
from rich.panel import Panel
# from agno.tools.duckduckgo import DuckDuckGoTools
# from agno.tools.yfinance import YFinanceTools
from alice.model.llm import ds_chat_model, ds_reasoning_model
from alice.tool.crawl4ai import crawl4ai_server_url

nest_asyncio.apply()

agent_storage: str = "data/dev/playground-agents.db"

# refer to https://github.com/agno-agi/agno/issues/2703#issuecomment-2798848659
async def serve_playground_app_async(
    app: Union[str, FastAPI],
    *,
    scheme: str = "http",
    host: str = "localhost",
    port: int = 7777,
    reload: bool = False,
    prefix="/v1",
    **kwargs,
):
    import uvicorn

    try:
        create_playground_endpoint(
            playground=PlaygroundEndpointCreate(
                endpoint=f"{scheme}://{host}:{port}", playground_data={"prefix": prefix}
            ),
        )
    except Exception as e:
        logger.error(f"Could not create playground endpoint: {e}")
        logger.error("Please try again.")
        return

    logger.info(f"Starting playground on {scheme}://{host}:{port}")
    # Encode the full endpoint (host:port)
    encoded_endpoint = quote(f"{host}:{port}")

    # Create a panel with the playground URL
    url = f"{agno_cli_settings.playground_url}?endpoint={encoded_endpoint}"
    panel = Panel(
        f"[bold green]Playground URL:[/bold green] [link={url}]{url}[/link]",
        title="Agent Playground",
        expand=False,
        border_style="cyan",
        box=box.HEAVY,
        padding=(2, 2),
    )

    # Print the panel
    console.print(panel)

    config = uvicorn.Config(app=app, host=host, port=port, reload=reload, **kwargs)
    server = uvicorn.Server(config)
    await server.serve()

async def init_playground():
    params = StreamableHTTPClientParams(
        url=crawl4ai_server_url,
        timeout = timedelta(seconds=60),
        sse_read_timeout = timedelta(seconds=60 * 5),
    )
    async with MCPTools(
        url=crawl4ai_server_url,
        transport="streamable-http",
        timeout_seconds=60,
        server_params=params,
    ) as mcp_tools:
        print("成功连接到 crawl4ai MCP 服务器")
        web_agent = Agent(
            name="网页总结",
            model=ds_chat_model,
            tools=[mcp_tools],
            instructions=["""你是阅读小助手，帮助用户分析总结信息，并回答用户提出的问题。

## 要求
1. 识别到 URL 时，使用 mcp 工具 fetch_web 来获取 URL 的网页内容
2. 回答用户时使用中文回答"""],
            storage=SqliteStorage(table_name="web_agent", db_file=agent_storage),
            add_datetime_to_instructions=True,
            add_history_to_messages=True,
            num_history_responses=5,
        )
        team = Team(members=[web_agent])
        playground = Playground(agents=[web_agent],teams=[team])
        app = playground.get_app()
        await serve_playground_app_async(app)

if __name__ == "__main__":
    asyncio.run(init_playground())