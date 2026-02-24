# Reliable Reminder Logic

## User Stories

* **As a** clinic manager
* **I want** to be sure all patients receive their reminders
* **So that** the clinic's absenteeism rate is as low as possible.

* **As a** patient
* **I want** to receive my 24h and 3h reminders even if the system was down for a few hours
* **So that** I don't forget my health commitments.

## CHANGED Requirements

### Requirement: Check-Point Notification
The system no longer uses fixed 2-hour windows. It MUST send a reminder IF the appointment is within the target threshold (24.5h or 3.5h) AND the corresponding flag (`notified_24h` or `notified_3h`) is False.

### Requirement: Past Appointment Protection
The system MUST NEVER send a reminder for an appointment whose start time has already passed.

## NEW Requirements

### Requirement: Late Booking Detection
If an appointment is booked with less than 24 hours remaining (e.g., 10 hours before the start), the system SHOULD automatically mark `notified_24h` as True (or skip it) and only target the 3h reminder.

## Scenarios

### Scenario: Scheduler recovered from downtime
- **GIVEN** an appointment is scheduled for tomorrow at 10:00 (18 hours from now)
- **AND** the scheduler was down during the 24h window
- **WHEN** the scheduler starts up
- **THEN** it identifies `notified_24h` is False and `hours_until` is 18 (<= 24.5)
- **THEN** it sends the 24h reminder immediately.

### Scenario: Late booking skip
- **GIVEN** a patient books at 16:00 for tomorrow at 09:00 (17 hours away)
- **WHEN** the scheduler runs for the first time for this appointment
- **THEN** it skips the 24h reminder (as it's too late for a "tomorrow" message) and waits for the 3h window.
