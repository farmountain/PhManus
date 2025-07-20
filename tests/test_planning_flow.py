import asyncio
import json

import pytest

from app.agent.base import BaseAgent
from app.flow.base import PlanStepStatus
from app.flow.planning import PlanningFlow
from app.llm import LLM
from app.tool.planning import PlanningTool


class DummyAgent(BaseAgent):
    name: str = "dummy"
    description: str = "d"
    llm: LLM

    async def step(self) -> str:
        return "ok"


@pytest.fixture()
def dummy_flow(monkeypatch):
    planning_tool = PlanningTool()
    llm = LLM()

    async def fake_ask_tool(*args, **kwargs):
        tool_call = type(
            "TC",
            (),
            {
                "function": type(
                    "F",
                    (),
                    {
                        "name": "planning",
                        "arguments": json.dumps(
                            {
                                "command": "create",
                                "title": "Example Plan",
                                "steps": ["step1", "step2"],
                            }
                        ),
                    },
                )(),
            },
        )
        return type("Resp", (), {"tool_calls": [tool_call]})()

    monkeypatch.setattr(llm, "ask_tool", fake_ask_tool)
    agent = DummyAgent(llm=llm)
    flow = PlanningFlow(
        agents={"dummy": agent}, llm=llm, planning_tool=planning_tool, plan_id="p1"
    )
    return flow


@pytest.mark.asyncio
async def test_create_initial_plan(dummy_flow):
    flow = dummy_flow
    await flow._create_initial_plan("test request")
    await asyncio.sleep(0)
    assert "p1" in flow.planning_tool.plans
    assert flow.planning_tool.plans["p1"]["title"] == "Example Plan"


@pytest.mark.asyncio
async def test_get_current_step_info(dummy_flow):
    flow = dummy_flow
    await flow._create_initial_plan("req")
    await asyncio.sleep(0)
    index, info = await flow._get_current_step_info()
    await asyncio.sleep(0)
    assert index == 0
    assert info["text"] == "step1"
    assert (
        flow.planning_tool.plans["p1"]["step_statuses"][0]
        == PlanStepStatus.IN_PROGRESS.value
    )


@pytest.mark.asyncio
async def test_mark_step_completed(dummy_flow):
    flow = dummy_flow
    await flow._create_initial_plan("req")
    await asyncio.sleep(0)
    index, _ = await flow._get_current_step_info()
    flow.current_step_index = index
    await flow._mark_step_completed()
    await asyncio.sleep(0)
    assert (
        flow.planning_tool.plans["p1"]["step_statuses"][index]
        == PlanStepStatus.COMPLETED.value
    )
