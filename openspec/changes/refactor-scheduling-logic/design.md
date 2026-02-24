# Technical Design: Scheduling Refactor

## Context
POST Clinics currently uses a basic scheduling mechanism without strict concurrency control or multi-professional support. The AI agent generates dynamic gaps, leading to inconsistent slot sizes (e.g., 20-min vs 60-min slots) and potential overlaps if two users book simultaneously.

## Goals
- Enforce strict 45-minute slots (configurable but deterministic).
- Support specific working hours per professional (e.g., Orto vs. Clinica Geral).
- Guarantee zero double-booking via database constraints.
- Optimize the prompt so the AI acts formally (no emojis) and falls back to humans cleanly.

## Non-Goals
- Full integration with external generic calendar APIs (Google Calendar) is not in scope for this specific refactor (we use the internal DB).

## Architecture / Implementation

### 1. Database Schema (`src/domain/models.py`)
- We will add a `professional` string field (or foreign key) to the `Appointment` model.
- We will add a **composite unique constraint** on `(professional, datetime, status)` where status is active, but SQLite doesn't cleanly support partial indexes in SQLModel without raw SQL. Therefore, when an appointment is cancelled, we should either delete the row OR change the `datetime` to a null/past value to free the slot, OR manually enforce the check inside a transaction.
- **Decision**: We will enforce concurrency using a read-check-write within a strict `Session` transaction loop, and rely on the UI/API layers rejecting duplicates. Alternatively, we can use an explicit DB locking mechanism if needed, but `check-then-insert` in a single SQLModel transaction is sufficient for our scale if handled carefully.

### 2. Slot Generation (`src/application/tools.py`)
Rewrite `_generate_availability` to:
- Map each service to a professional profile (hours + duration).
- Orto: 08:00–11:30, 13:00–17:30.
- Dra Débora / Dr Sidney: 09:00–12:00, 14:30–18:00 (Sat 08:00–12:30).
- Generate deterministic blocks (e.g., 08:00, 08:45, 09:30).
- Query the database to subtract booked slots.
- Return the first 5 available (morning + afternoon) options.

### 3. AI Behavior (`src/application/agent.py`)
- Update `CLINIC_CONFIG` instructions.
- Explicit rule: "NUNCA use emojis. Mantenha um tom estritamente profissional e clínico."
- Explicit rule: "Se o paciente solicitar, ou se houver um problema complexo, forneça a opção 'Falar com atendente'."

### 4. Frontend Updates (`dashboard/src/pages/Dashboard.tsx`)
- Install/Use FullCalendar's week/month views (`dayGridMonth`, `timeGridWeek`).
- Color code events based on professional or service to make visual distinction easier.

## Risks / Trade-offs
- **Risk**: SQLite concurrent write locking (`database is locked`). **Mitigation**: Ensure WAL mode is enabled and transactions are kept extremely short (only the booking insert).
