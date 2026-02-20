# Proposal: Mobile Responsiveness

## Goal
Make the dashboard usable on mobile devices (smartphones/tablets).

## Motivation
The current layout is hardcoded for desktop (`grid-template-columns: 260px 1fr`). On mobile, this breaks the UI, making it impossible to view proper data or navigate.

## Capabilities
### Capabilities Affected
- **Dashboard Layout**: Will adapt to screen size.
- **Navigation**: Sidebar will become a hidden menu or simplified header on mobile.
- **Calendar**: Will adjust view mode (automatically switch to List view on mobile).

## Success Criteria
1.  **Sidebar**: Hidden by default on mobile, accessible via Hamburger menu.
2.  **Layout**: Stacks vertically (1 column) on screens < 768px.
3.  **Calendar**: Renders in `listWeek` or `timeGridDay` on mobile for better readability.
4.  **Forms**: Modal windows fit within the screen width.
