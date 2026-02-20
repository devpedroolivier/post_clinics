---
artifact_type: spec
---

# Spec: Agent Scheduling Logic

## ADDED Requirements

### Requirement: Dynamic Slot Calculation
The `check_availability` tool SHALL calculate available time slots based on the specific service duration requested.

#### Scenario: 60-minute service booking
- **WHEN** user requests a "1st time" appointment (60 mins) for 09:00
- **AND** existing appointment exists at 09:30 (30 mins duration)
- **THEN** 09:00 slot is UNAVAILABLE (overlap).

#### Scenario: 40-minute service booking
- **WHEN** user requests a "Return" appointment (40 mins) for 09:00
- **AND** existing appointment exists at 10:00
- **THEN** 09:00 slot is AVAILABLE (09:00-09:40 fits before 10:00).

### Requirement: Intelligent Slot Suggestion
The tool SHALL return a list of optimal start times (e.g., every 30 mins) that fit the requested duration.

#### Scenario: Suggesting slots
- **WHEN** user asks "what times do you have?" for a 40-min service
- **THEN** returns a list like "09:00, 09:30, 10:00" checking each against existing bookings.
