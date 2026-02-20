# Design: Validation Framework

## Overview
We will implement a structured validation framework consisting of:
1.  **Backend Verification Script**: An enhanced `verify_flows.py` that handles CLI arguments to run specific scenarios.
2.  **Dashboard Verification Checklist**: A documented manual testing procedure (Markdown file) for UI interactions.
3.  **End-to-End Test Data**: A script to seed the database with known states (e.g., specific date with full slots) to test constraints.

## Technical Architecture

### 1. `verify_flows.py` Enhancements
- **Current**: Single monolithic script.
- **New**: Modular functions using `argparse`.
    - `test_availability(date)`
    - `test_collision(date, time)`
    - `test_invalid_date()`
    - `test_dashboard_api()`: Calls `/api/appointments` and verifies JSON structure.

### 2. Dashboard Validation
- Since we don't have Selenium/Playwright set up in this environment yet, we will define a **Manual Test Plan** (`dashboard_test_plan.md`).
- This plan will guide the user to:
    - Open Dashboard.
    - Create Appointment via UI.
    - Check if it appears in `verify_flows.py` output (API).

## File Changes
- **MODIFY** `verify_flows.py`: Add modular tests.
- **NEW** `tests/test_data_seeder.py`: Helper to inject data directly into SQLite for testing specific states.
- **NEW** `dashboard_test_plan.md`: Manual checklist.

## Constraints
- No new heavy dependencies (Keep it simple with `requests` and standard lib).
- Dashboard testing is manual for now.
