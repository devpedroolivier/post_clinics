---
artifact_type: spec
---

# Spec: Agent Tools Management

## ADDED Requirements

### Requirement: Cancel Appointment Tool
The agent SHALL have a `cancel_appointment` tool that updates an appointment status to 'cancelled'.

#### Scenario: User requests cancellation
- **WHEN** user says "cancel my appointment"
- **THEN** agent calls `cancel_appointment` with appointment ID (found via context/phone)
- **AND** system updates DB status to `cancelled`.

### Requirement: Reschedule Appointment Tool
The agent SHALL have a `reschedule_appointment` tool or logic to atomic move an appointment.

#### Scenario: User requests rescheduling
- **WHEN** user says "move my appointment from 10:00 to 14:00"
- **THEN** agent verifies 14:00 availability
- **AND** calls `reschedule_appointment(old_id, new_datetime)`
- **AND** system cancels old appt and creates new one for same patient.
