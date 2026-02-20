# Proposal: Expose Local Server via Ngrok

## Goal
Enable public access to the local development environment using Ngrok, allowing Z-API webhooks to reach the application running in Docker.

## Motivation
The user needs to test the verified application with real Z-API webhooks or external integrations. Since the app is running locally (Docker on localhost:8000), it is not reachable by the internet. Ngrok bridges this gap.

## Capabilities
### Capabilities Affected
- **Deployment**: Adds a sidecar container or service to handle tunneling.

### New Capabilities
- **Public URL**: Automatically generating a secure (https) URL for the local app.
- **Webhook Handling**: Enabling real-time "live" testing.

## Success Criteria
1.  Running `docker-compose up` automatically starts Ngrok.
2.  A public URL is generated and logged.
3.  Z-API can successfully send a POST request to `<public_url>/webhook/zapi`.
