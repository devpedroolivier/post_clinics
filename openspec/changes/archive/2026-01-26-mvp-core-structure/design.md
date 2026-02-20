# Design: MVP Core Structure

## Architecture
The system follows a layered architecture with FastAPI as the entry point, OpenAI Agents SDK for logic/state, and SQLite for persistence.

### Components
1.  **FastAPI Server (`src/main.py`)**:
    *   Exposes `POST /webhook/zapi`.
    *   Instantiates the Agent Runner.
    *   Handles asynchronous request processing.

2.  **Agent Layer (`src/agent.py`)**:
    *   Defines `NoShowReceptionist` agent.
    *   Persona: "Efficient Medical Secretary".
    *   Manages context via `SQLiteSession`.

3.  **Tools Layer (`src/tools.py`)**:
    *   `@function_tool` definitions.
    *   Interfaces between Agent and Database.
    *   Functions: `check_availability`, `confirm_appointment`.

4.  **Data Layer (`src/database.py`)**:
    *   SQLite database `noshow.db`.
    *   SQLAlchemy/SQLModel for ORM.
    *   Tables: `patients`, `appointments`.

## Directory Structure
```
src/
├── main.py         # Entry point, Webhook
├── agent.py        # Agent definition, Runner Config
├── tools.py        # Agent Tools
└── database.py     # DB Connection & Models
```

## Data Flow
1.  Z-API sends Webhook -> `main.py`
2.  `main.py` extracts text -> Calls `Runner.run(agent, input)`
3.  `agent.py` processes intent -> DECIDES tool call
4.  `tools.py` executes logic -> Accesses `database.py`
5.  `tools.py` returns result -> `agent.py` generates response
6.  `main.py` returns response to Z-API (or triggers async send).
