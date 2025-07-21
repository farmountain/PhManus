# Deployment Framework

This guide expands on the agentic design principles to outline how to create and operate large scale AI agents.

## 1. Parahelp SOP
Use structured prompt files (`.prompt.yaml`) defining role, objective, KPIs, output format and constraints. Version these files to ensure consistent behaviour across deployments.

## 2. Prompt Folding
Decompose projects from epics to tasks so each prompt contains only the context it needs. This keeps reasoning efficient and allows small models to handle micro‑tasks.

## 3. Prompt Chain
Stage agents for planning, execution and verification. Coordinators such as a `ChainOrchestrator` or `ReflexionAgent` maintain accountability and traceability between steps.

## 4. Prompt Library
Maintain a library of versioned prompts with quality annotations and rollback history. Reusable components help new agents ramp up quickly.

## 5. Debug Log Agent
Run an internal agent that records ambiguities and failures with confidence scores. Logs provide a feedback loop for continuous improvement.

## 6. FDE Agent Collaboration
Organise agents around the development value stream: planner, builder, tester, deployer and reflexion. Well‑defined APIs or shared memory keep them isolated yet cooperative.

Following these principles enables a modular and reliable approach for deploying enterprise or consumer grade AI assistants.

## Release Docker Images
For quick evaluation you can build a lightweight Docker image:

```bash
bash scripts/build-release-image.sh
```

Run the image with:

```bash
docker run -p 5000:5000 phmanus:release
```

This launches the web UI on port 5000.
