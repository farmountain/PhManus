import os
import sys

import pytest


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.config import config
from app.tool.planning import PlanningTool


@pytest.fixture(autouse=True)
def disable_mcp(monkeypatch):
    monkeypatch.setattr(config._config, "mcp_config", None)

    async def _noop(*args, **kwargs):
        return None

    monkeypatch.setattr(PlanningTool, "_sync_with_mcp", _noop)
