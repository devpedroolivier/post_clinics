# Design: Dashboard UX Polish

## Context
The current dashboard is functional but basic. The "POST" brand demands a "Quiet Luxury" aesthetic which implies high-quality interactions and information density without clutter.

## Goals
- **Information Hierarchy**: Critical numbers (KPIs) -> Visual Schedule (Calendar) -> Actions.
- **Interactivity**: Hover effects, smooth transitions, click-to-view.
- **Feedback**: System status should be visible (loading, success, error) without blocking user flow.

## UI Decisions
- **Layout**: CSS Grid with Sidebar (fixed left) and Main Content (scrollable).
- **KPI Cards**: 3-4 cards at top of Main Content.
    - *Total*: Clean number.
    - *Confirmed*: Green accent.
    - *Today*: Highlight.
- **Event Modal**: Re-use the existing Modal style but for "View Mode" (Read-only initially).
- **Toasts**: Fixed position bottom-right, stacking, auto-dismiss.

## Tech Implementation
- **KPIs**: Computed in `main.ts` from the `appointments` array after fetch.
- **Toasts**: Simple `showToast(message, type)` function appending to a container.
- **Sidebar**: Static HTML structure update.
