"""Chat models for API requests and responses."""

from pydantic import BaseModel, Field


class Message(BaseModel):
    """A single message in a conversation."""

    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request for chat completion."""

    messages: list[Message] = Field(..., description="Conversation history")
    model: str | None = Field(None, description="Model to use (defaults to gemini-2.0-flash)")
    system_prompt: str | None = Field(None, description="System instructions")


class ChatResponse(BaseModel):
    """Response from chat completion."""

    message: Message = Field(..., description="Assistant response")
    model: str = Field(..., description="Model used")
    usage: dict | None = Field(None, description="Token usage stats")


class SimpleQueryRequest(BaseModel):
    """Request for a simple one-shot query."""

    prompt: str = Field(..., description="User prompt")
    model: str | None = Field(None, description="Model to use")
    system_prompt: str | None = Field(None, description="System instructions")


class SimpleQueryResponse(BaseModel):
    """Response from a simple query."""

    text: str = Field(..., description="Response text")
    model: str = Field(..., description="Model used")
    usage: dict | None = Field(None, description="Token usage stats")
