# Design System Extraction & Calendar Planning

## Goal Description
The objective is to refactor the current clinic dashboard to emulate the modern, minimalist aesthetic of the provided "Doctor Calendar" and the reference link (`context7.com`). We will adopt a sleek, content-first black-and-white theme, applying this logic to our FullCalendar implementation and surrounding UI elements.

## Core UX/UI Principles (Minimalist Black & White)
1.  **Typography**: Strong emphasis on contrast. Use heavy sans-serif fonts for headings and clear, legible weights for dates and events.
2.  **Color Palette**:
    *   **Backgrounds**: Pure white (`#ffffff`) or very light grays (`#f8f9fa`) for subtle separation.
    *   **Text**: Deep black (`#111827` or `#000000`) for primary text, medium gray (`#6b7280`) for secondary text.
    *   **Accents**: Instead of a rainbow of colors for events, use shades of gray, black borders, or subtle, desaturated pastels ONLY when absolutely necessary for distinguishing states (e.g., a very faint green for confirmed, light gray for pending). The preference is a monochrome scheme using borders and opacity.
3.  **Layout & Spacing**: Generous padding. Elements should feel breathable. Remove heavy borders; prefer dividers or whitespace to separate sections.
4.  **Calendar Specifics (FullCalendar)**:
    *   Remove standard grid lines or make them extremely faint.
    *   Events should look like solid, rounded blocks (cards) with clear typography inside.
    *   The "Today" indicator should be a bold, simple accent (e.g., a solid black circle with white text for the date number).
    *   Clean, minimalist toolbar (Prev, Next, Today, Views).

## User Review Required
> [!IMPORTANT]
> **Constraint Check**: The prompt requests keeping a "black and white" version but also "highlighting the calendar according to the logic of our project".
> **Proposed Logic for Events**:
> - **Default/Pending**: White background, delicate black or gray border, black text.
> - **Confirmed**: Very soft, desaturated accent colors (matching the reference image's pastel vibe, e.g., extremely light blue, green, or pink) to differentiate professionals or services, OR stick to a strict monochrome palette (light gray bg vs white bg).
>
> *I will proceed with a strictly minimalist, high-contrast monochrome base, using extremely subtle pastel indicators ONLY for distinguishing the 3 professionals/services to maintain usability without breaking the minimalist aesthetic.*

## Proposed Changes

### Configuration
#### [MODIFY] tailwind.config.js
Update the color palette to enforce the new minimalist constraints if necessary, ensuring we have the right shades of gray and stark black/white available.

### Frontend Components
#### [MODIFY] src/style.css
- Restyle `.fc` (FullCalendar) classes entirely.
- Remove default borders on `.fc-theme-standard td`, `.fc-theme-standard th`.
- Style the header toolbar to match the modern, clean look (round buttons, bold text).
- Style `.fc-event` to look like the reference: rounded corners, clean padding, specific font weights.
- Implement the bold "Today" circle indicator (`.fc-day-today`).

#### [MODIFY] src/pages/Dashboard.tsx
- Update the `events` mapping logic to use the new minimalist color scheme.
- Refactor the `renderEventContent` custom view to display event details (time, patient name, professional) cleanly within the new monochrome constraints.
- Clean up the main dashboard container, sidebar, and KPI cards to match the new stark aesthetic (removing unnecessary shadows or borders, relying on spacing).
- Update modal styles to match the minimalist theme (black/white contrast).

## Verification Plan
### Automated & Manual Verification
- Render the dashboard using `npm run dev` and visually inspect the calendar layout.
- Verify that standard contrast rules (black text on light gray/white) are maintained.
- Ensure the event rendering distinguishes professionals clearly while adhering to the minimalist style.
- Test responsiveness on smaller viewports.
