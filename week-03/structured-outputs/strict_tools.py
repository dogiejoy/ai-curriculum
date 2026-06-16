"""
Week 3 Day 2 Block 2 — Strict tool use.
Compare guarantees with strict: True vs non-strict mode.
"""
import asyncio
import json

from anthropic import AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()
client = AsyncAnthropic()
MODEL = "claude-sonnet-4-6"


# ===== Tool with strict mode =====

TOOL_STRICT = {
    "name": "log_inventory_action",
    "strict": True,  # ⭐ ใหม่ — guarantee schema
    "description": "Log an inventory action for a vet clinic product.",
    "input_schema": {
        "type": "object",
        "properties": {
            "product_id": {
                "type": "string",
                "description": "Product ID like P001, P002",
            },
            "action": {
                "type": "string",
                "enum": ["receive", "dispense", "discard", "transfer"],
                "description": "Inventory action type",
            },
            "quantity": {
                "type": "integer",
                "description": "Quantity (positive integer)",
            },
            "reason": {
                "type": "string",
                "description": "Reason for action",
            },
        },
        "required": ["product_id", "action", "quantity", "reason"],
        "additionalProperties": False,
    },
}

TOOL_NON_STRICT = {k: v for k, v in TOOL_STRICT.items() if k != "strict"}


async def call_tool(user_message: str, tool: dict) -> dict | None:
    """Force the tool and return its input."""
    response = await client.messages.create(
        model=MODEL,
        max_tokens=1024,
        tools=[tool],
        tool_choice={"type": "tool", "name": tool["name"]},
        messages=[{"role": "user", "content": user_message}],
    )
    for block in response.content:
        if block.type == "tool_use":
            return block.input
    return None


async def compare(label: str, user_message: str):
    print(f"\n{'=' * 65}")
    print(f"{label}")
    print(f"USER: {user_message}")
    print('=' * 65)

    non_strict, strict = await asyncio.gather(
        call_tool(user_message, TOOL_NON_STRICT),
        call_tool(user_message, TOOL_STRICT),
    )

    print(f"\n── Non-strict ──")
    print(json.dumps(non_strict, ensure_ascii=False, indent=2))
    print(f"\n── Strict ──")
    print(json.dumps(strict, ensure_ascii=False, indent=2))


async def main():
    # Test 1: Clear, well-formed request — both should give same result
    await compare(
        "TEST 1: Clear request",
        "เพิ่งรับ Frontline Plus เข้าสต็อก 50 ขวด รหัส P001 จาก distributor",
    )

    # Test 2: Verb form mismatch — user says "received" (past tense)
    # but enum has "receive" (infinitive)
    await compare(
        "TEST 2: Verb form mismatch (user uses 'received', enum has 'receive')",
        "log inventory: P002 received 30 units, reason: PO #2026-001 delivery",
    )

    # Test 3: Out-of-enum action ("consume" not in [receive/dispense/discard/transfer])
    await compare(
        "TEST 3: Out-of-enum action ('consume' not in allowed list)",
        "บันทึก inventory: P003 consumed 5 units เพราะใช้ในการรักษาผู้ป่วย",
    )

    # Test 4: Missing field — user doesn't mention quantity
    await compare(
        "TEST 4: Missing required field (no quantity)",
        "บันทึก P004 ทิ้ง (discard) เพราะหมดอายุ",
    )


if __name__ == "__main__":
    asyncio.run(main())