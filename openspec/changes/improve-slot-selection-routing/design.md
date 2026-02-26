# Design: Slot Selection Scope Guard

## Root Cause
`is_in_supported_scope()` classifies user text by keyword regex only. Numeric replies (date/time) miss keywords.

## Design Decision
1. Add explicit patterns to supported scope:
- `DATE_SELECTION_PATTERN`: `dia 5/3`, `05/03`, `05-03-2026`.
- `TIME_SELECTION_PATTERN`: `15:15`, `às 15:15`, `15h15`.

2. Keep explicit handoff detection unchanged:
- Human request, financial, urgency, complaint still route directly to attendant.

3. Keep out-of-scope fallback behavior unchanged for non-scheduling content.

## Trade-offs
- Slightly broader in-scope acceptance for numeric messages.
- Reduced false-positive handoff in actual scheduling flows.

## Observability
Continue monitoring these counters after rollout:
- `[SCOPE] out_of_scope_attempt=2`
- `[WPP:IN]` vs `[WPP:OUT]`
- `[HANDOFF]` rate during scheduling conversations
