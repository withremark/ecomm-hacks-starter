"""Tests for service unavailability handling.

These tests verify that endpoints return 503 when the Gemini service is not initialized.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client_without_service():
    """Create a test client WITHOUT initializing the Gemini service."""
    # Don't use lifespan - this leaves gemini_service as None
    app.state.gemini_service = None
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


class TestServiceUnavailable:
    """Tests for 503 responses when Gemini service is unavailable."""

    @pytest.mark.anyio
    async def test_chat_query_returns_503_when_service_unavailable(self, client_without_service):
        """Test that /api/chat/query returns 503 when service is None."""
        response = await client_without_service.post(
            "/api/chat/query",
            json={"prompt": "Hello"},
        )
        assert response.status_code == 503
        assert "not initialized" in response.json()["detail"].lower()

    @pytest.mark.anyio
    async def test_chat_completions_returns_503_when_service_unavailable(self, client_without_service):
        """Test that /api/chat/completions returns 503 when service is None."""
        response = await client_without_service.post(
            "/api/chat/completions",
            json={"messages": [{"role": "user", "content": "Hello"}]},
        )
        assert response.status_code == 503
        assert "not initialized" in response.json()["detail"].lower()

    @pytest.mark.anyio
    async def test_media_query_returns_503_when_service_unavailable(self, client_without_service):
        """Test that /api/media/query returns 503 when service is None."""
        response = await client_without_service.post(
            "/api/media/query",
            json={"prompt": "Hello", "files": []},
        )
        assert response.status_code == 503
        assert "not initialized" in response.json()["detail"].lower()

    @pytest.mark.anyio
    async def test_image_generate_returns_503_when_service_unavailable(self, client_without_service):
        """Test that /api/image/generate returns 503 when service is None."""
        response = await client_without_service.post(
            "/api/image/generate",
            json={"prompt": "A red apple"},
        )
        assert response.status_code == 503
        assert "not initialized" in response.json()["detail"].lower()

    @pytest.mark.anyio
    async def test_image_edit_returns_503_when_service_unavailable(self, client_without_service):
        """Test that /api/image/edit returns 503 when service is None."""
        response = await client_without_service.post(
            "/api/image/edit",
            json={"prompt": "Make it blue", "image": "base64data", "mime_type": "image/png"},
        )
        assert response.status_code == 503
        assert "not initialized" in response.json()["detail"].lower()
