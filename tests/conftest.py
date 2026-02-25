import sys
import os

# Ensure project root is on the path for all tests
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env BEFORE any project imports so config picks up env vars
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

# Force test isolation: never use production data directory.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_DATA_DIR = os.path.join(PROJECT_ROOT, "data_test")
os.makedirs(TEST_DATA_DIR, exist_ok=True)
os.environ["DATA_DIR"] = TEST_DATA_DIR

# Provide a fallback JWT_SECRET_KEY for testing if not set in .env
if not os.environ.get("JWT_SECRET_KEY"):
    os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-smoke-tests"

# Disable webhook signature validation in tests by default
if not os.environ.get("WEBHOOK_VALIDATE_SIGNATURE"):
    os.environ["WEBHOOK_VALIDATE_SIGNATURE"] = "false"

import pytest
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture(scope="session")
def client():
    """FastAPI TestClient for the entire test session."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def auth_token(client):
    """Authenticate and return a valid JWT token."""
    username = os.getenv("ADMIN_USERNAME", "clinica_espaco_interativo_reabilitare")
    password = os.getenv("ADMIN_PASSWORD", "admin")
    resp = client.post("/api/auth/login", json={
        "username": username,
        "password": password,
    })
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    data = resp.json()
    return data.get("access_token") or data.get("token", "")


@pytest.fixture()
def auth_headers(auth_token):
    """Authorization headers for authenticated requests."""
    return {"Authorization": f"Bearer {auth_token}"}
