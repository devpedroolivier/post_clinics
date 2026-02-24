# Frontend Calendar Views

## User Stories

* **As a** secretary
* **I want** to map the calendar visually and see a full week or month
* **So that** I can manage a busy clinic with multiple professionals.

## CHANGED Requirements

### Requirement: Calendar View Options
The dashboard MUST provide buttons to switch between Daily, Weekly, and Monthly views using FullCalendar.

## NEW Requirements

### Requirement: Professional Labeling
The frontend event cards MUST display the professional's name prominently alongside the patient's name and service.

## Scenarios

### Scenario: Switching to Weekly View
- **GIVEN** the user is looking at the dashboard
- **WHEN** they click "Semana"
- **THEN** the calendar switches to a timeGridWeek view, revealing all slots across the week.
