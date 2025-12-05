"""Tests for image API endpoints."""

import base64
import os

import pytest


@pytest.mark.anyio
async def test_list_image_models_returns_available_models(client):
    """Test that /api/image/models returns available image models."""
    response = await client.get("/api/image/models")

    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) > 0

    # Check that each model has required fields
    for model in data["models"]:
        assert "id" in model
        assert "description" in model


@pytest.mark.anyio
async def test_list_image_models_includes_expected_models(client):
    """Test that expected image models are available."""
    response = await client.get("/api/image/models")

    data = response.json()
    model_ids = [m["id"] for m in data["models"]]

    # Verify expected models are present
    assert "gemini-2.5-flash-image" in model_ids
    assert "gemini-2.0-flash-exp" in model_ids


@pytest.mark.anyio
async def test_list_image_models_has_default_model(client):
    """Test that one image model is marked as default."""
    response = await client.get("/api/image/models")

    data = response.json()
    default_models = [m for m in data["models"] if m.get("default")]

    assert len(default_models) == 1
    assert default_models[0]["id"] == "gemini-2.5-flash-image"


@pytest.mark.anyio
@pytest.mark.integration
@pytest.mark.skipif(not os.environ.get("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set")
async def test_generate_image_returns_response(client):
    """Test that POST /api/image/generate returns a valid response."""
    response = await client.post(
        "/api/image/generate",
        json={
            "prompt": "A simple red circle on white background",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "images" in data
    assert "model" in data
    # Should return at least one image
    assert len(data["images"]) > 0
    # Each image should have data and mime_type
    for image in data["images"]:
        assert "data" in image
        assert "mime_type" in image
        # Verify the data is valid base64
        assert len(image["data"]) > 0


@pytest.mark.anyio
@pytest.mark.integration
@pytest.mark.skipif(not os.environ.get("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set")
async def test_generate_image_with_aspect_ratio(client):
    """Test that aspect_ratio parameter is accepted."""
    response = await client.post(
        "/api/image/generate",
        json={
            "prompt": "A simple blue square",
            "aspect_ratio": "1:1",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "images" in data


@pytest.mark.anyio
@pytest.mark.integration
@pytest.mark.skipif(not os.environ.get("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set")
async def test_edit_image_returns_response(client):
    """Test that POST /api/image/edit returns a valid response."""
    # Create a simple 1x1 red PNG image for testing
    # This is a minimal valid PNG (1x1 red pixel)
    png_data = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
    )
    image_base64 = base64.b64encode(png_data).decode("utf-8")

    response = await client.post(
        "/api/image/edit",
        json={
            "prompt": "Make this image blue instead of red",
            "image": image_base64,
            "mime_type": "image/png",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "images" in data
    assert "model" in data


@pytest.mark.anyio
async def test_generate_image_validation_error(client):
    """Test that missing required fields return validation error."""
    response = await client.post(
        "/api/image/generate",
        json={},  # Missing required 'prompt' field
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.anyio
async def test_edit_image_validation_error_missing_prompt(client):
    """Test that missing prompt returns validation error."""
    response = await client.post(
        "/api/image/edit",
        json={
            "image": "somebase64data",
            "mime_type": "image/png",
        },  # Missing required 'prompt' field
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.anyio
async def test_edit_image_validation_error_missing_image(client):
    """Test that missing image returns validation error."""
    response = await client.post(
        "/api/image/edit",
        json={
            "prompt": "Edit this image",
        },  # Missing required 'image' field
    )

    assert response.status_code == 422  # Validation error
