# Specs: Clinic Dashboard

### Requirement: Appointment Visualization
The dashboard correctly displays appointments fetched from the backend.

#### Scenario: Load Calendar
- **WHEN** the dashboard page is opened.
- **THEN** it makes a request to `GET /api/appointments`.
- **AND** it renders each appointment as a card/event in the calendar view.

#### Scenario: Real-time Update (Polling)
- **WHEN** a new appointment is added via the AI agent.
- **THEN** within 30 seconds, the dashboard refreshes its state.
- **AND** the new appointment appears on the calendar.

### Requirement: Responsive UI
The dashboard must be accessible on both desktop and tablet resolutions.

#### Scenario: Mobile View
- **WHEN** the screen width is less than 768px.
- **THEN** the calendar switches to a list view or a condensed layout.
