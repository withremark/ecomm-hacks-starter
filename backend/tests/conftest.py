"""Pytest configuration and fixtures for backend tests."""

import os

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app, lifespan


@pytest.fixture
def anyio_backend():
    """Use asyncio as the async backend."""
    return "asyncio"


@pytest.fixture
async def client():
    """Create an async test client for the FastAPI app with lifespan."""
    async with lifespan(app):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as ac:
            yield ac


@pytest.fixture
def has_gemini_api_key():
    """Check if Gemini API key is available."""
    return bool(os.environ.get("GEMINI_API_KEY"))


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "integration: marks tests as integration tests (require API key)")
