<artifact id="tasks" change="agent-performance-improvements">

## 1. Implement Async Webhook Processing
- [ ] 1.1 Extract the core agent interaction (`Runner.run`, tool loops, and `send_message`) from `receiver` into a new async function `process_webhook_payload`.
- [ ] 1.2 Inject `BackgroundTasks` from FastAPI into the `/webhook/zapi` endpoint.
- [ ] 1.3 Update the endpoint to enqueue `process_webhook_payload` and immediately return HTTP 200 with `{"status": "queued"}`.

## 2. Implement Safe Debounce per Phone
- [ ] 2.1 Create a mechanism (`asyncio.Lock` per phone in a global dictionary) to prevent parallel processing of messages from the same user.
- [ ] 2.2 Acquire the lock inside `process_webhook_payload` before invoking the LLM workflow to ensure sequential reasoning.

## 3. Testing and Deployment
- [ ] 3.1 Create a local script `scripts/test_async_webhook.py` to fire consecutive mock webhooks and assert that the HTTP endpoint returns <100ms.
- [ ] 3.2 Verify logs to confirm the Agent processes the sequence accurately behind the lock.

</artifact>
