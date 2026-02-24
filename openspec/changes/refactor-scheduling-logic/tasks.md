# Tasks: Scheduling Logic Refactor

## Phase 1: Database & Domain Models
- [ ] **Update Appointment Model**: Add `professional: str` field to `Appointment` in `src/domain/models.py`.
- [ ] **Migration Script**: Create and run a migration script (or update `src/migrate_db.py`) to add the `professional` column to existing SQLite database.
- [ ] **Update Schemas**: Update `AppointmentCreate` and `AppointmentUpdate` in `src/domain/schemas.py` to include the `professional` field.

## Phase 2: Core Scheduling Engine (`src/application/tools.py`)
- [ ] **Refactor `_check_availability`**:
    - [ ] Implement service-to-professional mapping logic based on `CLINIC_CONFIG`.
    - [ ] Change slot generation from dynamic gaps to a strict 45-minute grid.
    - [ ] Filter available slots by checking existing appointments for the *specific professional*.
    - [ ] Implement the "5 options" rule (balancing morning and afternoon).
- [ ] **Refactor `_schedule_appointment`**:
    - [ ] Add `professional` parameter.
    - [ ] Implement strict collision check (ensure the 45-min block is entirely free for that professional).
    - [ ] Use a database transaction to prevent race conditions.
- [ ] **Update Other Tools**: Update `_reschedule_appointment` to respect the new 45-min grid and professional constraints.

## Phase 3: AI Agent Behavior (`src/application/agent.py`)
- [ ] **Clean Prompt**: Update `get_agent_instructions` to explicitly ban emojis.
- [ ] **Tone Update**: Refine instructions for a more formal, clinical, and direct tone.
- [ ] **Human Fallback**: Add logic to the system prompt to offer "Falar com atendente" in complex or failing scenarios.
- [ ] **Tool Call Updates**: Update the example tool calls and instructions to include the `professional` parameter where applicable (or ensure it's derived correctly).

## Phase 4: Backend API (`src/api/routes/appointments.py`)
- [ ] **Update GET `/api/appointments`**: Ensure the `professional` field is returned to the frontend.
- [ ] **Update POST/PUT Routes**: Handle the `professional` field in creation and updates.
- [ ] **Concurrency Logic**: Ensure manual dashboard bookings also respect the new strict grid and professional constraints.

## Phase 5: Frontend Dashboard (`dashboard/src/pages/Dashboard.tsx`)
- [ ] **FullCalendar Views**: Add `timeGridDay` and `listMonth` (or similar) to `headerToolbar`.
- [ ] **Event Rendering**: Update `renderEventContent` to display the professional's name/label.
- [ ] **Color Coding**: Implement professional-based color coding for calendar events.
- [ ] **Form Update**: Add a "Professional" select field to the "Nova Consulta" and "Editar" modals.

## Phase 6: Testing & Validation
- [ ] **Unit Tests**: Create tests for the 45-min grid generation in `tests/test_scheduling.py`.
- [ ] **Concurrency Test**: Create a script to simulate dual-booking attempts (Race Condition).
- [ ] **End-to-End Test**: Verify the AI agent flow (no emojis + professional slots) using `scripts/test_agent_live.sh`.
