"""
Smoke tests — verify basic API startup, auth, CRUD and webhook endpoint.
Run: python -m pytest tests/test_smoke.py -v
"""
import json
import pytest


class TestHealth:
    def test_health_endpoint(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "message" in data


class TestAuth:
    def test_login_success(self, client):
        import os
        resp = client.post("/api/auth/login", json={
            "username": os.getenv("ADMIN_USERNAME", "clinica_espaco_interativo_reabilitare"),
            "password": os.getenv("ADMIN_PASSWORD", "admin"),
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data or "token" in data

    def test_login_wrong_password(self, client):
        resp = client.post("/api/auth/login", json={
            "username": "admin",
            "password": "wrong_password_12345",
        })
        assert resp.status_code in (401, 403)

    def test_protected_endpoint_without_token(self, client):
        resp = client.get("/api/appointments")
        assert resp.status_code == 401


class TestAppointmentsCRUD:
    def test_list_appointments(self, client, auth_headers):
        resp = client.get("/api/appointments", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "appointments" in data

    def test_create_appointment(self, client, auth_headers):
        resp = client.post("/api/appointments", headers=auth_headers, json={
            "patient_name": "Test Patient Smoke",
            "patient_phone": "5500000000000",
            "datetime": "2026-12-31 10:00",
            "service": "Clínica Geral",
        })
        assert resp.status_code == 200 or resp.status_code == 201


class TestWebhook:
    def test_webhook_missing_data(self, client):
        """Webhook should return 'ignored' for payloads without phone/text."""
        resp = client.post("/webhook/zapi", json={"random": "data"})
        # Should not crash — either ignored or 400
        assert resp.status_code in (200, 400, 401)

    def test_webhook_from_me_filtered(self, client):
        """Messages from the bot itself (fromMe=True) should be filtered out."""
        resp = client.post("/webhook/zapi", json={
            "phone": "5511999999999",
            "text": {"message": "test"},
            "messageId": "smoke-from-me",
            "fromMe": True,
            "isGroup": False,
        })
        # Expect ignored or 401 (if webhook signature validation is on)
        assert resp.status_code in (200, 401)
