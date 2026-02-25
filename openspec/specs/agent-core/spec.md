# agent-core Specification

## Purpose
TBD - created by archiving change agent-anti-hallucination-tests. Update Purpose after archive.
## Requirements
### Requirement: Strict Context Boundary Enforcement
The agent MUST explicitly refuse to answer or state its lack of knowledge when a user query requests information not present in the injected context or its baseline training, strongly prioritizing the injected context.

#### Scenario: Query outside of context
- **WHEN** a user asks a question about a specific clinic protocol not present in the dynamically injected context
- **THEN** the agent responds indicating it does not have that information, rather than inventing a plausible protocol

### Requirement: Ambiguity Resolution Prompting
The agent MUST ask clarifying questions when the user prompt is too ambiguous to map securely to the available context.

#### Scenario: Ambiguous user query
- **WHEN** the user provides an overly broad or ambiguous prompt
- **THEN** the agent requests clarification before attempting to fetch context or provide a final answer

