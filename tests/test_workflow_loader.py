import pytest

from app.flow.workflow_loader import load_workflow


def test_load_workflow():
    wf = load_workflow("agent_templates/industry_agent_steps.yaml")
    assert wf["name"] == "industry_prompt_workflow"
    assert wf["steps"][0]["agent"] == "domain-specialist-agent"


@pytest.mark.sit
def test_load_workflow_sit():
    wf = load_workflow("agent_templates/industry_agent_steps.yaml")
    assert len(wf["steps"]) >= 5


@pytest.mark.uat
def test_load_workflow_uat():
    wf = load_workflow("agent_templates/industry_agent_steps.yaml")
    step_ids = [s["id"] for s in wf["steps"]]
    assert "final_review" in step_ids
