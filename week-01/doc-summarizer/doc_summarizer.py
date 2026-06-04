"""
Week 1 final project — Doc Summarizer.

Input: folder of .md/.txt files
Output: 3-bullet summary per file (JSON) with cost tracking
Compare: Opus 4.7 vs Sonnet 4.6 vs Haiku 4.5
"""
import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Literal

from anthropic import AsyncAnthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

load_dotenv()
client = AsyncAnthropic()


ModelName = Literal[
    "claude-opus-4-7",
    "claude-sonnet-4-6",
    "claude-haiku-4-5-20251001",
]

PRICING: dict[str, dict[str, float]] = {
    "claude-opus-4-7":           {"input": 5.00, "output": 25.00},
    "claude-sonnet-4-6":         {"input": 3.00, "output": 15.00},
    "claude-haiku-4-5-20251001": {"input": 1.00, "output":  5.00},
}


# ===== Pydantic models =====

class FileSummary(BaseModel):
    """Result of summarizing one file with one model."""
    filename: str
    file_size_chars: int
    model: ModelName
    bullets: list[str] = Field(min_length=3, max_length=3)
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_seconds: float
    summarized_at: datetime = Field(default_factory=datetime.now)

@field_validator("bullets")
@classmethod
def check_bullets_quality(cls, v: list[str]) -> list[str]:
    """Language-agnostic bullet validation using char count."""
    for i, bullet in enumerate(v):
        bullet = bullet.strip()
        char_count = len(bullet)
        
        if char_count < 20:
            raise ValueError(f"Bullet {i+1} too short ({char_count} chars): {bullet!r}")
        if char_count > 250:
            raise ValueError(f"Bullet {i+1} too long ({char_count} chars)")
        if not bullet:
            raise ValueError(f"Bullet {i+1} empty")
    return v
# ===== Core logic =====
# V1 :
# SUMMARIZE_PROMPT = """\
# สรุปเอกสารต่อไปนี้เป็น 3 bullet points ที่กระชับและจับใจความสำคัญ \
# แต่ละ bullet ไม่เกิน 25 คำ

# ตอบเป็น JSON เท่านั้น ในรูปแบบ:
# {{"bullets": ["bullet 1", "bullet 2", "bullet 3"]}}

# ห้ามใส่ markdown code fence หรือ explanation อื่นๆ ตอบเฉพาะ JSON

# เอกสาร:
# ---
# {content}
# ---"""
# V2 : multishot
SUMMARIZE_PROMPT = """\
สรุปเอกสารต่อไปนี้เป็น 3 bullet points ที่กระชับและจับใจความสำคัญ
แต่ละ bullet ไม่เกิน 25 คำ

<example>
<document>
Docker Compose is a tool for defining multi-container applications using YAML.
Services share networks, volumes, and configuration. Useful for local dev.
</document>
<output>
{{"bullets": [
  "Docker Compose จัดการ multi-container app ผ่าน YAML file เดียว ตั้งค่า service + network + volume ได้ครบ",
  "Service ใน compose เข้าถึงกันด้วย service name เป็น hostname บน network ที่ Docker สร้างให้",
  "ใช้ในงาน local development เพื่อ spin up dependencies เช่น Postgres + Redis ในคำสั่งเดียว"
]}}
</output>
</example>

ตอบเป็น JSON เท่านั้น ห้ามใส่ markdown code fence หรือ explanation อื่นๆ

เอกสาร:
---
{content}
---"""

def calculate_cost(model: ModelName, input_tokens: int, output_tokens: int) -> float:
    rates = PRICING[model]
    return (input_tokens / 1_000_000) * rates["input"] + \
           (output_tokens / 1_000_000) * rates["output"]


def parse_json_response(text: str) -> dict:
    """Strip optional markdown fence + parse JSON."""
    text = text.strip()
    if text.startswith("```"):
        # Remove ```json ... ``` wrapper
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(text)


async def summarize_file(path: Path, model: ModelName) -> FileSummary:
    """Summarize one file using one model."""
    content = path.read_text(encoding="utf-8")
    start = time.time()

    response = await client.messages.create(
        model=model,
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": SUMMARIZE_PROMPT.format(content=content),
        }],
    )

    latency = time.time() - start

    parsed = parse_json_response(response.content[0].text)

    return FileSummary(
        filename=path.name,
        file_size_chars=len(content),
        model=model,
        bullets=parsed["bullets"],
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        cost_usd=calculate_cost(
            model,
            response.usage.input_tokens,
            response.usage.output_tokens,
        ),
        latency_seconds=latency,
    )


