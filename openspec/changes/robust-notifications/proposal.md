# Robust Notifications & Reminders

## Why
The current notification system in `src/application/scheduler.py` uses fixed windows (e.g., exactly between 23 and 25 hours before an appointment) which are fragile. If the scheduler misses its window, the notification is lost. Additionally, there is no log in the database for failed attempts, making it impossible to distinguish between a "not sent" status due to logic versus a "not sent" due to a Z-API failure.

## What Changes
1. **Window-less Notification Logic**: Move from fixed windows (23-25h) to a more robust "Is it within 24h and not already sent?" logic.
2. **Notification Persistence**: Introduce a `NotificationLog` model to track every attempt, status code, and timestamp for better observability.
3. **Retry Strategy**: Implement an automatic retry mechanism for 5xx or transient network errors when sending via Z-API.
4. **Status Consistency**: Ensure that notifications are only sent for `confirmed` or `scheduled` statuses and that a notification attempt marks the appointment definitively so as not to duplicate.
5. **Dashboard Observability**: (Optional/Secondary) Show notification status (sent/failed) in the dashboard if possible.

## Capabilities
- `reliable-reminder-logic`: Replacing windows with thresholds.
- `notification-logging`: DB tracking for all attempts.
- `retry-mechanism`: Automatic handling of network flakiness.
- `status-synchronization`: Atomic updates to the appointment flags.

## Impact
- **Impacts**: `src/application/scheduler.py`, `src/infrastructure/services/zapi.py`, `src/domain/models.py`.
