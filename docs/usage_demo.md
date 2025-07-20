# Usage Example

The simplest way to try the framework is to run the interactive command line
helper:

```bash
python run_flow.py
```

You will be prompted for a task description. The `PlanningFlow` will generate a
plan, execute each step with the `Manus` agent and print the result. For example:

```text
Enter your prompt: Summarise the recent news about space exploration
Processing your request...
Plan completed:
...
```

For advanced usage you can embed `PlanningFlow` in your own Python code and pass
custom agents:

```python
from app.flow.planning import PlanningFlow
from app.agent.manus import Manus

flow = PlanningFlow(agents={"manus": Manus()})
result = asyncio.run(flow.execute("Find today's weather in Paris"))
print(result)
```
You can also load predefined workflows from YAML:
```python
from app.flow.workflow_loader import load_workflow
wf = load_workflow("agent_templates/industry_agent_steps.yaml")
print(wf["steps"])
```
