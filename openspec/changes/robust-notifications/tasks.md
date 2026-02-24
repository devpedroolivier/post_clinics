# Tasks: Robust Notifications

## Phase 1: Database & Models
- [ ] **Add `NotificationLog` Model**: Create the model in `src/domain/models.py`.
- [ ] **Migration**: Update `src/migrate_db.py` to create the `notification_log` table.

## Phase 2: Enhanced Communication Service (`src/infrastructure/services/zapi.py`)
- [ ] **Refactor `send_message`**: Return a structured response object (success, code, body).
- [ ] **Implement Retry Logic**: Add a retry decorator or loop with backoff.

## Phase 3: Robust Scheduler Refactor (`src/application/scheduler.py`)
- [ ] **Update Logic**: Replace window-based checks with "threshold + flag" logic.
- [ ] **Logging Integration**: Ensure every attempt is recorded in `NotificationLog`.
- [ ] **Timezone Hardening**: Use `BR_TZ` consistently and verify naive-to-aware comparisons.
- [ ] **Late Booking Protection**: Add logic to skip 24h reminders for late bookings.

## Phase 4: Observability & Refinement
- [ ] **Improved Logging**: Add structured logging for clearer failure tracing.
- [ ] **Error Handling**: Gracefully handle database locks during concurrent commits.

## Phase 5: Testing & Validation
- [ ] **Unit Tests**: Create `tests/test_notifications.py`.
- [ ] **Mock Z-API**: Simulate 200, 400, and 500 responses to verify logging and retry logic.
- [ ] **Time Jump Test**: Use a mock time to simulate scheduler recovery after downtime.
- [ ] **Late Booking Test**: Verify that 24h reminders are skipped for short-notice appointments.
