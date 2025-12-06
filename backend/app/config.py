"""Shared configuration for the Gemini backend."""

import os

# Default models
DEFAULT_MODEL = "gemini-3-pro-preview"
DEFAULT_IMAGE_MODEL = "gemini-3-pro-image-preview"

# Default CORS origins for local development
DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:4173",
    "http://localhost:4174",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
]

# Default server settings
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000

# Model alias mapping - maps friendly names to actual Gemini model IDs
MODEL_MAP: dict[str, str] = {
    "pro": "gemini-3-pro-preview",
    "flash": "gemini-3-pro-preview",  # Use pro for everything
    "flash-thinking": "gemini-3-pro-preview",
}


def get_model(alias: str, default: str | None = None) -> str:
    """Get the Gemini model ID for a given alias.

    Args:
        alias: Model alias (e.g., "pro", "flash")
        default: Default model if alias not found. Uses DEFAULT_MODEL if not specified.

    Returns:
        Gemini model ID string
    """
    if default is None:
        default = DEFAULT_MODEL
    return MODEL_MAP.get(alias, default)


def get_cors_origins() -> list[str]:
    """Get CORS allowed origins from env var or defaults.

    Set CORS_ORIGINS env var as comma-separated list to override.
    Example: CORS_ORIGINS=http://example.com,http://test.com

    Returns:
        List of allowed origin URLs
    """
    env_origins = os.environ.get("CORS_ORIGINS")
    if env_origins:
        return [origin.strip() for origin in env_origins.split(",") if origin.strip()]
    return DEFAULT_CORS_ORIGINS.copy()


def get_server_host() -> str:
    """Get server host from env var or default.

    Set HOST env var to override (default: 0.0.0.0).

    Returns:
        Host string
    """
    return os.environ.get("HOST", DEFAULT_HOST)


def get_server_port() -> int:
    """Get server port from env var or default.

    Set PORT env var to override (default: 8000).

    Returns:
        Port number
    """
    port_str = os.environ.get("PORT")
    if port_str:
        return int(port_str)
    return DEFAULT_PORT
