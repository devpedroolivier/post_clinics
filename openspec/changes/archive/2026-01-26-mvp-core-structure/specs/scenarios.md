# Scenarios: MVP Core Structure

## Scenario A: Webhook Receipt
**Given** the FastAPI server is running
**When** a POST request is received at `/webhook/zapi` with a Z-API payload containing a text message
**Then** the system should validate the payload
**And** extract the sender's phone number and message content
**And** forward this input to the Agent for processing.

## Scenario B: Agent Scheduling Logic
**Given** the Agent receives a user message
**When** the intention is identified as "agendar" (schedule)
**Then** the Agent should invoke the `check_availability` tool to find open slots.
**When** the intention is identified as "confirmar" (confirm)
**Then** the Agent should invoke the `confirm_appointment` tool.
**And** the Agent should maintain conversation context using `SQLiteSession`.

## Scenario C: Persistence
**Given** the Agent or Tools generate new data (e.g., a new patient or appointment)
**When** the transaction is committed
**Then** the data must be persisted in the local SQLite database `noshow.db`.
**And** the `patients` table should store name and phone.
**And** the `appointments` table should store timestamp, patient_id, and status.
