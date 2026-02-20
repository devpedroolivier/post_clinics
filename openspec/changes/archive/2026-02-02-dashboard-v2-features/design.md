# Design: Dashboard V2

## Context
The current dashboard is a read-only list of cards. The clinic needs a proper calendar view to manage time slots effectively and a way to input data manually.

## Goals
- **Calendar**: Visual representation of time slots. Click to inspect.
- **Manual Entry**: Simple form to add `Patient Name`, `Phone`, `Service`, `Date/Time`.
- **Sync**: Manual entries must trigger the same database updates as AI agents.

## Decisions
- **Library**: Use `@fullcalendar/core`, `@fullcalendar/daygrid`, `@fullcalendar/timegrid` (Standard, robust, free tier sufficient).
- **UI Interaction**:
    - "New Appointment" floating button (FAB) or Header button opens a Modal.
    - Modal contains a simple HTML form.
    - Form submits JSON to `POST /api/appointments`.
- **Tech Stack**: Continue using Vanilla TypeScript + CSS (No React/Vue framework overhead needed for this simple MVP).

## Risks
- **Timezone**: Ensure `datetime` from manual entry matches the server's expected UTC/Local format.
- **Validation**: Basic validation for phone numbers and dates on the frontend.
