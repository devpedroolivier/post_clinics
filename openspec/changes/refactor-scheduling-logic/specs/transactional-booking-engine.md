# Transactional Booking Engine

## User Stories

* **As a** patient
* **I want** my booking to be guaranteed once confirmed
* **So that** I don't show up and find someone else in my spot.

* **As a** clinic manager
* **I want** cancellations to immediately free up the slot
* **So that** I can book someone else right away.

## CHANGED Requirements

### Requirement: Concurrency Prevention
The system MUST guarantee that two simultaneous requests for the same professional at the exact same datetime do not result in a double booking.

### Requirement: Robust Cancellation Sync
When an appointment is cancelled, its status MUST be updated to `cancelled`, and the availability engine MUST ignore it when calculating free slots.

## NEW Requirements

### Requirement: Database Constraints
The `Appointment` table MUST have logic or composite constraints to reject duplicate `(professional_id, datetime)` pairs if the status is active (`scheduled` or `confirmed`).

## Scenarios

### Scenario: Race condition on the same slot
- **GIVEN** two users try to book Dr. Sidney at 09:00 on the exact same second
- **WHEN** the backend processes the requests
- **THEN** the first transaction succeeds, and the second transaction fails with an error (or is gracefully handled by the AI to offer the next slot).

### Scenario: Cancellation frees slot
- **GIVEN** an appointment exists at 10:00
- **WHEN** the user or admin cancels it
- **THEN** the slot at 10:00 immediately appears in the next availability request.
