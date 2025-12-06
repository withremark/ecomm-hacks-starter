"""Tests for image search API endpoints (Wikimedia Commons)."""

from unittest.mock import AsyncMock, patch

import pytest


class TestImageSearchEndpoints:
    """Tests for /api/images/* endpoints."""

    @pytest.mark.anyio
    async def test_search_images_returns_results(self, client):
        """Test that /api/images/search returns results for a valid query."""
        # Mock the httpx response to avoid hitting real API
        mock_response = {
            "query": {
                "pages": {
                    "123": {
                        "title": "File:Test_image.jpg",
                        "imageinfo": [
                            {
                                "url": "https://example.com/image.jpg",
                                "thumburl": "https://example.com/thumb.jpg",
                                "extmetadata": {
                                    "ImageDescription": {"value": "A test image"},
                                    "Artist": {"value": "Test Artist"},
                                },
                            }
                        ],
                    }
                }
            }
        }

        with patch("app.routers.images.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get.return_value = AsyncMock(
                status_code=200,
                json=lambda: mock_response,
                raise_for_status=lambda: None,
            )
            mock_client.return_value.__aenter__.return_value = mock_instance

            response = await client.get("/api/images/search?query=sunset")

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "query" in data
        assert data["query"] == "sunset"

    @pytest.mark.anyio
    async def test_search_images_requires_query(self, client):
        """Test that /api/images/search requires a query parameter."""
        response = await client.get("/api/images/search")
        assert response.status_code == 422  # Validation error

    @pytest.mark.anyio
    async def test_search_images_validates_limit(self, client):
        """Test that limit parameter is validated."""
        # Limit too high
        response = await client.get("/api/images/search?query=test&limit=100")
        assert response.status_code == 422

        # Limit too low
        response = await client.get("/api/images/search?query=test&limit=0")
        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_random_images_returns_results(self, client):
        """Test that /api/images/random returns results."""
        mock_response = {
            "query": {
                "pages": {
                    "456": {
                        "title": "File:Featured_image.jpg",
                        "imageinfo": [
                            {
                                "url": "https://example.com/featured.jpg",
                                "thumburl": "https://example.com/featured_thumb.jpg",
                                "extmetadata": {},
                            }
                        ],
                    }
                }
            }
        }

        with patch("app.routers.images.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get.return_value = AsyncMock(
                status_code=200,
                json=lambda: mock_response,
                raise_for_status=lambda: None,
            )
            mock_client.return_value.__aenter__.return_value = mock_instance

            response = await client.get("/api/images/random")

        assert response.status_code == 200
        data = response.json()
        assert "results" in data

    @pytest.mark.anyio
    async def test_search_handles_api_error(self, client):
        """Test that API errors are handled gracefully."""
        import httpx

        with patch("app.routers.images.httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get.side_effect = httpx.HTTPError("Connection failed")
            mock_client.return_value.__aenter__.return_value = mock_instance

            response = await client.get("/api/images/search?query=test")

        assert response.status_code == 502
        assert "Wikimedia API error" in response.json()["detail"]
