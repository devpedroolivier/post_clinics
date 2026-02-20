# Proposal: Validation of Appointment Flows and Dashboard Integration

## Background
The system has implemented Dockerized backend/frontend and Agentic flows for appointment scheduling. We need to ensure that the core business logic—scheduling, confirming, rescheduling, and canceling appointments—works reliably across both the AI Agent interface and the Dashboard. Additionally, we need to verify that the reminder workflows are triggered correctly according to clinic rules.

## Goals
1.  **Validate Agent Flows**:
    *   Scheduling a new appointment.
    *   Confirming an appointment.
    *   Rescheduling an existing appointment.
    *   Canceling an appointment.
2.  **Validate Dashboard Interactions**:
    *   Manual creation of appointments by the clinic staff.
    *   Viewing and managing existing appointments.
3.  **Validate Workflows**:
    *   Ensure the "Reminder" workflow operates correctly upon appointment confirmation.
    *   Verify data consistency between Agent, Database, and Dashboard.

## Non-Goals
*   Refactoring the underlying database schema (unless blocking).
*   UI/UX redesign of the Dashboard (focus is on functionality).

## Risks
*   Z-API connectivity or simulation might be flaky during testing.
*   Database state might need frequent resetting during testing cycles.

## Success Criteria
*   All 4 agent flows (Schedule, Confirm, Reschedule, Cancel) passes.
*   Dashboard correctly reflects all changes made by the Agent.
*   Manual Dashboard changes are reflected in the system and trigger appropriate workflows.
