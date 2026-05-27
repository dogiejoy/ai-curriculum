"""
Pydantic models สำหรับงาน LLM จริง — จะใช้ต่อใน Block 3 ตอน refactor compare_models.py
"""
from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


ModelName = Literal[
    "claude-opus-4-7",
    "claude-sonnet-4-6",
    "claude-haiku-4-5-20251001",
]


class TokenUsage(BaseModel):
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)


class LLMCallResult(BaseModel):
    """ผลของ 1 API call — เก็บทุกอย่างที่ต้องใช้ analyze"""
    
    model: ModelName
    prompt: str
    response_text: str
    
    usage: TokenUsage
    latency_seconds: float = Field(gt=0)
    cost_usd: float = Field(ge=0)
    
    model_provider : Literal["anthropic", "openai"]

    # Auto timestamp
    called_at: datetime = Field(default_factory=datetime.now)
    
    def summary(self) -> str:
        return (
            f"{self.model} | "
            f"in/out: {self.usage.input_tokens}/{self.usage.output_tokens} | "
            f"{self.latency_seconds:.2f}s | "
            f"${self.cost_usd:.5f}"
        )


# Test > Call :: LLMCallResult
result = LLMCallResult(
    model="claude-opus-4-7",
    model_provider="anthropic",
    prompt="แนะนำตัว 2 ประโยค",
    response_text="สวัสดีครับ ผมคือ Claude...",
    usage=TokenUsage(input_tokens=38, output_tokens=117),
    latency_seconds=2.34,
    cost_usd=0.009345,
)

print(result.summary())
print(f"\nFull dict:")
print(result.model_dump_json(indent=2))


# Save list of results to JSON file (Block 3 จะใช้ pattern นี้)
from pathlib import Path

results = [result]
output_file = Path("results.json")
output_file.write_text(
    "[" + ",\n".join(r.model_dump_json(indent=2) for r in results) + "]",
    encoding="utf-8",
)
print(f"\nSaved to {output_file}")