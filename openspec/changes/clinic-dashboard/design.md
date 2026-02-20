# Design: Clinic Dashboard

## Context
The clinic needs a way to view appointments in a structured, visual format (calendar). Currently, appointments are only stored in SQLite and handled via an AI agent.

## Goals / Non-Goals
**Goals:**
- Provide a clear calendar view for clinic staff.
- Ensure the dashboard reflects the same state as the backend database.
- Create a modern, premium UI consistent with "POST Clinics" branding.

**Non-Goals:**
- User Authentication (for this MVP version, assume internal/one-clinic use).
- Multi-clinic support.
- Direct rescheduling through the dashboard (read-only for now, agent handles scheduling).

## Decisions
- **Framework**: Vite + React for fast development and state management.
- **State Management**: Simple `useEffect` with polling (every 30s) to keep it simple and robust for MVP.
- **UI Components**: `react-calendar` or a custom CSS Grid implementation for maximum design control.
- **API**: FastAPI will expose a new `/api/appointments` endpoint returning SQLModel objects as JSON.

## Risks / Trade-offs
- **CORS**: Cross-Origin Resource Sharing will need to be enabled in FastAPI.
- **Data Sync**: Polling might have a slight delay compared to WebSockets, but it's easier to maintain and sufficient for clinic operations.
