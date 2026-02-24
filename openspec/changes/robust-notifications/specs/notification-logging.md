# Notification Logging

## User Stories

* **As a** developer
* **I want** to see every Z-API call attempt in the database
* **So that** I can debug failures without parsing text logs.

* **As a** clinic manager
* **I want** to see why a reminder failed (e.g., "invalid number")
* **So that** I can correct the patient's data.

## NEW Requirements

### Requirement: Database Logging
Each attempt to send a message via Z-API MUST result in a record in the `NotificationLog` table.

### Requirement: Failure Context
The system MUST capture the status code and response body for any Z-API errors.

## Scenarios

### Scenario: Successful send
- **GIVEN** a reminder is ready to be sent
- **WHEN** the system calls Z-API and receives a 200 OK
- **THEN** a record is created in `NotificationLog` with `status="sent"` and `sent_at=now`.

### Scenario: Failed send (Invalid Phone)
- **GIVEN** a patient has an invalid phone number
- **WHEN** the system calls Z-API and receives a 400 Bad Request
- **THEN** a record is created in `NotificationLog` with `status="failed"` and the error description from the response.
