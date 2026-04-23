import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import fakeredis
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app  # noqa: E402


@pytest.fixture
def fake_redis():
    server = fakeredis.FakeServer()
    return fakeredis.FakeRedis(server=server)


@pytest.fixture
def client(fake_redis):
    with patch("main.r", fake_redis):
        yield TestClient(app)


def test_health_check_returns_ok(client, fake_redis):
    with patch("main.r", fake_redis):
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_job_returns_job_id(client, fake_redis):
    with patch("main.r", fake_redis):
        response = client.post("/jobs", json={"payload": "test-job"})
    assert response.status_code == 200
    assert "job_id" in response.json()


def test_each_job_gets_unique_id(client, fake_redis):
    with patch("main.r", fake_redis):
        r1 = client.post("/jobs", json={"payload": "job-one"})
        r2 = client.post("/jobs", json={"payload": "job-two"})
    assert r1.json()["job_id"] != r2.json()["job_id"]


def test_new_job_status_is_pending(client, fake_redis):
    with patch("main.r", fake_redis):
        create = client.post("/jobs", json={"payload": "status-check"})
        job_id = create.json()["job_id"]
        response = client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "queued"


def test_get_nonexistent_job_returns_404(client, fake_redis):
    with patch("main.r", fake_redis):
        response = client.get("/jobs/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_health_check_when_redis_down():
    dead_redis = MagicMock()
    dead_redis.ping.side_effect = Exception("Connection refused")
    with patch("main.r", dead_redis):
        response = TestClient(app).get("/health")
    assert response.status_code == 503
