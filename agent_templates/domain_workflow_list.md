# Domain Workflow Library

This directory provides example workflow definitions for different domains. Use these YAML files with `load_workflow` to bootstrap domain specific planning flows.

## Available Workflows

- `industry_agent_steps.yaml` – generic industry prompt workflow
- `finance_agent_steps.yaml` – finance domain prompt workflow
- `healthcare_agent_steps.yaml` – healthcare domain prompt workflow
- `agent_steps.yaml` – basic prompt workflow template

Each workflow uses the core agents from this project:

- `domain-specialist-agent`
- `prompt-engineering-agent`
- `prompt-quality-evaluator-agent`
- `prompt-optimizer-agent`

Load a workflow with:

```python
from app.flow.workflow_loader import load_workflow
wf = load_workflow("agent_templates/finance_agent_steps.yaml")
```
