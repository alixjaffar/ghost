"""
Smoke tests for the Ghost backend.

Run from the `scraper/` directory:
    pip install -r requirements-dev.txt
    pytest

These tests use a throwaway SQLite DB and disable the background scheduler.
They do not require any AI/API keys (the analyzer falls back to regex).
"""
import os
import tempfile
import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    # Use an isolated temp DB and disable the scheduler before importing the app
    tmp_dir = tempfile.mkdtemp()
    os.environ["DATABASE_PATH"] = os.path.join(tmp_dir, "test_ghost.db")
    os.environ["ENABLE_SCHEDULER"] = "false"

    # Import (or reload) config + api so they pick up the env vars above
    import config
    importlib.reload(config)
    import api
    importlib.reload(api)

    with TestClient(api.app) as c:
        yield c


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"
    assert "sources" in body
    assert body["database"] == "connected"


def test_stats(client):
    resp = client.get("/api/stats")
    assert resp.status_code == 200
    body = resp.json()
    assert "content_items" in body
    assert "ticker_mentions" in body


def test_signals_list(client):
    resp = client.get("/api/signals")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_ingest_extracts_tickers(client):
    payload = {
        "items": [
            {
                "source": "youtube",
                "source_id": "smoke-test-1",
                "title": "NVDA and AMD surge on AI chip demand",
                "content": "Nvidia $NVDA is dominating AI chips. AMD and TSM also benefit.",
                "url": "https://youtube.com/watch?v=smoke-test-1",
                "author": "TestChannel",
                "engagement": 1000,
                "published_at": "2026-06-09T12:00:00Z",
            }
        ]
    }
    resp = client.post("/api/ingest", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "success"
    assert body["ingested"] == 1
    # Regex extraction alone should find at least one tracked ticker
    assert body["mentions"] >= 1


def test_content_after_ingest(client):
    resp = client.get("/api/content?limit=10")
    assert resp.status_code == 200
    items = resp.json()
    assert any(item.get("id") for item in items)
