# Tasks: Improve Slot Selection Routing

- [x] Add date/time regex patterns to webhook scope classifier.
- [x] Ensure date/time-only messages are treated as supported scope.
- [x] Add regression test for `dia 5/3` + `15:15` flow.
- [ ] Add optional flow-state marker per phone (`awaiting_service/date/time/name/confirmation`) to reduce reliance on regex-only routing.
- [ ] Add telemetry counters for `false_handoff_prevented` and `slot_selection_detected` in webhook logs.
- [ ] Monitor production logs for 24h to confirm handoff false positives are reduced.
