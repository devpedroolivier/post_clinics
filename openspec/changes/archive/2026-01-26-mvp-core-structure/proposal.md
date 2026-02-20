# Proposal: MVP Core Structure for NoShowAI

## Change Description
Establish the backbone of the NoShowAI backend using Python FastAPI and OpenAI Agents SDK. This change covers the setup of the API server to receive Z-API webhooks, the configuration of the intelligent Agent, and the basic persistence layer with SQLite.

## Why
To validate the hypothesis that automating schedule confirmation via WhatsApp reduces no-shows. The goal is to have a functional MVP deployed in a pilot clinic within 30 days, capable of handling basic scheduling intents automatically.

## Objectives
- Create a FastAPI server with a webhook endpoint (`/webhook/zapi`).
- Implement the "NoShowReceptionist" Agent using `openai-agents`.
- Set up SQLite persistence for `patients` and `appointments`.
- Enable the end-to-end flow: Webhook -> Agent -> Tool -> Database.
