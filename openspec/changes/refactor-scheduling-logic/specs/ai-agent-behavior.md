# AI Agent Behavior

## User Stories

* **As a** patient
* **I want** clear, professional text without emojis
* **So that** the clinic feels serious and reliable.

* **As a** patient with a complex problem
* **I want** an easy way to talk to a human
* **So that** I am not stuck talking to a bot.

## CHANGED Requirements

### Requirement: Tone and Style
The system prompt MUST explicitly ban the use of emojis by the AI model. The tone MUST be professional, clinical, and direct.

## NEW Requirements

### Requirement: Human Fallback
The system prompt MUST instruct the AI to offer "Falar com atendente" if the user has a complex doubt, requests a human, or if scheduling fails repeatedly.

### Requirement: Robust Intent Parsing
The webhook middleware `preprocess_intent` MUST use Regex patterns or substring matching instead of exact string matches to reliably detect implicit confirmation/cancellation intents even when accompanied by greetings or punctuation (e.g., "Boa tarde, Sim" or "Sim.").

### Requirement: Anti-Loop Confirmations
The AI system prompt MUST explicitly handle situations where users greet alongside confirming an appointment, prioritizing the explicit intent (Confirm/Reschedule/Cancel) over the greeting. Once a confirmation is handled, the AI MUST NOT offer to schedule further services continuously to prevent loop states.

## Scenarios

### Scenario: Normal scheduling conversation
- **GIVEN** the user asks to schedule
- **WHEN** the AI replies
- **THEN** the text contains zero emojis and is formatted cleanly with markdown.

### Scenario: User is confused
- **GIVEN** the user asks a medical question the AI cannot answer safely
- **WHEN** the AI replies
- **THEN** it politely explains its limitations and explicitly offers scheduling an appointment or "Falar com um atendente" to transfer routing.
