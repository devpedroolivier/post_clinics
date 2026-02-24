# Status Synchronization

## User Stories

* **As a** developer
* **I want** the notification flags to be updated atomically
* **So that** I don't send the same reminder twice.

## NEW Requirements

### Requirement: Atomic Updates
The system MUST update the `notified_24h` or `notified_3h` flags in the same transaction as the `NotificationLog` entry (if possible, or immediately after success) to prevent race conditions.

### Requirement: Skip logic
If an appointment is cancelled, all pending notification logic for it MUST stop immediately.

## Scenarios

### Scenario: Race condition avoidance
- **GIVEN** two instances of the scheduler were to run at once
- **WHEN** the first instance sends the 24h reminder
- **THEN** it immediately marks the DB flag so the second instance sees it as "already notified".
