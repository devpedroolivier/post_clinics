# Tasks: Real Integration Z-API

## Implementation Checklist

- [ ] **Dependency Management**
    - [ ] Update `requirements.txt`: Add `openai-agents`, `python-multipart`.
    - [ ] Install new dependencies.
    - [ ] Delete `openai_agents/` mock directory.

- [ ] **Agent Refactoring (`src/agent.py`)**
    - [ ] Update imports to real SDK (e.g. `from agents import ...`).
    - [ ] Configure `Agent` with `model='gpt-4o'`.
    - [ ] Refine system instructions (Persona).

- [ ] **API Refactoring (`src/main.py`)**
    - [ ] Define Pydantic models for Z-API payload (`phone`, `text.message`, `messageId`).
    - [ ] Update `receiver` endpoint to use Pydantic validation (or manual extraction robustness).
    - [ ] Ensure `messageId` is logged/handled.

- [ ] **Tunnel Setup (Manual)**
    - [ ] User must run: `ngrok http 8000`.
    - [ ] User must register URL in Z-API.

- [ ] **Verification**
    - [ ] Start Uvicorn.
    - [ ] Simulate Real Z-API payload via Curl/Postman.
    - [ ] Verify logs and DB.
