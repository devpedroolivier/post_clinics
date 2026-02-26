## ADDED Requirements

### Requirement: Persistent Human Handoff
The system MUST persist the handoff state and completely halt automated responses for the session when a patient requests a human attendant, until explicitly resumed or timed out.

#### Scenario: Patient requests human
- **WHEN** the patient asks to speak with a human or the agent triggers `request_human_attendant`
- **THEN** the system sets a persistent handoff state and stops routing subsequent patient messages to the LLM.