async def summarize_folder(folder: Path, model: ModelName) -> list[FileSummary]:
    """Summarize all .md/.txt files. Skip + log files that fail."""
    files = sorted(
        f for f in folder.iterdir()
        if f.suffix in (".md", ".txt") and f.is_file()
    )

    if not files:
        print(f"⚠️  No .md/.txt files found in {folder}")
        return []

    print(f"  Processing {len(files)} files with {model}...")
    
    # Use gather with return_exceptions to not crash on single failure
    raw_results = await asyncio.gather(
        *(summarize_file(f, model) for f in files),
        return_exceptions=True,
    )
    
    successes = []
    for path, result in zip(files, raw_results):
        if isinstance(result, Exception):
            print(f"  ❌ {path.name}: {type(result).__name__}: {result}")
        else:
            successes.append(result)
    
    return successes

def print_model_report(model: ModelName, results: list[FileSummary]) -> None:
    """Per-model summary stats + sample output."""
    if not results:
        return

    total_cost = sum(r.cost_usd for r in results)
    total_in = sum(r.input_tokens for r in results)
    total_out = sum(r.output_tokens for r in results)
    avg_latency = sum(r.latency_seconds for r in results) / len(results)

    print(f"\n  📊 Files: {len(results)}")
    print(f"     Tokens (in/out): {total_in} / {total_out}")
    print(f"     Total cost: ${total_cost:.5f}")
    print(f"     Avg latency: {avg_latency:.2f}s")
    print(f"     Cost per 1000 docs (projected): ${total_cost * 1000 / len(results):.2f}")

    # Show first file's bullets as quality sample
    sample = results[0]
    print(f"\n     Sample output ({sample.filename}):")
    for i, bullet in enumerate(sample.bullets, 1):
        print(f"       {i}. {bullet}")

async def summarize_with_fallback(
    path: Path,
    model_tier: list[ModelName] = None,
) -> FileSummary:
    """
    Try cheap model first → escalate to more expensive if validation fails.
    
    Args:
        path: file to summarize
        model_tier: ordered list cheap→expensive (default Haiku→Sonnet→Opus)
    
    Returns:
        FileSummary from first model that passes validation.
    
    Raises:
        Exception if all models fail validation.
    """
    if model_tier is None:
        model_tier = [
            "claude-haiku-4-5-20251001",  # Try cheap first
            "claude-sonnet-4-6",          # Escalate if fail
            "claude-opus-4-7",            # Last resort
        ]
    
    errors = []
    for model in model_tier:
        try:
            result = await summarize_file(path, model)
            if model != model_tier[0]:
                print(f"  ⚡ {path.name}: escalated to {model}")
            return result
        except Exception as e:
            errors.append(f"{model}: {type(e).__name__}: {e}")
            continue
    
    raise RuntimeError(
        f"All models failed for {path.name}:\n  " + "\n  ".join(errors)
    )

async def main():
    folder = Path("test-docs")

    if not folder.exists():
        print(f"❌ Folder not found: {folder.absolute()}")
        return

    all_results: list[FileSummary] = []
    models: list[ModelName] = [
        "claude-opus-4-7",
        "claude-sonnet-4-6",
        "claude-haiku-4-5-20251001",
    ]

    overall_start = time.time()

    for model in models:
        print(f"\n{'=' * 70}")
        print(f"Model: {model}")
        print('=' * 70)

        results = await summarize_folder(folder, model)
        all_results.extend(results)
        print_model_report(model, results)

    overall_time = time.time() - overall_start

    # Save all results
    output = Path("summaries.json")
    output.write_text(
        "[\n"
        + ",\n".join(r.model_dump_json(indent=2) for r in all_results)
        + "\n]",
        encoding="utf-8",
    )

    print(f"\n{'=' * 70}")
    print(f"⏱  Total wall time: {overall_time:.2f}s")
    print(f"💾 Saved {len(all_results)} summaries → {output}")
    
    # ========================================
    # Mode B: Smart routing (cheap-first + fallback)
    # ========================================
    print("\n" + "█" * 70)
    print("MODE B: Smart routing (Haiku → Sonnet → Opus on fail)")
    print("█" * 70)
    
    files = sorted(
        f for f in folder.iterdir()
        if f.suffix in (".md", ".txt") and f.is_file()
    )
    
    tasks = [summarize_with_fallback(f) for f in files]
    smart_results = await asyncio.gather(*tasks)
    
    total_cost_smart = sum(r.cost_usd for r in smart_results)
    by_model_smart: dict[str, int] = {}
    for r in smart_results:
        by_model_smart[r.model] = by_model_smart.get(r.model, 0) + 1
    
    print(f"\n📊 Smart routing results:")
    print(f"   Files processed: {len(smart_results)}")
    print(f"   Total cost: ${total_cost_smart:.5f}")
    print(f"   Cost per 1000 (projected): ${total_cost_smart * 1000 / len(smart_results):.2f}")
    print(f"   Model usage breakdown:")
    for model, count in by_model_smart.items():
        pct = count / len(smart_results) * 100
        print(f"     {model}: {count} files ({pct:.0f}%)")

if __name__ == "__main__":
    asyncio.run(main())
