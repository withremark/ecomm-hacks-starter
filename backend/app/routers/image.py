"""Image generation router for Nano Banana endpoints."""

import base64
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from app.models.image import (
    GeneratedImage,
    ImageEditRequest,
    ImageGenerateRequest,
    ImageResponse,
)
from app.services.gemini import GeminiService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/image", tags=["image"])


def get_gemini_service(request: Request) -> GeminiService:
    """Dependency to get Gemini service from app state."""
    return request.app.state.gemini_service


@router.post("/generate", response_model=ImageResponse)
async def generate_image(
    request: ImageGenerateRequest,
    gemini: Annotated[GeminiService, Depends(get_gemini_service)],
):
    """Generate images using Nano Banana (Gemini 2.0 Flash Exp).

    Send a text prompt and receive generated images.
    Images are returned as base64-encoded data.
    """
    try:
        result = await gemini.generate_image(
            prompt=request.prompt,
            model=request.model or "gemini-2.5-flash-image",
            aspect_ratio=request.aspect_ratio,
        )

        return ImageResponse(
            text=result.text,
            images=[GeneratedImage(data=img["data"], mime_type=img["mime_type"]) for img in result.images],
            model=result.model,
            usage=result.usage,
        )

    except Exception as e:
        logger.error(f"Image generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/edit", response_model=ImageResponse)
async def edit_image(
    request: ImageEditRequest,
    gemini: Annotated[GeminiService, Depends(get_gemini_service)],
):
    """Edit an existing image using Nano Banana.

    Send an image (base64) with editing instructions.
    Returns the edited image as base64-encoded data.
    """
    try:
        # Decode base64 image
        image_data = base64.b64decode(request.image)

        result = await gemini.edit_image(
            prompt=request.prompt,
            image_data=image_data,
            image_mime_type=request.mime_type,
            model=request.model or "gemini-2.5-flash-image",
        )

        return ImageResponse(
            text=result.text,
            images=[GeneratedImage(data=img["data"], mime_type=img["mime_type"]) for img in result.images],
            model=result.model,
            usage=result.usage,
        )

    except Exception as e:
        logger.error(f"Image editing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_image_models():
    """List available image generation models."""
    return {
        "models": [
            {
                "id": "gemini-2.5-flash-image",
                "alias": "nano-banana",
                "description": "Gemini 2.5 Flash Image (Nano Banana) - State-of-the-art image generation",
                "default": True,
            },
            {
                "id": "gemini-3-pro-image-preview",
                "alias": "nano-banana-pro",
                "description": "Gemini 3 Pro Image (Nano Banana Pro) - Best quality (preview)",
            },
            {
                "id": "gemini-2.0-flash-exp",
                "alias": "legacy",
                "description": "Gemini 2.0 Flash Experimental - Legacy image generation",
            },
        ]
    }
