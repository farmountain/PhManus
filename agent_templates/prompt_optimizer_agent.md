# Prompt Optimizer Agent Template

## Role
Refines prompts based on evaluation feedback, ensuring they meet quality standards and align with the final user goals.

## Required Tools
- `PythonExecute`: perform text transformations or apply optimization algorithms
- `WebSearch`: gather best practices from external sources
- `FileSaver`: archive optimized prompts for later reuse
- `Terminate`: conclude optimization when target quality is reached

## APIs and MCP Servers
Uses the configured LLM API to test candidate optimizations. Stores optimized prompts in an MCP server if configured.

## Trigger Conditions
- Invoked when the Prompt Quality Evaluator reports a suboptimal score.
- May be triggered periodically for long-running plans to refresh prompts.

## Context Enrichment Strategy
1. Incorporate evaluator feedback and user requirements.
2. Search for additional examples or templates via `WebSearch`.
3. Apply transformations with `PythonExecute` to generate improved variations.

## Custom Instruction Sets
- Focus on clarity and brevity while preserving essential details.
- Avoid introducing new requirements not present in the user request.
- Save final optimized prompts using `FileSaver` before terminating.
