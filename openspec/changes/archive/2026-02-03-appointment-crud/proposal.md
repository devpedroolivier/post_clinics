# Proposal: Appointment CRUD

## Goal
Add "Edit" and "Delete" capabilities to the existing Appointment management.

## Motivation
Currently, users can only create appointments. If a mistake is made or an appointment is cancelled, there's no way to manage it from the dashboard.

## Capabilities
### Capabilities Affected
- **Dashboard**: Will show Edit/Delete buttons in the "Details" modal.
- **Backend API**: New endpoints to modify database records.

## Success Criteria
1.  **Edit**: User can change date, service, or status of an appointment.
2.  **Delete**: User can remove an appointment (soft delete or hard delete).
3.  **UI Feedback**: Toast notifications for success/error.
