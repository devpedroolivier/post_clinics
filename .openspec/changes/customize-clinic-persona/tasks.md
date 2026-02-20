# Tasks: Customize Clinic Persona

## Implementation Checklist

- [ ] **Data Layer**
    - [ ] Create `src/config.py` with `CLINIC_CONFIG` mock data.

- [ ] **Agent Layer (`src/agent.py`)**
    - [ ] Implement `get_agent_instructions(config)` function.
    - [ ] Update `INSTRUCTIONS` generation logic.
    - [ ] Reconfigure `agent` instance to use dynamic instructions.

- [ ] **Tools Layer (`src/tools.py`)**
    - [ ] Update `check_availability` to respect `CLINIC_CONFIG` opening hours (simple check).
    - [ ] (Optional) Make tools aware of service duration.

- [ ] **Verification**
    - [ ] Verify Agent greeting (Identity).
    - [ ] Verify Service listing awareness.
    - [ ] Verify Outside-of-hours rejection.
