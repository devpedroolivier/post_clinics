---
artifact_type: spec
---

# Spec: Agent Core Stability

## ADDED Requirements

### Requirement: Robust Tool Calling
The system SHALL reliably detect and execute tool calls from Llama-3 model.

#### Scenario: Agent calls tool
- **WHEN** agent outputs `<function=check_availability>{"date": "2023-10-27"}</function>` OR similar tag
- **THEN** system parses function name and JSON arguments properly
- **AND** executes tool and returns result to agent loop.

### Requirement: System Prompt Guidance
The agent's system prompt SHALL explicitly instruct the model on the required output format for tools.

#### Scenario: Prompting
- **WHEN** agent is initialized
- **THEN** Instructions include "Para usar ferramentas, use o formato: <function=NAME>ARGS_JSON</function>" to reduce hallucinated formats.
