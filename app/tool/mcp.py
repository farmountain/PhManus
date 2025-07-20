import asyncio
import re
from typing import ClassVar, Optional

import requests

from app.config import config
from app.tool.base import BaseTool, ToolResult


class MCPMarketplace(BaseTool):
    """Fetch available MCP servers from the official marketplace."""

    name: str = "mcp_marketplace"
    description: str = (
        "List community MCP servers from the official marketplace repository"
    )
    parameters: dict = {
        "type": "object",
        "properties": {
            "keyword": {
                "type": "string",
                "description": "Filter servers containing this keyword",
            }
        },
    }

    MARKET_URL: ClassVar[
        str
    ] = "https://raw.githubusercontent.com/modelcontextprotocol/servers/main/README.md"

    async def execute(self, keyword: Optional[str] = None) -> str:
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, requests.get, self.MARKET_URL)
        text = data.text
        servers = re.findall(r"\*\*\[(.*?)\]\((.*?)\)\*\*", text)
        lines = [f"{name} - {url}" for name, url in servers]
        if keyword:
            keyword = keyword.lower()
            lines = [line for line in lines if keyword in line.lower()]
        return "\n".join(lines) if lines else "No servers found"


class MCPServerTool(BaseTool):
    """Interact with a configured MCP server."""

    name: str = "mcp_server"
    description: str = "Interact with the configured MCP server for plan storage"
    parameters: dict = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "enum": ["list_tools"],
                "description": "Operation to perform",
            }
        },
        "required": ["command"],
    }

    async def execute(self, command: str) -> ToolResult:
        if not config.mcp_config or not config.mcp_config.server_url:
            return ToolResult(output="No MCP server configured")
        url = config.mcp_config.server_url.rstrip("/")
        headers = {}
        if config.mcp_config.api_key:
            headers["Authorization"] = f"Bearer {config.mcp_config.api_key}"
        if command == "list_tools":
            return await self._list_tools(url, headers)
        return ToolResult(output=f"Unknown command: {command}")

    async def _list_tools(self, url: str, headers: dict) -> ToolResult:
        endpoint = f"{url}/tools"
        loop = asyncio.get_event_loop()
        resp = await loop.run_in_executor(
            None, lambda: requests.get(endpoint, headers=headers, timeout=5)
        )
        if resp.status_code != 200:
            return ToolResult(output=f"Server error: {resp.status_code}")
        try:
            data = resp.json()
        except Exception:
            return ToolResult(output=resp.text)
        if isinstance(data, list):
            return ToolResult(output="\n".join(data))
        return ToolResult(output=str(data))
