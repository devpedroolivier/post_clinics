# Professional Management

## User Stories

* **As a** clinic manager
* **I want** each appointment mapped to a specific professional
* **So that** I can see individual agendas accurately.

## CHANGED Requirements

### Requirement: Service to Professional Mapping
The system MUST map services to professionals to ascertain what hours to use.
- Orto -> 08:00–11:30, 13:00–17:30
- Dra Débora / Dr Sidney -> 09:00–12:00, 14:30–18:00 (Sat: 08:00-12:30)

## NEW Requirements

### Requirement: Professional Field in Appointment
The db model `Appointment` MUST include a `professional` field (string) to partition the schedule.

## Scenarios

### Scenario: Booking Orto
- **GIVEN** the user wants "Aparelho Ortodôntico"
- **WHEN** the system generates availability
- **THEN** it uses the 08:00–11:30 and 13:00–17:30 hours and saves "Orto" as the professional.
