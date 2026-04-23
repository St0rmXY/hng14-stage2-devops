"""
Unit tests for the API — Redis is fully mocked using fakeredis.
At least 3 tests required by the pipeline spec.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import fakeredis
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app, redis_client  # noqa: E402


@pytest.fixture
def fake_redis():
    """Swap the real Redis client for an in-memory fakeredis instance."""
    server = fakeredis.FakeServer()
    fake = fakeredis.FakeRedis(server=server)
    return fake


@pytest.fixture
def client(fake_redis):
    """FastAPI test client with Redis patched out."""
    with patch("main.redis_client", fake_redis):
        yield TestClient(app)


# ── Test 1: Health endpoint returns 200 ───────────────────────────────────────
def test_health_check_returns_ok(client, fake_redis):
    with patch("main.redis_client", fake_redis):
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# ── Test 2: Creating a job returns a job_id and pending status ────────────────
def test_create_job_returns_job_id(client, fake_redis):
    with patch("main.redis_client", fake_redis):
        response = client.post("/jobs", json={"payload": "test-job"})
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert len(data["job_id"]) > 0


# ── Test 3: Each created job gets a unique ID ─────────────────────────────────
def test_each_job_gets_unique_id(client, fake_redis):
    with patch("main.redis_client", fake_redis):
        r1 = client.post("/jobs", json={"payload": "job-one"})
        r2 = client.post("/jobs", json={"payload": "job-two"})
    assert r1.json()["job_id"] != r2.json()["job_id"]


# ── Test 4: Job status starts as pending ─────────────────────────────────────
def test_new_job_status_is_pending(client, fake_redis):
    with patch("main.redis_client", fake_redis):
        create = client.post("/jobs", json={"payload": "status-check"})
        job_id = create.json()["job_id"]
        response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "pending"


# ── Test 5: Querying a non-existent job returns 404 ──────────────────────────
def test_get_nonexistent_job_returns_404(client, fake_redis):
    with patch("main.redis_client", fake_redis):
        response = client.get("/jobs/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


# ── Test 6: Health check fails gracefully when Redis is down ──────────────────
def test_health_check_when_redis_down():
    dead_redis = MagicMock()
    dead_redis.ping.side_effect = Exception("Connection refused")
    with patch("main.redis_client", dead_redis):
        response = TestClient(app).get("/health")
    assert response.status_code == 503
