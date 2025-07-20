import asyncio
import json
import os
from app.tool.planning import PlanningTool
import pytest


def test_json_persistence(tmp_path):
    path = tmp_path / "plans.json"
    tool = PlanningTool(storage_type="json", storage_path=str(path))
    asyncio.run(tool.execute(command="create", plan_id="p1", title="t", steps=["s1"]))
    assert path.exists()
    tool2 = PlanningTool(storage_type="json", storage_path=str(path))
    assert "p1" in tool2.plans


@pytest.mark.asyncio
@pytest.mark.sit
async def test_resume_command(tmp_path):
    path = tmp_path / "plans.json"
    tool = PlanningTool(storage_type="json", storage_path=str(path))
    await tool.execute(command="create", plan_id="p1", title="t", steps=["s1"])
    await tool.execute(command="create", plan_id="p2", title="t2", steps=["x"])
    await tool.execute(command="set_active", plan_id="p1")
    await tool.execute(command="resume", plan_id="p2")
    assert tool._current_plan_id == "p2"


@pytest.mark.asyncio
@pytest.mark.uat
async def test_sqlite_persistence(tmp_path):
    path = tmp_path / "plans.db"
    tool = PlanningTool(storage_type="sqlite", storage_path=str(path))
    await tool.execute(command="create", plan_id="p1", title="t", steps=["s1"])
    assert path.exists()
    tool2 = PlanningTool(storage_type="sqlite", storage_path=str(path))
    assert "p1" in tool2.plans
