# Design: Appointment CRUD

## Backend (FastAPI)
### New Endpoints
1.  `DELETE /api/appointments/{appointment_id}`
    -   Action: Deletes the record from `appointments` table (or marks as cancelled).
    -   Parameters: `id`.
    -   Response: `{"status": "success"}`.

2.  `PUT /api/appointments/{appointment_id}`
    -   Action: Updates fields (datetime, status, service, patient_name/phone).
    -   Body: JSON with fields to update.
    -   Response: `{"status": "success"}`.

## Frontend (Dashboard)
### "Details" Modal
-   Inject **"Editar"** and **"Excluir"** buttons into the `eventDetailsModal`.
-   **Edit Flow**: Open a pre-filled form (reuse `appointmentModal` or create a new one).
-   **Delete Flow**: Confirm dialog -> Call DELETE API -> Remove from Calendar.

### Logic
-   `api.ts`: Add `updateAppointment` and `deleteAppointment` functions.
-   `main.ts`: Handle button clicks in the details modal.
