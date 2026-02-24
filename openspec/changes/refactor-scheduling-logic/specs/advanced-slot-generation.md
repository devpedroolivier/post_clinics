# Advanced Slot Generation

## User Stories

* **As a** patient
* **I want** to be offered clear, specific timeslots (e.g., 08:00, 08:45)
* **So that** I don't get confused by random gap times and can choose easily.

* **As a** clinic manager
* **I want** the system to enforce 45-minute strict slots
* **So that** the doctor's schedule is organized and predictably full without gaps.

## CHANGED Requirements

### Requirement: Deterministic Slot Grid
The system no longer calculates free gaps dynamically. It MUST project a fixed grid of 45-minute slots onto the professional's working hours, and subtract any slots that overlap with existing appointments.

### Requirement: 5 Options Rule
The system MUST return a maximum of 5 available slots to the user, ideally distributed as morning and afternoon options to give variety.

## NEW Requirements

(None strictly new, replacing the existing gap logic with fixed grid logic).

## Scenarios

### Scenario: Requesting availability for a full day
- **GIVEN** a professional has working hours 08:00–11:30 and 13:00–17:30
- **WHEN** the patient asks for availability on an empty day
- **THEN** the system generates slots: 08:00, 08:45, 09:30, 10:15... and 13:00, 13:45, etc., returning the first 5 across the morning and afternoon.

### Scenario: Requesting availability after hours
- **GIVEN** the global block rule 09:00-18:00 for the clinic
- **WHEN** the generator runs
- **THEN** no slot shall be offered before 08:00 or after 18:00 regardless of individual professional bounds (just a failsafe).
