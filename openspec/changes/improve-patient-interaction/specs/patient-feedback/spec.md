## ADDED Requirements

### Requirement: Post-Appointment Feedback Request
The assistant MUST ask the patient for an evaluation/feedback immediately after successfully scheduling an appointment.

#### Scenario: Successful scheduling
- **WHEN** the assistant confirms an appointment has been scheduled successfully
- **THEN** the assistant asks the patient to evaluate the service.

### Requirement: Feedback Integration in Learning Loop
The system MUST extract patient evaluations and integrate them into the agent's context (persona) for continuous improvement.

#### Scenario: Integrating feedback
- **WHEN** a patient provides feedback after an appointment
- **THEN** the learning loop processes this feedback and updates the assistant's behavior/knowledge base.