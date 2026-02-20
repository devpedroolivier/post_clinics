# Tasks: Dashboard V2

## 1. Backend (Manual Entry)
- [ ] 1.1 Create `POST /api/appointments` endpoint in `src/main.py`.
    - Accepts JSON: `{ name, phone, datetime, service }`.
    - Creates/Get `Patient` -> Creates `Appointment`.

## 2. Frontend (FullCalendar Integration)
- [ ] 2.1 Install `@fullcalendar/core`, `@fullcalendar/daygrid`, `@fullcalendar/timegrid`.
- [ ] 2.2 Replace custom grid implementation in `main.ts` with FullCalendar initialization.
- [ ] 2.3 Map API data to FullCalendar event format `{ title, start, allDay: false }`.

## 3. Frontend (Manual Entry Modal)
- [ ] 3.1 Create HTML structure for Modal (dialog element or custom div).
- [ ] 3.2 Implement "Nova Consulta" button in Header.
- [ ] 3.3 Implement Form Logic (submit -> `fetch POST` -> toast success -> refresh calendar).
