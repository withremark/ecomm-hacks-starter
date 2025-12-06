"""Tests for shared configuration."""

import os

import pytest


class TestModelConfig:
    """Tests for model configuration."""

    def test_model_map_exists(self):
        """Test that MODEL_MAP is importable from config."""
        from app.config import MODEL_MAP

        assert MODEL_MAP is not None
        assert isinstance(MODEL_MAP, dict)

    def test_model_map_has_required_keys(self):
        """Test that MODEL_MAP has all required model aliases."""
        from app.config import MODEL_MAP

        required_keys = ["pro", "flash", "flash-thinking"]
        for key in required_keys:
            assert key in MODEL_MAP, f"Missing key: {key}"

    def test_model_map_values_are_valid_models(self):
        """Test that MODEL_MAP values are valid Gemini model names."""
        from app.config import MODEL_MAP

        for alias, model in MODEL_MAP.items():
            assert model.startswith("gemini-"), f"Invalid model for {alias}: {model}"

    def test_default_model_constant_exists(self):
        """Test that DEFAULT_MODEL constant exists."""
        from app.config import DEFAULT_MODEL

        assert DEFAULT_MODEL is not None
        assert DEFAULT_MODEL.startswith("gemini-")

    def test_default_image_model_constant_exists(self):
        """Test that DEFAULT_IMAGE_MODEL constant exists."""
        from app.config import DEFAULT_IMAGE_MODEL

        assert DEFAULT_IMAGE_MODEL is not None
        assert "image" in DEFAULT_IMAGE_MODEL.lower() or "preview" in DEFAULT_IMAGE_MODEL

    def test_get_model_function(self):
        """Test get_model helper returns correct model."""
        from app.config import get_model

        # Known alias should return mapped model
        result = get_model("pro")
        assert result.startswith("gemini-")

        # Unknown alias should return default
        result = get_model("unknown-alias")
        assert result.startswith("gemini-")

    def test_get_model_with_custom_default(self):
        """Test get_model with custom default."""
        from app.config import get_model

        custom_default = "gemini-custom-model"
        result = get_model("unknown-alias", default=custom_default)
        assert result == custom_default


class TestServerConfig:
    """Tests for server configuration."""

    def test_get_cors_origins_returns_list(self):
        """Test that get_cors_origins returns a list."""
        from app.config import get_cors_origins

        origins = get_cors_origins()
        assert isinstance(origins, list)

    def test_get_cors_origins_has_defaults(self):
        """Test that default CORS origins are provided."""
        from app.config import get_cors_origins

        origins = get_cors_origins()
        assert len(origins) > 0
        # Should include common localhost ports
        assert any("localhost" in o for o in origins)

    def test_get_cors_origins_from_env(self, monkeypatch):
        """Test that CORS origins can be set via env var."""
        from app.config import get_cors_origins

        monkeypatch.setenv("CORS_ORIGINS", "http://example.com,http://test.com")
        origins = get_cors_origins()
        assert "http://example.com" in origins
        assert "http://test.com" in origins

    def test_get_server_port_default(self):
        """Test that default server port is 8000."""
        from app.config import get_server_port

        port = get_server_port()
        assert port == 8000

    def test_get_server_port_from_env(self, monkeypatch):
        """Test that server port can be set via env var."""
        from app.config import get_server_port

        monkeypatch.setenv("PORT", "9000")
        port = get_server_port()
        assert port == 9000

    def test_get_server_host_default(self):
        """Test that default server host is 0.0.0.0."""
        from app.config import get_server_host

        host = get_server_host()
        assert host == "0.0.0.0"

    def test_get_server_host_from_env(self, monkeypatch):
        """Test that server host can be set via env var."""
        from app.config import get_server_host

        monkeypatch.setenv("HOST", "127.0.0.1")
        host = get_server_host()
        assert host == "127.0.0.1"
