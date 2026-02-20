---
artifact_type: tasks
---

# Tasks: Improve Agent Core Logic & Autonomy

## 1. Database Updates
- [x] 1.1 Add `notified_24h` and `notified_3h` boolean columns to `Appointment` model in `src/database.py`.
- [x] 1.2 Run migration script or recreate tables (if MVP allows drop) to apply changes.
- [x] 1.3 Verify DB schema with a test script.

## 2. Dynamic Scheduling Logic
- [x] 2.1 Refactor `check_availability` in `src/tools.py` to accept service duration (map from string to minutes).
- [x] 2.2 Implement logic to fetch all appointments for the day and find free gaps >= requested duration.
- [x] 2.3 Ensure `check_availability` returns smart suggestions (e.g., nearest valid slots).
- [x] 2.4 Verify `check_availability` with unit tests (mock DB).

## 3. Tool Implementation
- [x] 3.1 Implement `cancel_appointment(appointment_id)` in `src/tools.py`.
- [x] 3.2 Implement `reschedule_appointment(old_id, new_datetime)` in `src/tools.py`.
- [x] 3.3 Add `get_available_services()` tool to help agent know durations.
- [x] 3.4 Register new tools in `agent.py`.

## 4. Scheduler Service
- [x] 4.1 Create `src/scheduler.py` script.
- [x] 4.2 Implement loop to check DB for upcoming appointments (24h and 3h).
- [x] 4.3 Implement Z-API sending logic using `src/zapi.py`.
- [x] 4.4 Implement logic to update `notified_` flags after sending.
- [x] 4.5 Add `scheduler` service to `docker-compose.yml` and `docker-compose.prod.yml`.

## 5. Agent Stability
- [x] 5.1 Update `get_agent_instructions` in `src/agent.py` with explicit tool format instructions.
- [x] 5.2 Review `main.py` regex logic to ensure it captures the new format robustly.
- [x] 5.3 Test agent conversation flow to verify tool usage.

## 6. Verification
- [x] 6.1 Update `verify_flows.py` to include cancellation and rescheduling scenarios.
- [x] 6.2 Monitor scheduler output to verify reminders are sent (mock Z-API if needed).
