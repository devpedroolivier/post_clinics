# Technical Design: Robust Notifications

## Context
POST Clinics currently uses a basic scheduler that runs every 10 minutes (`SCHEDULER_INTERVAL`) and checks for appointments within specific 2-hour windows (23-25h and 2.5-3.5h). This approach is fragile: if the scheduler is down for 2 hours, notifications are never sent.

## Goals
- Guarantee that all appointments receive a 24h and 3h reminder if they haven't been sent.
- Provide full observability into why a notification failed (invalid phone, Z-API error, etc.).
- Prevent accidental duplicate notifications.
- Correct handling of timezone offsets.

## Non-Goals
- Real-time notification tracking (webhook responses for "delivered/read") is not in scope yet (just "sent").

## Architecture / Implementation

### 1. Database Schema (`src/domain/models.py`)
Add a `NotificationLog` model:
- `id` (PK)
- `appointment_id` (FK)
- `notification_type` ("24h", "3h")
- `status` ("sent", "failed")
- `error_message` (str, nullable)
- `sent_at` (datetime)
- `attempt_count` (int)

### 2. Refined Scheduler Logic (`src/application/scheduler.py`)
Replace the window check (e.g., `23 <= hours_until <= 25`) with a "Check-Point" logic:
- `is_within_24h = hours_until <= 24.5` (slight buffer for late bookings)
- `needs_24h_reminder = is_within_24h and not appointment.notified_24h`
- For 3h: `hours_until <= 3.5 and not appointment.notified_3h`

**Edge Case Protection**:
- Check if the appointment is in the PAST before sending.
- Check if the appointment was created *after* the 24h mark (e.g., booked for "in 12 hours"). In this case, maybe skip 24h and send only 3h.

### 3. Z-API Wrapper Enhancement (`src/infrastructure/services/zapi.py`)
- Refactor `send_message` to return a richer result (success, status_code, response_body).
- Wrap the call in a retry loop (using `tenacity` or a simple `while` loop with backoff).

### 4. Timezone Handling
- Always use `datetime.now(BR_TZ)` and avoid `replace(tzinfo=None)` for comparisons.
- SQLite stores naive datetimes, so ensure we compare `Appointment.datetime` (naive) against `now.replace(tzinfo=None)`.

## Risks / Trade-offs
- **Risk**: Infinite retries if a phone number is invalid. **Mitigation**: Limit `max_attempts` and flag as "permanently failed" on 4xx errors.
