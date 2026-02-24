# Refactor Scheduling Logic

## Why
The current scheduling logic lacks strict concurrency control, multi-professional support, and deterministic time slots, which can lead to double-bookings or inefficient gap management. The WhatsApp AI agent also needs behavioral refinements to sound more professional (no emojis) and provide a clear human fallback ("Falar com atendente"). This refactor aims to make the scheduling engine robust, atomic, and scalable for multiple professionals with specific working hours.

## What Changes
1. **Multi-Professional Scheduling**: Appointments will be explicitly tied to a professional and a specific service label.
2. **Strict Time Slot Engine**: Implementation of deterministic 45-minute slots respecting individual professional hours and global clinic boundaries (09:00–18:00 block outside rules).
3. **Concurrency Prevention**: Database-level unique constraints (professional_id + datetime) combined with atomic transactions to guarantee zero double-bookings.
4. **Enhanced Cancellation Sync**: Robust status updates that reliably free up slots immediately upon cancellation.
5. **AI Behavioral Polish**: Prompt engineering to eliminate emojis and ensure a graceful fallback to human attendants.
6. **Frontend Enhancements**: Weekly/monthly calendar views to support the new multi-professional data structure.

## Capabilities

- `advanced-slot-generation`
- `transactional-booking-engine`
- `professional-management`
- `ai-agent-behavior`
- `frontend-calendar-views`

## Impact

### `advanced-slot-generation`
- **Impacts**: Backend schedule logic (`src/application/tools.py`), AI prompt constraints.

### `transactional-booking-engine`
- **Impacts**: Database schema (`Appointment` model), backend route handlers, scheduler.

### `professional-management`
- **Impacts**: Database schema (new `Professional` model or fields), backend configuration (`src/core/config.py`), dashboard UI (`Dashboard.tsx`).

### `ai-agent-behavior`
- **Impacts**: AI system prompts (`src/application/agent.py`).

### `frontend-calendar-views`
- **Impacts**: React dashboard components (`Dashboard.tsx`, FullCalendar integration).
