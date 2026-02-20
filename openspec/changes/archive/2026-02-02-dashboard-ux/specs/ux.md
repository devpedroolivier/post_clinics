# Specs: Dashboard UX

### Requirement: KPI Summary
The dashboard displays key metrics based on current appointment data.
- **Metrics**:
    - **Total Agendamentos**: Count of all future active appointments.
    - **Hoje**: Count of appointments for the current date.
    - **Confirmados**: Percentage or count of status='confirmed'.

### Requirement: Toast Notifications
System feedback is distinct and non-blocking.
- **Scenario**: Successful Booking
    - **WHEN** a manual appointment is created.
    - **THEN** a green toast appears: "Agendamento criado com sucesso".
    - **AND** it disappears automatically after 3 seconds.

### Requirement: Layout Structure
- **Sidebar**: Permanent navigation rail on the left (250px width).
- **Header**: Search bar + User profile (simulation) + "Nova Consulta" button.
- **Content**: KPI Grid + Calendar.
