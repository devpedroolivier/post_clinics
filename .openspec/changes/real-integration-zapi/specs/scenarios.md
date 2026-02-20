# Scenarios: Real Integration Z-API

## Scenario A: Real Webhook Payload
**Given** a POST request from Z-API
**And** the payload structure matches the `on-message-received` event (nested `phone`, `text`, `messageId`)
**When** the server processes the request
**Then** it must correctly extract the phone number `5511...` and the message text.
**And** ignore messages if `isGroup: true` or `fromMe: true` (optional but good practice).

## Scenario B: Real Agent Execution
**Given** the Agent is initialized with `model="gpt-4o"`
**When** `Runner.run()` is called with the extracted text
**Then** it should communicate with OpenAI API (requires `OPENAI_API_KEY` in environment).
**And** maintain state in `SQLiteSession`.

## Scenario C: Tool Execution
**Given** the Agent decides to schedule an appointment
**When** it calls `schedule_appointment`
**Then** the real SQLite database should be updated.
