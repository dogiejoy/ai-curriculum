from pydantic import BaseModel
from typing import Literal


class ContentBlock(BaseModel):
    type: Literal["text", "tool_use", "image"]
    text: str | None = None  # Python 3.10+ syntax for Optional


class Usage(BaseModel):
    input_tokens: int
    output_tokens: int


class ApiResponse(BaseModel):
    """Modeled after Anthropic Messages API response."""
    id: str
    model: str
    stop_reason: Literal["end_turn", "max_tokens", "stop_sequence", "tool_use"]
    content: list[ContentBlock]
    usage: Usage


# Simulate parsing API response (raw dict from JSON)
raw_response = {
    "id": "msg_01ABC123",
    "model": "claude-opus-4-7",
    "stop_reason": "end_turn",
    "content": [
        {"type": "text", "text": "Hello, Dogie!"},
    ],
    "usage": {
        "input_tokens": 38,
        "output_tokens": 117,
    },
}

# Pydantic parses + validates ทั้ง object รวม nested
response = ApiResponse(**raw_response)
print(response)
print(f"\nText: {response.content[0].text}")
print(f"Tokens: {response.usage.input_tokens}")

# If raw_response มี field ผิด — Pydantic จับได้ทันที + ชี้ที่ nested location
bad_raw = {
    "id": "msg_01ABC123",
    "model": "claude-opus-4-7",
    "stop_reason": "invalid_reason",  # ❌ ไม่อยู่ใน Literal
    "content": [{"type": "text", "text": "hi"}],
    "usage": {"input_tokens": "abc", "output_tokens": 117},  # ❌ ไม่ใช่ int
}

try:
    bad = ApiResponse(**bad_raw)
except Exception as e:
    print(f"\nNested errors:\n{e}")