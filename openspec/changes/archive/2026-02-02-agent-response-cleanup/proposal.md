# Proposal: Agent Response Cleanup

## Goal
Ensure messages sent to WhatsApp are clean, natural, and free of system artifacts, thought chains, or formatting errors.

## Context
The user reports that the agent is sending messages "with system things". This usually happens when the LLM outputs its chain-of-thought (CoT), tool arguments, or XML tags into the final response channel.

## Solution
1. **Prompt Engineering**: Update the System Prompt to strictly forbid internal monologues in the final output.
2. **Output Guardrail**: Implement a cleaning function in the middleware (`src/main.py`) to strip known artifacts (e.g., `<thought>`, `Function Call:`, JSON blocks).
