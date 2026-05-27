# Basic types
def greet(name: str) -> str:
    return f"Hello, {name}"

# Multiple params with defaults
def call_model(
    model: str,
    prompt: str,
    max_tokens: int = 1024,
    temperature: float = 1.0,
) -> str:
    # Imagine API call here
    return f"Response from {model}"


# Collections (Python 3.9+ syntax)
def process_messages(messages: list[dict]) -> dict:
    return {"count": len(messages)}


# More specific types
from typing import Optional, Literal, Any

def get_text(response: Any, block_index: int = 0) -> Optional[str]:
    """Return text from response, or None if no text block."""
    try:
        return response.content[block_index].text
    except (IndexError, AttributeError):
        return None


# Literal — restrict to specific values (compile-time check)
ModelName = Literal["claude-opus-4-7", "claude-sonnet-4-6", "claude-haiku-4-5-20251001"]

def estimate_cost(
    model: ModelName,  # IDE/mypy จะ flag ถ้าส่ง string อื่น
    input_tokens: int,
    output_tokens: int,
) -> float:
    rates = {"claude-opus-4-7": (5.0, 25.0), 
             "claude-sonnet-4-6": (3.0, 15.0),
             "claude-haiku-4-5-20251001": (1.0, 5.0)}
    in_rate, out_rate = rates[model]
    return (input_tokens / 1_000_000) * in_rate + \
           (output_tokens / 1_000_000) * out_rate


# TypedDict — like PHP shape annotation
from typing import TypedDict

class ApiResult(TypedDict):
    model: str
    text: str
    input_tokens: int
    output_tokens: int
    cost_usd: float


def summarize(result: ApiResult) -> str:
    return f"{result['model']}: ${result['cost_usd']:.4f}"


# Test
result: ApiResult = {
    "model": "claude-opus-4-7",
    "text": "hello",
    "input_tokens": 10,
    "output_tokens": 5,
    "cost_usd": 0.000175,
}
print(summarize(result))
print(estimate_cost("claude-haiku-4-5-20251001", 1000, 500))