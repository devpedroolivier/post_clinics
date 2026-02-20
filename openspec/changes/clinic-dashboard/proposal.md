# Proposal: Clinic Dashboard

## Goal
Create an intelligent frontend dashboard for clinic staff to visualize managed appointments, calendar events, and trigger automated reminders.

## Capabilities

### New Capabilities
- `dashboard-calendar`: Integrated calendar view showing all scheduled appointments from the database.
- `real-time-updates`: Automated refresh or WebSocket connection to show new appointments as soon as the AI agent schedules them.
- `reminder-workflow`: Integration with Z-API to trigger manual or automated reminders directly from the dashboard.

## Impact
- **Backend**: New API endpoints in `src/main.py` to fetch appointments and manage configuration.
- **Frontend**: A new React/Vite project in the `dashboard/` directory.
- **Database**: Potential minor schema updates or just read access to existing tables.
