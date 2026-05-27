"""
Week 1 — Compare models in parallel using async.
Pydantic for type safety + asyncio.gather for parallelism.
"""
import asyncio
import time
from datetime import datetime
from pathlib import Path
from typing import Literal

from anthropic import AsyncAnthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()
client = AsyncAnthropic()  # ← Async version


ModelName = Literal[
    "claude-opus-4-7",
    "claude-sonnet-4-6",
    "claude-haiku-4-5-20251001",
]

# ⚠️ Update with verified pricing from Day 2
PRICING: dict[str, dict[str, float]] = {
    "claude-opus-4-7":           {"input": 5.00, "output": 25.00},
    "claude-sonnet-4-6":         {"input": 3.00, "output": 15.00},
    "claude-haiku-4-5-20251001": {"input": 1.00, "output": 5.00},
}


# ===== Pydantic models =====

class TokenUsage(BaseModel):
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)


class LLMCallResult(BaseModel):
    model: ModelName
    prompt: str
    response_text: str
    usage: TokenUsage
    latency_seconds: float = Field(gt=0)
    cost_usd: float = Field(ge=0)
    called_at: datetime = Field(default_factory=datetime.now)


# ===== Logic =====

def calculate_cost(model: ModelName, input_tokens: int, output_tokens: int) -> float:
    rates = PRICING[model]
    return (input_tokens / 1_000_000) * rates["input"] + \
           (output_tokens / 1_000_000) * rates["output"]


async def call_model(model: ModelName, prompt: str) -> LLMCallResult:
    """Async API call → validated Pydantic model."""
    start = time.time()

    response = await client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    latency = time.time() - start

    return LLMCallResult(
        model=model,
        prompt=prompt,
        response_text=response.content[0].text,
        usage=TokenUsage(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        ),
        latency_seconds=latency,
        cost_usd=calculate_cost(
            model,
            response.usage.input_tokens,
            response.usage.output_tokens,
        ),
    )


async def compare_all_models(prompt: str) -> list[LLMCallResult]:
    """Run all 3 models for one prompt — in parallel."""
    models: list[ModelName] = [
        "claude-opus-4-7",
        "claude-sonnet-4-6",
        "claude-haiku-4-5-20251001",
    ]

    # ⭐ This is the magic — asyncio.gather runs all coroutines concurrently
    tasks = [call_model(m, prompt) for m in models]
    results = await asyncio.gather(*tasks)
    return results


async def main():
    test_prompts = [
        "เมืองหลวงของประเทศไทยคืออะไร? ตอบสั้นๆ",
        "อธิบาย event loop ใน JavaScript ใน 3 ประโยคภาษาไทย",
        "Laravel migration สำหรับ table 'orders' มี columns: id, user_id (FK), "
        "total (decimal 10,2), status (enum pending/paid/cancelled). เขียน code",
        "ถ้า x=3, y=x*2+1, z=y-x และ w=z*z แล้ว w=? โชว์ขั้นตอน",
    ]

    all_results: list[LLMCallResult] = []
    overall_start = time.time()

    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n{'=' * 75}")
        print(f"[{i}/{len(test_prompts)}] PROMPT: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        print('=' * 75)

        # ⭐ 3 models in parallel per prompt
        results = await compare_all_models(prompt)
        all_results.extend(results)

        for r in results:
            short = r.model.split("-")[1].title()
            print(f"\n→ {short:7s} {r.latency_seconds:5.2f}s | "
                  f"in/out: {r.usage.input_tokens}/{r.usage.output_tokens:3d} | "
                  f"${r.cost_usd:.5f}")
            preview = r.response_text[:150].replace("\n", " ")
            print(f"  {preview}...")

    overall_time = time.time() - overall_start

    # ===== Summary =====
    print(f"\n{'=' * 75}")
    print("SUMMARY")
    print('=' * 75)
    print(f"\n  ⏱  Wall time: {overall_time:.2f}s (sequential = ~{overall_time * 3:.1f}s)")
    print(f"  💡 Speedup from parallelism: ~3x\n")

    # Per-model aggregate using dict comprehension
    by_model: dict[str, list[LLMCallResult]] = {}
    for r in all_results:
        by_model.setdefault(r.model, []).append(r)

    for model, results in by_model.items():
        total_cost = sum(r.cost_usd for r in results)
        avg_latency = sum(r.latency_seconds for r in results) / len(results)
        total_in = sum(r.usage.input_tokens for r in results)
        total_out = sum(r.usage.output_tokens for r in results)
        print(f"  {model}")
        print(f"    Total cost: ${total_cost:.5f}")
        print(f"    Avg latency: {avg_latency:.2f}s")
        print(f"    Total tokens (in/out): {total_in}/{total_out}")
        print()

    # ===== Save results =====
    output_file = Path("results_async.json")
    output_file.write_text(
        "[\n"
        + ",\n".join(r.model_dump_json(indent=2) for r in all_results)
        + "\n]",
        encoding="utf-8",
    )
    print(f"  💾 Saved {len(all_results)} results → {output_file}")


if __name__ == "__main__":
    # asyncio.run = entry point ที่จัดการ event loop ให้
    asyncio.run(main())