# Proposal: Validation of Flows and Dashboards

## Goal
Establish a comprehensive validation suite for the POST Clinics MVP, covering the end-to-end appointment flow (WhatsApp Agent -> API -> Database) and the Dashboard visualization.

## Motivation
The current MVP has basic verification scripts (`verify_flows.py`), but we need a robust "to-do" list of tests and a structured validation process to ensure:
1.  Agent reliably schedules, confirms, and checks slots.
2.  API correctly handles Webhooks and Dashboard requests.
3.  Dashboard accurately reflects the state of the database (calendar syncing).
4.  No-show reduction logic (reminders) is testable.

## Proposed Capabilities
- **Enhanced Verification Script**: Expand `verify_flows.py` to cover edge cases (collision, invalid dates).
- **Dashboard Testing**: Manual or automated checklist for UI actions (Create Appointment, View Details).
- **End-to-End Flow**: Verify that an appointment created via Agent appears on Dashboard, and vice-versa.

## Success Criteria
- [ ] `verify_flows.py` runs with exit code 0 and covers >90% of backend flows.
- [ ] Documented manual test plan for Dashboard.
- [ ] Confirmed bidirectional sync between Agent and Dashboard.
