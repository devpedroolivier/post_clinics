# Design: Validation Strategy for Appointment Flows

## Overview
This design outlines the strategy to validate the appointment scheduling, confirmation, rescheduling, and cancellation flows. We will implement a dedicated verification suite `verify_flows.py` that simulates external events (Z-API webhooks) and inspects the internal state (SQLite database) to assert correctness.

## Test Strategy

### 1. Unified Test Driver (`verify_flows.py`)
We will create a Python script that acts as an integration test runner.
*   **Requests**: It will send HTTP POST requests to `http://localhost:8000/webhook/zapi` simulating user messages.
*   **State Inspection**: It will connect directly to `post_clinics.db` and `conversations.db` to verify that:
    *   Appointments are created/updated with correct status.
    *   Agent memory reflects the conversation.
    *   Patients are correctly registered.

### 2. Test Scenarios

#### Scenario A: Happy Path (New Patient -> Schedule -> Confirm)
1.  **Input**: "Olá, gostaria de agendar uma consulta para amanhã às 14h."
2.  **Expected Agent**: Asks for name (if new) or confirmation.
3.  **Input**: "Meu nome é Pedro."
4.  **Expected Agent**: Confirms pending appointment.
5.  **Input**: "Sim, confirmado."
6.  **Expected DB State**: `Appointment` record exists, status=`scheduled` (or `confirmed` depending on logic), `Patient` record exists.
7.  **Dashboard Check**: API `/api/appointments` returns this appointment.

#### Scenario B: Reschedule
1.  **Prerequisite**: Existing appointment from Scenario A.
2.  **Input**: "Preciso remarcar para 16h."
3.  **Expected Agent**: Proposes change.
4.  **Input**: "Pode ser."
5.  **Expected DB State**: Appointment datetime updated.

#### Scenario C: Cancellation
1.  **Input**: "Quero cancelar minha consulta."
2.  **Expected Agent**: Asks for confirmation.
3.  **Input**: "Sim, pode cancelar."
4.  **Expected DB State**: Appointment status=`cancelled`.

#### Scenario D: Dashboard Integration
1.  **Action**: Call POST `/api/appointments` (simulating Dashboard Manual Create).
2.  **Validation**: Verify DB has new appointment.
3.  **Cross-Check**: Verify Agent "knows" about this slot (if free-busy is implemented) or at least doesn't overwrite it.

## Verification Tools
*   `httpx`: For sending webhook requests.
*   `sqlmodel`: For reading the DB state.
*   `logging`: Detailed output of steps for the walkthrough artifact.

## Reminder Workflow Validation
*   We will simulate the "time passing" or trigger the reminder function directly if it's a background task, to ensure it filters for `confirmed` appointments.
