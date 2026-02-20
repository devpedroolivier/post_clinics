---
artifact_type: proposal
---

# Change: Improve Agent Core Logic & Autonomy

## Problem Statement

The current agent implementation has critical limitations:
1. **Scheduling Logic**: `check_availability` uses fixed slots and ignores service duration, risking overbooking.
2. **Missing Tools**: The agent cannot cancel or reschedule appointments autonomously.
3. **Reactive Only**: No proactive reminders or notifications; the system only responds to user input.
4. **Stability Issues**: The Llama-3 model relies on a regex workaround for tool calling, which is fragile.

## Proposed Solution

Implement a robust core logic for the agent, including:
1. **Dynamic Availability**: A new logic that calculates slots based on service duration and existing appointments.
2. **Extended Toolset**: Add `cancel_appointment`, `reschedule_appointment`, and `get_services` tools.
3. **Scheduler System**: A background job to send reminders (24h and 3h before) via Z-API.
4. **Native Tool Calling**: Optimize the system prompt or migrate to a model/wrapper that supports native tool calling more reliably, removing the regex workaround.

## What Changes

### New Capabilities
- `agent-scheduling-logic`: Logic to calculate available slots dynamically based on service duration.
- `agent-tools-management`: New tools for modification (cancel/reschedule) and information (services).
- `agent-notifications`: Background scheduler for proactive messages (reminders).
- `agent-core-stability`: Improvements to the agent's tool execution reliability.

### Impact
- **Database**: No schema changes expected, but queries will become more complex.
- **Agent**: Significant update to `tools.py` and `agent.py`.
- **Infrastructure**: New `scheduler.py` script to run alongside the main app.
