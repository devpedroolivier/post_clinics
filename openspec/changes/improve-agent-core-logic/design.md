---
artifact_type: design
---

# Design: Improve Agent Core Logic & Autonomy

## Context

Current implementation uses hardcoded time slots (09, 10, 11...) and ignores service duration. The agent cannot cancel or reschedule, and there are no reminders. The tool calling mechanism relies on a fragile regex parser for Llama-3.

## Goals / Non-Goals

**Goals:**
- Implement dynamic availability checking considering service duration (e.g., 40min vs 60min).
- Add capability for the agent to cancel and reschedule appointments.
- Implement a background scheduler for sending reminders 24h and 3h before.
- Improve robustness of tool calling parsing.

**Non-Goals:**
- Migration to PostgreSQL (keep SQLite for MVP simplicity).
- Switching LLM provider (keep Groq/Llama-3 for speed/cost).
- Building a complex UI for configuration (keep config in code/env).

## Decisions

### 1. Dynamic Scheduling Logic
- **Approach**: Fetch all appointments for a day, sort them. Generate potential start times (e.g., every 30 mins or aligned to service duration) and check if the duration fits without overlap.
- **Rationale**: Flexible and accurate. Avoids "block" logic which is too rigid.

### 2. Scheduler Service (`scheduler.py`)
- **Approach**: A standalone Python script running in a loop (e.g., every 10 mins). Checks DB for appointments matching notification criteria (24h or 3h before) and sends Z-API message. Marks appointment as `notified_24h` or `notified_3h` to avoid duplicates (requires DB schema update for flags).
- **Rationale**: Simple to deploy via Docker, decoupled from the main API process.
- **DB Update**: Add `notification_status` column or separate table. For MVP, adding columns `notified_24h` (bool) and `notified_3h` (bool) to `Appointment` model is sufficient.

### 3. Tool Calling Strategy
- **Approach**: Retain the regex workaround but refine the System Prompt to strictly enforce a specific output format like `[TOOL_CALL: name(args)]` to make parsing deterministic.
- **Rationale**: Llama-3 8B is powerful but inconsistent with JSON tool calling. XML/Tag based prompting is more reliable for this model size.

## Risks / Trade-offs

- **Risk**: Scheduler might double-send if process restarts or race conditions occur.
  - *Mitigation*: DB flags (`notified_24h`) should prevent this.
- **Trade-off**: Polling DB for availability is slightly slower than in-memory slots, but negligible for MVP scale.
