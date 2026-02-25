# Objective
Separate the "Dra. Débora / Dr. Sidney" professional grouping into distinct individuals ("Dra. Débora", "Dr. Sidney", "Dr. Ewerton") and visually distinguish them in the frontend calendar.
 
# Context
Currently, the system couples multiple professionals into a single string for scheduling ("Dra. Débora / Dr. Sidney"). The frontend calendar uses this single string in its filter dropdown and rendering logic. The user requested to separate these professionals and assign unique colors to each in the dashboard calendar.
 
# Modifications
1.  **Dashboard Dropdown**: Update `<select>` options in `Dashboard.tsx` to include "Dra. Débora", "Dr. Sidney", and "Dr. Ewerton".
2.  **Calendar Event Colors**: Update `renderEventContent` and the event generator in `Dashboard.tsx` to colorize events based on the assigned individual professional.
3.  **Backend Configuration**: Update `CLINIC_CONFIG` in `src/core/config.py` to separate the schedules for each doctor. 
