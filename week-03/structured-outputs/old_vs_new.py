"""
Week 3 Day 2 — Old approach (Week 2 style) vs New structured outputs.
Same task: extract structured data from text.
"""
import asyncio
import json
import time

from anthropic import Anthropic, AsyncAnthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

load_dotenv()
sync_client = Anthropic()
async_client = AsyncAnthropic()

MODEL = "claude-sonnet-4-6"


# ===== Pydantic schema =====

class ContactInfo(BaseModel):
    name: str
    email: str
    plan_interest: str = Field(description="Plan tier user is interested in")
    demo_requested: bool


EMAIL_TEXT = (
    "John Smith (john.smith@example.com) is interested in our "
    "Enterprise plan and wants to schedule a demo for next Tuesday at 2pm."
)


# ===== Approach 1: OLD WAY (Week 1-2 style) =====

OLD_PROMPT = f"""ดึงข้อมูลจาก email นี้และตอบเป็น JSON valid:

{{
  "name": "...",
  "email": "...",
  "plan_interest": "...",
  "demo_requested": true/false
}}

ห้ามมี markdown wrapper หรือ explanation อื่น

Email:
{EMAIL_TEXT}"""


def strip_code_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return text


async def extract_old_way() -> tuple[ContactInfo | None, str, float]:
    """Old way: prompt instruction + strip code fence + Pydantic validate."""
    start = time.time()
    response = await async_client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": OLD_PROMPT}],
    )
    raw = response.content[0].text
    latency = time.time() - start
    
    # Need to handle markdown wrapper + parse + validate
    try:
        cleaned = strip_code_fence(raw)
        data = json.loads(cleaned)
        contact = ContactInfo(**data)
        return contact, raw, latency
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"❌ Old way parse fail: {e}")
        return None, raw, latency


# ===== Approach 2: NEW WAY (structured outputs + Pydantic helper) =====

def extract_new_way() -> tuple[ContactInfo, str, float]:
    """New way: client.messages.parse() with Pydantic model — guaranteed valid."""
    start = time.time()
    # Note: parse() is sync in current SDK
    response = sync_client.messages.parse(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": f"Extract contact info from: {EMAIL_TEXT}"}],
        output_format=ContactInfo,
    )
    latency = time.time() - start
    return response.parsed_output, response.content[0].text, latency


async def main():
    print(f"{'=' * 70}")
    print("Compare: Old approach (prompt+parse) vs New (structured outputs)")
    print('=' * 70)
    
    # OLD way
    print(f"\n── OLD: prompt instruction + strip + parse ──")
    old_result, old_raw, old_latency = await extract_old_way()
    print(f"Latency: {old_latency:.2f}s")
    print(f"Raw output:\n{old_raw}")
    if old_result:
        print(f"\nParsed: {old_result.model_dump_json(indent=2)}")
    
    # NEW way (call twice to show compilation caching)
    print(f"\n── NEW (1st call): structured outputs ──")
    new_result1, new_raw1, new_latency1 = extract_new_way()
    print(f"Latency: {new_latency1:.2f}s (includes grammar compilation)")
    print(f"Raw output:\n{new_raw1}")
    print(f"\nParsed: {new_result1.model_dump_json(indent=2)}")
    
    print(f"\n── NEW (2nd call): same schema ──")
    new_result2, _, new_latency2 = extract_new_way()
    print(f"Latency: {new_latency2:.2f}s (cached grammar)")
    
    # Compare
    print(f"\n{'=' * 70}")
    print("Comparison:")
    print(f"  Old latency:           {old_latency:.2f}s")
    print(f"  New 1st latency:       {new_latency1:.2f}s")
    print(f"  New 2nd latency:       {new_latency2:.2f}s (after cache)")
    print(f"  Same output?           {old_result == new_result1 if old_result else 'N/A'}")


if __name__ == "__main__":
    asyncio.run(main())