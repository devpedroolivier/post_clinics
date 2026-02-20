# Tasks: MVP Core Structure

## Implementation Checklist

- [ ] **Setup Environment**
    - [ ] Create virtual environment (`venv`) inside the project root.
    - [ ] Install dependencies: `openai-agents`, `fastapi`, `uvicorn`, `sqlalchemy` (or `sqlmodel`).
    - [ ] Freeze requirements to `requirements.txt`.

- [ ] **Database Layer (`src/database.py`)**
    - [ ] Configure SQLite connection to `noshow.db`.
    - [ ] Define `Patient` model (id, name, phone, created_at).
    - [ ] Define `Appointment` model (id, patient_id, datetime, status, created_at).
    - [ ] Create script to initialize tables.

- [ ] **Tools Layer (`src/tools.py`)**
    - [ ] Implement `check_availability(date)` stub (mocked or DB query).
    - [ ] Implement `confirm_appointment(appointment_id)` stub.
    - [ ] Decorate functions with `@function_tool`.

- [ ] **Agent Layer (`src/agent.py`)**
    - [ ] Define `Agent(name="NoShowReceptionist")`.
    - [ ] Write system instructions for the Persona.
    - [ ] Register tools with the agent.
    - [ ] Configure `SQLiteSession` for conversation memory.

- [ ] **API Layer (`src/main.py`)**
    - [ ] Initialize FastAPI app.
    - [ ] Create `POST /webhook/zapi` endpoint.
    - [ ] Parse Z-API payload.
    - [ ] Call `await Runner.run(...)` with the incoming message.
    - [ ] Log response.

- [ ] **Verification**
    - [ ] Run `uvicorn src.main:app --reload`.
    - [ ] Use `curl` or Postman to send a comprehensive JSON payload to the webhook.
    - [ ] Verify that an entry acts on the DB (or logs show tool usage).
