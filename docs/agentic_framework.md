# Agentic System Framework

This document outlines a domain independent blueprint for building reliable and scalable agent based systems. The guidance distils the core design principles used throughout this project.

## 1. Parahelp SOP
Standardised prompt files (`.prompt.yaml`) capture role, objective, KPIs, output format and constraints. Versioning these assets allows consistent agent behaviour and easy onboarding for new workflows.

## 2. Prompt Folding
Break down complex projects into epics, features, user stories and tasks. Each prompt only needs the context relevant to its task which keeps reasoning efficient and enables the use of small models when appropriate.

## 3. Prompt Chains
Multiple specialised agents collaborate across planning, execution and evaluation stages. Orchestrators like `ChainOrchestrator` or `ReflexionAgent` maintain traceability of reasoning and provide accountability for every step.

## 4. Prompt Library
All prompts live in a central library with version history and quality notes. Reusable snippets and annotations speed up iteration and allow quick rollback should regressions appear.

## 5. Debug Log Agent
An internal logging agent records ambiguities, hallucinations and failures. Structured logs with confidence scores help diagnose errors and trigger fallbacks when needed.

## 6. FDE Agent Collaboration
Agents are grouped by role – planner, builder, tester, deployer and reflexion – mirroring the standard development lifecycle. Clear APIs and isolated domains reduce coupling and optimise multi agent communication.

Following these principles promotes modular, reliable and human aligned AI assistants that can evolve from small prototypes to enterprise scale deployments.
