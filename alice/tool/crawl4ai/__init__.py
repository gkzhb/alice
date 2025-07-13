from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools

# use https://github.com/gkzhb/crawl4ai-mcp
crawl4ai_server_url = "http://localhost:8585/mcp"

# crawl4ai_mcp = MCPTools(url=crawl4ai_server_url, transport="sse")