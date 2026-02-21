# Spec: Code Learning Loop

## ADDED Requirements

### Requirement: Extract Learnings
O sistema DEVE ser capaz de analisar o histórico de conversões/dúvidas complexas e extrair regras de atendimento (learnings) de forma assíncrona.

#### Scenario: Asynchronous Learning Extraction
- **GIVEN** a cron-job or scheduler is triggered
- **WHEN** the system scans recent sqlite conversation logs for agent mistakes, human handoffs, or detailed explanations
- **THEN** the system extracts a structured "learning" rule
- **AND** the system saves this rule into the Vector Database

### Requirement: Inject Learnings
O agente DEVE injetar "learnings" prévios relacionados a um paciente ou contexto no prompt de sistema atual.

#### Scenario: Providing Context
- **GIVEN** a user sends a new message
- **WHEN** the agent initialization detects relevant historical "learnings" from the vector database
- **THEN** these learnings are appended to the system instructions to prevent repeating the same mistakes or asking the same preference questions
