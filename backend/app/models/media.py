"""Media models for multi-file API requests and responses."""

from pydantic import BaseModel, Field


class MediaFile(BaseModel):
    """A single media file (image, PDF, audio, video, text)."""

    data: str = Field(..., description="Base64-encoded file data")
    mime_type: str = Field(..., description="MIME type (e.g., image/png, application/pdf)")


class MediaQueryRequest(BaseModel):
    """Request for multi-media query."""

    prompt: str = Field(..., description="Text prompt/instruction")
    files: list[MediaFile] = Field(default_factory=list, description="List of media files")
    model: str | None = Field(None, description="Model to use (defaults to gemini-3-pro-preview)")
    response_modalities: list[str] | None = Field(None, description="Response types: ['TEXT'] or ['TEXT', 'IMAGE']")
    system_prompt: str | None = Field(None, description="System instructions")


class GeneratedMedia(BaseModel):
    """A generated media item (typically image)."""

    data: str = Field(..., description="Base64-encoded data")
    mime_type: str = Field(..., description="MIME type")


class MediaQueryResponse(BaseModel):
    """Response from multi-media query."""

    text: str | None = Field(None, description="Text response")
    images: list[GeneratedMedia] = Field(default_factory=list, description="Generated images")
    model: str = Field(..., description="Model used")
    usage: dict | None = Field(None, description="Token usage stats")
