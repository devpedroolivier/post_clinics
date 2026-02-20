---
artifact_type: spec
---

# Spec: Agent Notifications (Scheduler)

## ADDED Requirements

### Requirement: 24h Reminder
The system SHALL send a WhatsApp reminder 24 hours before the appointment.

#### Scenario: Sending 24h reminder
- **WHEN** current time is 24h before appointment +/- threshold (e.g., 23-25h window)
- **AND** `notified_24h` is False
- **THEN** system sends Z-API message template "Lembrete: Sua consulta é amanhã..."
- **AND** sets `notified_24h` to True.

### Requirement: 3h Confirmation/Reminder
The system SHALL send a WhatsApp reminder 3 hours before the appointment.

#### Scenario: Sending 3h reminder
- **WHEN** current time is 3h before appointment
- **AND** `notified_3h` is False
- **THEN** system sends Z-API message template "Lembrete: Sua consulta é em 3 horas..."
- **AND** sets `notified_3h` to True.
