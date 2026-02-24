# Retry Mechanism

## User Stories

* **As a** developer
* **I want** the system to automatically retry on network failures or 500 errors
* **So that** transient Z-API downtime doesn't result in missed reminders.

* **As a** clinic manager
* **I want** to avoid duplicate messages during retries
* **So that** I don't annoy the patient with many identical reminders.

## NEW Requirements

### Requirement: Retry Strategy
On any 5xx error or transient network error (e.g., timeout, connection refused), the system MUST retry the call.

### Requirement: Backoff Delay
The system SHOULD wait for an increasing amount of time (e.g., 2, 4, 8 minutes) between retries.

### Requirement: Max Attempts Limit
The system MUST stop retrying after a configurable maximum number of attempts (default 3) to prevent infinite loops.

## Scenarios

### Scenario: Z-API is temporarily offline (503)
- **GIVEN** a reminder is ready to be sent
- **WHEN** the system calls Z-API and receives a 503 Service Unavailable
- **THEN** it waits 2 minutes and retries.
- **AND** it marks the attempt in `NotificationLog`.

### Scenario: Z-API is permanently failing (400)
- **GIVEN** a patient has an invalid number
- **WHEN** the system calls Z-API and receives a 400 Bad Request
- **THEN** it does NOT retry, as the error is client-side and persistent.
