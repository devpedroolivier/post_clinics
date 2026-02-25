# Objective
Improve the UI of the FullCalendar specifically for the month, week, and day views. In the month view, limit the displayed events to a maximum of 3. In the week and day views, enhance the clarity, padding, and text contrast of the events to prevent text from being squished or unreadable.
 
# Context
Currently, the `renderEventContent` custom component is optimized for the month view with restricted height and `justify-center`. In `timeGrid` views (day and week), this causes the text to be squished towards the center of a tall event block. The month view currently displays up to 4 events before showing "+X more", and the user requested strictly 3.
 
# Modifications
1.  **Month View Limit**: Change `dayMaxEvents` from 4 to 3 in `Dashboard.tsx`.
2.  **Responsive Event UI**: Modify `renderEventContent` in `Dashboard.tsx` to detect the current view type. 
    - If `dayGridMonth`, keep a compact, minimal horizontal layout.
    - If `timeGridWeek` or `timeGridDay`, provide a spacious, top-aligned vertical layout with larger typography and cleaner spacing so the patient name, time, and professional are easy to read.
3.  **Color Enhancements**: Ensure the pastel event backgrounds look modern with deeper text colors for accessibility.
