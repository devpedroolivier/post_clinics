# Proposal: Real Integration Z-API

## Change Description
Upgrade the NoShowAI MVP from a mock environment to a production-ready integration using the real `openai-agents` SDK and live Z-API webhooks.

## Why
To enable actual communication with patients via WhatsApp. Mocks are sufficient for structural testing, but real dependencies are required for the pilot.

## Objectives
- Replace mock SDK with real `openai-agents` library (importing from `agents` package).
- Configure Agent with `gpt-4o` model.
- Implement robust Z-API payload parsing (nested `text.message` structure).
- Enable public access tunnel (ngrok) for webhook reception.
