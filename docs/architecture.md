# Architecture

PhManus is organised around a collection of asynchronous agents, tools and flows.
The `PlanningFlow` coordinates task execution by invoking different agents. Each agent
subclasses `BaseAgent` and can use tools from `ToolCollection` such as `PythonExecute`,
`WebSearch` and `BrowserUseTool`.

The central planning capability is implemented via the `PlanningTool`, which tracks
step progress and can optionally persist plans to JSON or SQLite files. Agents call
this tool through the language model using function calling to create, update and
resume plans.

```
User -> PlanningFlow -> [Agents] -> Tools
                     \-> PlanningTool (plan storage)
```

The LLM interface is encapsulated in `LLM` which supports OpenAI, Azure and Ollama
endpoints.  Configuration is loaded from `config.toml`.
Workflows can also be described in YAML files. The helper `load_workflow` parses these definitions so they can be inspected or executed programmatically.
