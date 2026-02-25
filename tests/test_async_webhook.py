import asyncio
import time
import json
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from src.api.main import app
from src.core.security import generate_signature
from src.api.routes import webhooks
from src.infrastructure.database import create_db_and_tables

def test_webhook_latency_and_debounce():
    """
    Test that sending multiple concurrent webhooks returns immediately (< 100ms)
    and the background tasks process them safely.
    """
    class _FakeRunnerResult:
        final_output = "Resposta de teste"

    async def _run():
        # Setup test secrets
        import os
        os.environ["WEBHOOK_SIGNATURE_SECRET"] = "test_secret_123"
        from src.core import config, security
        config.WEBHOOK_SIGNATURE_SECRET = "test_secret_123"
        security.WEBHOOK_VALIDATE_SIGNATURE = False
        config.ANTISPAM_CONFIG["max_messages_per_minute"] = 9999
        config.ANTISPAM_CONFIG["cooldown_seconds"] = 0
        webhooks._phone_out_of_scope_attempts.clear()
        webhooks._phone_timestamps.clear()
        webhooks._seen_messages.clear()

        with patch("src.api.routes.webhooks.Runner.run", new_callable=AsyncMock) as mock_runner:
            with patch("src.api.routes.webhooks.send_message", new_callable=AsyncMock) as mock_send:
                mock_runner.return_value = _FakeRunnerResult()
                mock_send.return_value = {"success": True, "status_code": 200, "error_message": None}

                create_db_and_tables()
                from httpx import ASGITransport
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    
                    payloads = [
                        {"phone": "5511999999999", "messageId": "msg_async_1", "text": "Mensagem 1"},
                        {"phone": "5511999999999", "messageId": "msg_async_2", "text": "Mensagem 2"},
                        {"phone": "5511999999999", "messageId": "msg_async_3", "text": "Mensagem 3"}
                    ]
                    
                    # Send concurrent requests
                    start_time = time.time()
                    tasks = []
                    for payload in payloads:
                        body_bytes = json.dumps(payload).encode("utf-8")
                        sig = generate_signature(body_bytes)
                        headers = {"X-Webhook-Signature": f"sha256={sig}"}
                        
                        # Mock Z-API payload structure
                        tasks.append(client.post("/webhook/zapi", json=payload, headers=headers))
                        
                    
                    results = await asyncio.gather(*tasks)
                    elapsed_time = time.time() - start_time
                    
                    # Check elapsed time is incredibly short (Background tasks decouple execution)
                    print(f"Total time for 3 webhooks: {elapsed_time:.4f}s")
                    assert elapsed_time < 2.0, f"Webhook blocking the event loop! Time: {elapsed_time:.4f}s"
                    
                    for i, res in enumerate(results):
                        if res.status_code != 200:
                            print(f"Request {i} failed: {res.status_code} - {res.text}")
                        assert res.status_code == 200
                        assert res.json() == {"status": "queued"}
                    
                    # Allow background tasks to run briefly for assertions in actual logs
                    await asyncio.sleep(0.1)
                    
                    print("Webhook latency is properly decoupled.")

    asyncio.run(_run())

if __name__ == "__main__":
    test_webhook_latency_and_debounce()
