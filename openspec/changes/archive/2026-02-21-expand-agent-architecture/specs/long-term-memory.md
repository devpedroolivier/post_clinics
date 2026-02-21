# Spec: Long Term Memory

## ADDED Requirements

### Requirement: Store Patient Preferences
O sistema DEVE ser capaz de armazenar preferências importantes declaradas pelos pacientes (ex: "só posso vir de manhã", "tenho alergia a X").

#### Scenario: Saving a Preference
- **GIVEN** a patient explicitly states a durable preference or constraint during a conversation
- **WHEN** the conversation turn ends
- **THEN** the system invokes an update to the patient's long-term memory profile in the Vector Database or a dedicated SQL table

### Requirement: Retrieve Patient Profile
O agente DEVE acessar o sumário consolidado do paciente no início da conversa.

#### Scenario: Returning Patient
- **GIVEN** a known patient sends a message
- **WHEN** the session initializes
- **THEN** the patient's long-term summary is retrieved and provided to the agent as background context
