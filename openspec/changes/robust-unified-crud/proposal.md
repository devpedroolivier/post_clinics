# Proposal: Robust Unified Appointment CRUD

## Goal
Unify the scheduling logic between the Dashboard API and the AI Agent tools to ensure consistency, prevent schedule conflicts, and simplify maintenance.

## Problem
- The API was creating appointments without checking for conflicts.
- Business logic (like fuzzy service matching and professional assignment) was duplicated between `tools.py` and `routes/appointments.py`.
- No automated tests existed for the full API CRUD cycle.

## Solution
1.  **New Service Layer**: Created `src/application/services/appointment_manager.py` to centralize all CRUD logic.
2.  **API Refactoring**: Updated `src/api/routes/appointments.py` to use the manager, adding conflict detection (409 Conflict).
3.  **Tool Refactoring**: Updated `src/application/tools.py` to use the manager, ensuring the AI and the Dashboard follow the same rules.
4.  **Testing**: Added `tests/test_appointments_crud.py` for full coverage of the API endpoints.

## Success Criteria
1.  API should reject overlapping appointments (unless forced).
2.  All tests (`test_smoke.py`, `test_scheduling.py`, and `test_appointments_crud.py`) pass.
3.  No code duplication for core scheduling rules.
