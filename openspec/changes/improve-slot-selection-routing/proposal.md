# Proposal: Improve Slot Selection Routing (Avoid False Human Handoff)

## Background
Recent production logs from **2026-02-26** show a regression in scheduling flow:
- After presenting available times, user replied only with a time (`15:15`).
- The webhook classified it as out-of-scope (`out_of_scope_attempt=2`) and routed to human attendant.

This interrupts a valid booking flow and increases manual workload.

## Problem Statement
The current scope detector relies mostly on keyword-based intent (`agendar`, `consulta`, etc.).
Short slot-selection replies (time/date only) do not contain these keywords and can be misclassified as out-of-scope.

## Goals
1. Treat time/date-only replies as valid scope during scheduling.
2. Prevent false escalation to human attendant in slot selection step.
3. Preserve existing safety handoff behavior for truly out-of-scope messages.
4. Add tests for date/time-only replies in webhook flow.

## Success Criteria
- Reply `dia 5/3` and `15:15` no longer increment out-of-scope attempts to escalation in scheduling flow.
- No regression in explicit handoff triggers (financial/urgency/complaints/human request).
- Test coverage includes slot-selection scope classification.
