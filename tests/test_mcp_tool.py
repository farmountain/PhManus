import pytest

from app.tool.mcp import MCPMarketplace, MCPServerTool, config, requests


class DummyResponse:
    text = "**[Server](http://example.com)**"
    status_code = 200

    def json(self):
        return ["tool1", "tool2"]


@pytest.mark.asyncio
async def test_marketplace(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda url: DummyResponse())
    tool = MCPMarketplace()
    result = await tool.execute()
    assert "Server" in result


@pytest.mark.asyncio
async def test_server_list(monkeypatch):
    monkeypatch.setattr(
        config._config,
        "mcp_config",
        type("cfg", (), {"server_url": "http://x", "api_key": None}),
    )
    monkeypatch.setattr(requests, "get", lambda *a, **k: DummyResponse())
    tool = MCPServerTool()
    res = await tool.execute("list_tools")
    assert "tool1" in res.output
