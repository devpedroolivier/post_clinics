# Proposal: Dashboard V2 - Interactive Calendar & Manual Utils

## Goal
Enhance the clinic dashboard with an interactive calendar visualization and a tool for manually registering physical/past appointments.

## Capabilities

### New Capabilities
- `interactive-calendar`: Replace the static grid with a fully interactive calendar (e.g., FullCalendar) supporting month/week/day views.
- `manual-appointment-entry`: A form interface to register appointments that weren't made via the AI agent (e.g., reception desk, legacy data).

## Impact
- **Frontend**: Integration of a calendar library (FullCalendar) and creation of a Modal/Form component.
- **Backend**: New `POST /api/appointments` endpoint to handle manual creations.
- **Database**: Leveraging existing `Appointment` and `Patient` tables.
