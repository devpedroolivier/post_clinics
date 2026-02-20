# Design: Real Integration Z-API

## Components

### 1. Dependencies
- Add `openai-agents` to `requirements.txt`.
- Add `python-multipart` to `requirements.txt`.
- Remove `openai_agents` mock directory.

### 2. API Layer (`src/main.py`)
- Use Pydantic models to validate Z-API Payload:
    ```python
    class ZApiText(BaseModel):
        message: str

    class ZApiPayload(BaseModel):
        phone: str
        text: ZApiText
        messageId: str
    ```
- Endpoint should accept arguments matching this structure or parse raw JSON if dynamic.

### 3. Agent Layer (`src/agent.py`)
- **Import Change**: `from agents import Agent, Runner` (based on user instruction) OR `from openai_agents import ...` if package name differs. *Plan: Check package contents but default to `agents` namespace as requested.*
- **Model**: Set `model="gpt-4o"`.
- **Persona**: Ensure instructions clearly define "Recepção Clínica".

## Network
- Use `ngrok` to tunnel localhost:8000 to the internet.
