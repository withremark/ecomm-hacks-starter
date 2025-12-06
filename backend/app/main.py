"""Main FastAPI application for Gemini backend."""

import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_cors_origins, get_server_host, get_server_port
from app.routers import chat, generate, image, images, media, onboard, style
from app.services.gemini import GeminiService

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        method = request.method
        path = request.url.path
        query = str(request.query_params) if request.query_params else ""

        # Log request
        logger.info(f"[HTTP] --> {method} {path}{f'?{query}' if query else ''}")

        try:
            response = await call_next(request)
            elapsed = time.time() - start_time

            # Log response with appropriate level based on status code
            status = response.status_code
            level = logging.INFO if status < 400 else logging.WARNING if status < 500 else logging.ERROR
            logger.log(level, f"[HTTP] <-- {method} {path} {status} ({elapsed:.2f}s)")

            return response
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"[HTTP] <-- {method} {path} ERROR ({elapsed:.2f}s): {type(e).__name__}: {e}")
            raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown."""
    logger.info("Starting Gemini backend...")

    # Initialize Gemini service
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY not set - API calls will fail")

    default_model = os.environ.get("GEMINI_MODEL", "gemini-3-pro-preview")

    try:
        app.state.gemini_service = GeminiService(api_key=api_key, default_model=default_model)
        logger.info(f"Gemini service initialized with model: {default_model}")
    except ValueError as e:
        logger.error(f"Failed to initialize Gemini service: {e}")
        # Create a placeholder service that will error on use
        app.state.gemini_service = None

    host = get_server_host()
    port = get_server_port()
    logger.info(f"Gemini backend ready at http://{host}:{port}")

    yield

    logger.info("Shutting down Gemini backend...")


app = FastAPI(
    title="Gemini Backend API",
    description="FastAPI backend for Google Gemini API",
    version="0.1.0",
    lifespan=lifespan,
)

# Request logging middleware (added first, runs last)
app.add_middleware(RequestLoggingMiddleware)

# CORS middleware - origins configurable via CORS_ORIGINS env var
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(image.router)
app.include_router(media.router)

# Ephemeral canvas routers
app.include_router(onboard.router)
app.include_router(generate.router)
app.include_router(style.router)
app.include_router(images.router)


@app.get("/")
async def root():
    """API root - list available endpoints."""
    return {
        "name": "Gemini Backend API",
        "version": "0.1.0",
        "endpoints": {
            # Core Gemini endpoints
            "chat_completions": "POST /api/chat/completions",
            "simple_query": "POST /api/chat/query",
            "list_chat_models": "GET /api/chat/models",
            "generate_image": "POST /api/image/generate",
            "edit_image": "POST /api/image/edit",
            "list_image_models": "GET /api/image/models",
            "multimedia_query": "POST /api/media/query",
            "list_media_types": "GET /api/media/supported-types",
            # Ephemeral canvas endpoints
            "onboard": "POST /api/onboard",
            "generate": "POST /api/generate",
            "style": "POST /api/style",
            "images_search": "GET /api/images/search",
            "images_random": "GET /api/images/random",
            "health": "GET /health",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=get_server_host(), port=get_server_port())
