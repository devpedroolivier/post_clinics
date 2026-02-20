# Design: Customize Clinic Persona

## Components

### 1. Configuration (`src/config.py`) [NEW]
Define a dictionary `CLINIC_CONFIG` to act as the single source of truth for the clinic profile.
```python
CLINIC_CONFIG = {
    "name": "Espaço Interativo Reavilitare",
    "assistant_name": "Carol",
    "hours": "Segunda a Sexta: 09:00 às 17:30. Sábados (quinzenalmente): 09:00 às 13:00.",
CLINIC_CONFIG = {
    "name": "Espaço Interativo Reavilitare",
    "assistant_name": "Carol",
    "hours": "Segunda a Sexta: 09:00 às 17:30. Sábados (quinzenalmente): 09:00 às 13:00.",
    "services": [
        {"name": "Odontopediatria (1ª vez)", "duration": 60},
        {"name": "Odontopediatria (Retorno)", "duration": 40},
        {"name": "Pacientes Especiais (1ª vez)", "duration": 60},
        {"name": "Pacientes Especiais (Retorno)", "duration": 40},
        {"name": "Implante", "duration": 40},
        {"name": "Clínica Geral", "duration": 40},
        {"name": "Ortodontia", "duration": 40, "note": "Apenas dias 24 e 25 de Fev"}
    ],
    "cancellation_policy": "Cancelamentos devem ser feitos com 24h de antecedência.",
    "communication_flow": "Enviamos confirmação 1 dia antes e lembrete 3h antes da consulta."
}
```

### 2. Agent Factory (`src/agent.py`)
Refactor the module to export a function or use the config to build `agent`.
- **Function**: `get_agent_instructions(config: dict) -> str`
- **Logic**: Formats the prompt using f-strings, embedding the services list and rules.
- **Instantiation**: `agent` object now initialized *after* config is loaded or directly using the imported config.

### 3. Tools (`src/tools.py`)
- Import `CLINIC_CONFIG` to access hours/rules if needed.
- `check_availability`: (MVP Refinement) Ensure it generates slots consistent with `CLINIC_CONFIG['hours']`.

## Data Flow
`main.py` -> imports `agent` -> `agent` initialized with `CLINIC_CONFIG` instructions.
