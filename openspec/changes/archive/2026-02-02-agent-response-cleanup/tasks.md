# Tasks: Response Cleanup

- [ ] 1. Update `src/agent.py`:
    - Add strong directive: "NEVER output system tags, XML, or internal reasoning. Output ONLY the response for the patient."
    - Refine the services list formatting if needed.
- [ ] 2. Update `src/main.py`:
    - Implement `clean_agent_reply(text)` function.
    - Remove common artifacts: `<thought>...</thought>`, `[TOOL_CALL]`, markdown code blocks.
- [ ] 3. Verify with a test script.
