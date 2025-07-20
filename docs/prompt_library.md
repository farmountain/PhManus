# Prompt Library

The `prompt_templates` directory contains standardized prompt specifications using the Parahelp SOP schema. Each `.prompt.yaml` file defines:

- `role`: the agent role name
- `objective`: the desired goal of the agent
- `kpis`: success metrics
- `output_format`: expected output style
- `constraints`: key limitations or policies

Example:
```yaml
role: finance-domain-specialist
objective: "Provide financial analysis and recommendations"
kpis:
  - regulatory_compliance
  - accuracy
output_format: markdown
constraints:
  - "No personal investment advice"
  - "Adhere to local financial regulations"
```
Use these files as starting points for new agents or workflows. They provide versioned, reusable assets that align with the core design principles.
