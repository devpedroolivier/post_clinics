## 1. Setup and Persistence

- [x] 1.1 Update webhook or session storage logic to persist handoff state indefinitely until human closure.
- [x] 1.2 Modify `request_human_attendant` function handling to enforce the new persistent handoff.

## 2. Session Lifecycle

- [x] 2.1 Implement inactivity timeout logic (30 mins) in the webhook/session manager to close inactive sessions.
- [x] 2.2 Add logic to handle new messages from inactive/closed sessions by creating a new session (reactivation).

## 3. Patient Feedback & Learning

- [x] 3.1 Update the assistant's system prompt to explicitly ask for feedback (1 to 5) after successfully scheduling an appointment.
- [x] 3.2 Enhance `learning_loop.py` (or equivalent) to extract post-appointment feedback messages and inject them into the agent's context.

## 4. Testing & Validation

- [x] 4.1 Write/update tests to verify handoff persistence.
- [x] 4.2 Write/update tests for the session timeout and reactivation logic.
- [x] 4.3 Write/update tests verifying the feedback prompt and learning loop extraction.