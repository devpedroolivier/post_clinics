## ADDED Requirements

### Requirement: Session Inactivity Timeout
The system MUST automatically close an active session if no messages have been exchanged for 30 minutes.

#### Scenario: Inactive session
- **WHEN** 30 minutes pass since the last message in an active session
- **THEN** the system marks the session as closed/inactive.

### Requirement: Session Reactivation
The system MUST create a new session or reactivate the conversation when a patient sends a message after their previous session has timed out.

#### Scenario: Message after timeout
- **WHEN** a patient sends a message and their last session was closed due to timeout
- **THEN** the system initiates a new session and the assistant greets the patient anew.
