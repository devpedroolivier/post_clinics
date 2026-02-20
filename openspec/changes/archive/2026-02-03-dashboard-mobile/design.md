# Design: Mobile Dashboard

## Strategy
We will use CSS Media Queries to adapt the layout without rewriting the HTML structure (Responsive Web Design).

### Breakpoints
- **Desktop**: > 768px (Existing layout)
- **Mobile**: <= 768px

### Layout Changes
1.  **Grid System (`#app`)**:
    - Change from `grid-template-columns: 260px 1fr` to `1fr` (Single column).
2.  **Sidebar**:
    - Default: `display: none`.
    - Active: `position: fixed`, `z-index: 1000`, full width/height or slide-in.
    - Trigger: Add a "Hamburger" button to `.header`.
3.  **KPI Row**:
    - `grid-template-columns: 1fr` (Stack cards vertically).
4.  **Calendar**:
    - Reduce height on mobile.
    - JavaScript logic to switch `initialView` based on window width.

## UI Components
- **Hamburger Button**: Added dynamically to `.header-actions` or left side of header via JS.
- **Close Sidebar Button**: Added to sidebar for mobile closing.

## Logic Changes
- **`main.ts`**:
    - Detect mobile on load -> set Calendar view to `listWeek`.
    - Add event listeners for Sidebar Toggle.
