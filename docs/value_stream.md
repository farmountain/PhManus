# Value Stream Activities

PhManus focuses on planning and execution of tasks through a sequence of agents and tools. The high level value stream is:

1. **User Request** – a task description is provided through the CLI or chat interface.
2. **Plan Generation** – `PlanningFlow` uses the LLM and `PlanningTool` to create a step based plan.
3. **Agent Execution** – each step is delegated to the appropriate agent. Agents may call tools or other agents.
4. **Result Aggregation** – outputs from agents are stored in memory and summarised when the plan completes.
5. **Persistence & MCP Integration** – optional interaction with MCP servers to list community tools or save plans.

These activities allow the framework to continuously refine tasks and deliver results that can be reused or extended in future plans.
