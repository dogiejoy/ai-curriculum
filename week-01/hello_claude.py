"""
Week 1 — First call to Claude API from Python.
Goal: verify SDK works + understand response structure.
"""
import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load .env (ANTHROPIC_API_KEY available in os.environ after this)
load_dotenv()

# Anthropic() auto-reads ANTHROPIC_API_KEY from env — no need to pass it
client = Anthropic()

# Pricing per million tokens (USD) — verify ปัจจุบันที่ https://docs.claude.com/en/docs/about-claude/pricing
PRICING = {
    "claude-opus-4-7":              {"input": 5.00, "output": 25.00},
    "claude-sonnet-4-6":            {"input":  3.00, "output": 15.00},
    "claude-haiku-4-5-20251001":    {"input":  1.00, "output":  5.00},
}


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate cost in USD for a single API call."""
    if model not in PRICING:
        return 0.0
    rates = PRICING[model]
    cost = (input_tokens / 1_000_000) * rates["input"] + \
           (output_tokens / 1_000_000) * rates["output"]
    return cost

response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "แนะนำตัวเป็นภาษาไทย 2 ประโยค"}
    ],
)

# response.content is a LIST of content blocks
# Each block can be type "text", "tool_use", etc.
# For simple text response, first block is type="text"

print(response.content[0].text)

print("\n" + "=" * 60)
print("Response object inspection:")
print("=" * 60)

print(f"\nModel used: {response.model}")
print(f"Stop reason: {response.stop_reason}")
print(f"Message ID: {response.id}")

print(f"\nUsage:")
print(f"  Input tokens:  {response.usage.input_tokens}")
print(f"  Output tokens: {response.usage.output_tokens}")

print(f"\nContent blocks ({len(response.content)}):")
for i, block in enumerate(response.content):
    print(f"  [{i}] type={block.type}, text_len={len(block.text)}")

cost = calculate_cost(response.model, response.usage.input_tokens, response.usage.output_tokens)
print(f"\nEstimated cost: ${cost:.6f} (~฿{cost * 36:.4f})")
