import pytest

from app.prompt.loader import load_prompt


def test_load_prompt():
    data = load_prompt("prompt_templates/finance.prompt.yaml")
    assert data["role"] == "finance-domain-specialist"


@pytest.mark.sit
def test_prompt_missing_field(tmp_path):
    path = tmp_path / "bad.prompt.yaml"
    path.write_text("role: r")
    with pytest.raises(ValueError):
        load_prompt(str(path))


@pytest.mark.uat
def test_load_healthcare_prompt():
    data = load_prompt("prompt_templates/healthcare.prompt.yaml")
    assert "patient_safety" in data["kpis"]
