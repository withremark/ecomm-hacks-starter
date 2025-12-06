"""Tests for chat API endpoints."""

import os

import pytest


@pytest.mark.anyio
async def test_list_chat_models_returns_available_models(client):
    """Test that /api/chat/models returns available Gemini models."""
    response = await client.get("/api/chat/models")

    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) > 0

    # Check that each model has required fields
    for model in data["models"]:
        assert "id" in model
        assert "description" in model


@pytest.mark.anyio
async def test_list_chat_models_includes_expected_models(client):
    """Test that expected Gemini models are available."""
    response = await client.get("/api/chat/models")

    data = response.json()
    model_ids = [m["id"] for m in data["models"]]

    # Verify expected models are present
    assert "gemini-3-pro-preview" in model_ids


@pytest.mark.anyio
@pytest.mark.integration
@pytest.mark.skipif(not os.environ.get("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set")
async def test_simple_query_returns_response(client):
    """Test that POST /api/chat/query returns a valid response."""
    response = await client.post(
        "/api/chat/query",
        json={
            "prompt": "Reply with only the word 'hello'",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    assert "model" in data
    assert len(data["text"]) > 0


@pytest.mark.anyio
@pytest.mark.integration
@pytest.mark.skipif(not os.environ.get("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set")
async def test_simple_query_with_system_prompt(client):
    """Test that system_prompt is respected in simple query."""
    response = await client.post(
        "/api/chat/query",
        json={
            "prompt": "What is your name?",
            "system_prompt": "You are a helpful assistant named TestBot. Always introduce yourself as TestBot.",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    # The response should mention TestBot if system prompt is working
    assert "TestBot" in data["text"] or "testbot" in data["text"].lower()


@pytest.mark.anyio
@pytest.mark.integration
@pytest.mark.skipif(not os.environ.get("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set")
async def test_chat_completions_returns_response(client):
    """Test that POST /api/chat/completions returns a valid response."""
    response = await client.post(
        "/api/chat/completions",
        json={
            "messages": [{"role": "user", "content": "Reply with only the word 'hello'"}],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"]["role"] == "assistant"
    assert len(data["message"]["content"]) > 0
    assert "model" in data


@pytest.mark.anyio
@pytest.mark.integration
@pytest.mark.skipif(not os.environ.get("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set")
async def test_chat_completions_with_conversation_history(client):
    """Test that multi-turn conversation works correctly."""
    response = await client.post(
        "/api/chat/completions",
        json={
            "messages": [
                {"role": "user", "content": "My favorite color is blue. Remember this."},
                {"role": "assistant", "content": "I'll remember that your favorite color is blue!"},
                {"role": "user", "content": "What is my favorite color?"},
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    # The response should reference blue from the conversation history
    assert "blue" in data["message"]["content"].lower()


@pytest.mark.anyio
async def test_simple_query_validation_error(client):
    """Test that missing required fields return validation error."""
    response = await client.post(
        "/api/chat/query",
        json={},  # Missing required 'prompt' field
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.anyio
async def test_chat_completions_validation_error(client):
    """Test that missing required fields return validation error."""
    response = await client.post(
        "/api/chat/completions",
        json={},  # Missing required 'messages' field
    )

    assert response.status_code == 422  # Validation error
