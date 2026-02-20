## 1. Environment & Tools

- [x] 1.1 Create `tests/test_data_seeder.py` to create specific database states.
- [x] 1.2 Update `verify_flows.py` to use `argparse` and support modular execution.

## 2. Backend Verification

- [x] 2.1 Implement `test_availability(date)` in `verify_flows.py`.
- [x] 2.2 Implement `test_collision(date, time)` (requires seeder).
- [x] 2.3 Implement `test_invalid_date()`.
- [x] 2.4 Implement `test_dashboard_api()` (GET /api/appointments).

## 3. Dashboard Validation Plan

- [x] 3.1 Create `dashboard_test_plan.md` with manual steps for UI verification.
- [x] 3.2 Add instructions for End-to-End verification (Agent -> DB -> Dashboard).
