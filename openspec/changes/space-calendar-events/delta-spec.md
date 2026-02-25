# Objective
Increase the visual spacing between overlapping events in the FullCalendar day/week views to ensure readability and a less "squished" appearance.

# Context
Currently, overlapping events in the day or week view stretch horizontally to fill the time slot, but when multiple events overlap, they compress into slim vertical strips. The user requested to separate them more.

# Modifications
1.  **Dashboard.tsx (FullCalendar Options)**:
    - Set `slotEventOverlap={false}`. This strictly prevents events from visually stacking on top of each other slightly, forcing them into distinct side-by-side columns with natural gaps.
    - Set `eventMaxStack={2}` (or an appropriate limit) if we need to control heavy overlap, but disabling slot overlap is the primary fix.
    - Introduce a slight margin in `renderEventContent` via CSS classes (e.g., `mr-1`) to ensure there is always a tiny pixel gap between the colored backgrounds even when they are positioned side-by-side by the calendar calculating engine.
