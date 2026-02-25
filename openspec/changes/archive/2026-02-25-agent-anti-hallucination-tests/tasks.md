## 1. Context Injection Middleware

- [x] 1.1 Create the Context Injection service/module
- [x] 1.2 Implement logic to fetch context documents related to user prompts
- [x] 1.3 Implement token filtering/sizing logic to respect context limits
- [x] 1.4 Integrate the Context Injection service into the main agent message pipeline

## 2. Agent Core Updates

- [x] 2.1 Update the agent's baseline system prompt to enforce strict context boundaries
- [x] 2.2 Add instructions for the agent to explicitly state "I don't know" or ask for clarification when context is missing

## 3. Anti-Hallucination Test Suite

- [x] 3.1 Setup testing environment for agent conversational workflows (e.g., using pytest or jest)
- [x] 3.2 Create test fixtures with out-of-scope and ambiguous prompts
- [x] 3.3 Implement assertions to verify the agent refuses to hallucinate and correctly reports lack of knowledge
- [x] 3.4 Configure the CI/CD pipeline to run the anti-hallucination tests and generate reports
