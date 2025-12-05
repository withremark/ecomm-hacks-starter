"""Tests for root and health endpoints."""

import pytest


@pytest.mark.anyio
async def test_root_endpoint_returns_api_info(client):
    """Test that root endpoint returns API info with available endpoints."""
    response = await client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Gemini Backend API"
    assert data["version"] == "0.1.0"
    assert "endpoints" in data


@pytest.mark.anyio
async def test_root_endpoint_lists_all_endpoints(client):
    """Test that root endpoint lists all available API endpoints."""
    response = await client.get("/")

    data = response.json()
    endpoints = data["endpoints"]

    # Verify all expected endpoints are listed
    assert "chat_completions" in endpoints
    assert "simple_query" in endpoints
    assert "list_chat_models" in endpoints
    assert "generate_image" in endpoints
    assert "edit_image" in endpoints
    assert "list_image_models" in endpoints
    assert "health" in endpoints


@pytest.mark.anyio
async def test_health_endpoint_returns_ok(client):
    """Test that health endpoint returns status ok."""
    response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
