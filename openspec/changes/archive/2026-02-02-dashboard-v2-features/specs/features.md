# Specs: Dashboard V2 Features

### Requirement: Interactive Calendar
The dashboard displays appointments on a calendar grid.

#### Scenario: View Appointments
- **WHEN** the dashboard loads.
- **THEN** it renders a standard calendar view (Month/Week).
- **AND** appointments appear as events on the correct date/time.

### Requirement: Manual Appointment Entry
Clinic staff can manually register appointments.

#### Scenario: Add Appointment
- **WHEN** the user clicks "Nova Consulta".
- **THEN** a modal appears asking for Patient Name, Phone, and Date/Time.
- **WHEN** the form is submitted.
- **THEN** a `POST` request is sent to the backend.
- **AND** the calendar refreshes to show the new event.
