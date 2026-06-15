"""
Week 3 Day 1 Block 3 — Multi-tool chain + tool_choice experiments.
"""
import asyncio
import json

from anthropic import AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()
client = AsyncAnthropic()
MODEL = "claude-sonnet-4-6"


# ===== 3 Tools (vet clinic products domain) =====

TOOLS = [
    {
        "name": "search_products",
        "description": (
            "Search for veterinary products by name. "
            "Returns matching products with id, name, and price."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Product name to search"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_inventory",
        "description": (
            "Get current stock quantity for a product. "
            "Call AFTER search_products to get the product_id."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "Product ID returned from search_products",
                },
            },
            "required": ["product_id"],
        },
    },
    {
        "name": "calculate_tax",
        "description": "Calculate VAT tax. Thai VAT rate is 0.07 (7%).",
        "input_schema": {
            "type": "object",
            "properties": {
                "amount": {"type": "number"},
                "rate": {
                    "type": "number",
                    "description": "Tax rate as decimal (e.g. 0.07 for 7%)",
                },
            },
            "required": ["amount"],
        },
    },
]


# ===== Mock data =====

PRODUCTS = {
    "P001": {"name": "Frontline Plus (Dog)", "price": 850.00},
    "P002": {"name": "Frontline Plus (Cat)", "price": 780.00},
    "P003": {"name": "Royal Canin Adult Cat 5kg", "price": 1250.00},
    "P004": {"name": "Bravecto Chewable Tablet", "price": 1850.00},
}

INVENTORY = {"P001": 24, "P002": 11, "P003": 5, "P004": 0}


def search_products(query: str) -> list:
    q = query.lower()
    matches = [
        {"id": pid, **info}
        for pid, info in PRODUCTS.items()
        if q in info["name"].lower()
    ]
    return matches or [{"error": "No products found"}]


def get_inventory(product_id: str) -> dict:
    if product_id not in INVENTORY:
        return {"error": f"Product not found: {product_id}"}
    return {"product_id": product_id, "quantity_in_stock": INVENTORY[product_id]}


def calculate_tax(amount: float, rate: float = 0.07) -> dict:
    tax = amount * rate
    return {
        "amount": amount,
        "rate": rate,
        "tax": round(tax, 2),
        "total_with_tax": round(amount + tax, 2),
    }


TOOL_FUNCTIONS = {
    "search_products": search_products,
    "get_inventory": get_inventory,
    "calculate_tax": calculate_tax,
}


def execute_tool(name: str, args: dict) -> str:
    func = TOOL_FUNCTIONS.get(name)
    if not func:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        return json.dumps(func(**args), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ===== Multi-turn loop with configurable tool_choice =====
MAX_TURNS = 5

async def chat_with_tools(user_message: str, tool_choice: dict | None = None):
    messages = [{"role": "user", "content": user_message}]
    print(f"\n{'=' * 65}")
    print(f"USER: {user_message}")
    print(f"tool_choice: {tool_choice or 'default (auto)'}")
    print('=' * 65)

    turn = 0
    while turn < MAX_TURNS:
        turn += 1
        kwargs = {
            "model": MODEL,
            "max_tokens": 1024,
            "tools": TOOLS,
            "messages": messages,
        }
        # ⭐ Force tool_choice ONLY on first turn — prevent infinite loop
        if tool_choice and turn == 1:
            kwargs["tool_choice"] = tool_choice

        response = await client.messages.create(**kwargs)
        print(f"\n── Turn {turn} [stop_reason: {response.stop_reason}] ──")

        if response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    print(f"\n💬 CLAUDE: {block.text}")
            return

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "text" and block.text:
                    print(f"\n💬 CLAUDE: {block.text}")
                if block.type == "tool_use":
                    print(f"\n🔧 {block.name}({json.dumps(block.input, ensure_ascii=False)})")
                    result = execute_tool(block.name, block.input)
                    print(f"   ↓ {result}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": tool_results})
            continue

        print(f"⚠️ Unexpected stop_reason: {response.stop_reason}")
        return

    # Hit max turns
    print(f"\n⚠️ Hit MAX_TURNS ({MAX_TURNS}) — aborting")

async def main():
    # =====  Experiment 1: Sequential chain (auto) =====
    print("\n" + "▼" * 65)
    print("EXPERIMENT 1: auto + sequential chain")
    print("(search → get product_id → inventory + tax in parallel)")
    print("▼" * 65)
    await chat_with_tools(
        "Frontline Plus สำหรับสุนัขราคาเท่าไหร่ มีของในสต็อกกี่ขวด คำนวณ VAT 7% ด้วย"
    )

    # =====  Experiment 2: tool_choice='any' on chat-only message =====
    print("\n" + "▼" * 65)
    print("EXPERIMENT 2: tool_choice='any' (forces SOME tool)")
    print("Question doesn't need tool — but forced")
    print("▼" * 65)
    await chat_with_tools(
        "สวัสดี วันนี้เป็นอย่างไรบ้าง?",
        tool_choice={"type": "any"},
    )

    # =====  Experiment 3: Force specific tool =====
    print("\n" + "▼" * 65)
    print("EXPERIMENT 3: tool_choice forces calculate_tax")
    print("▼" * 65)
    await chat_with_tools(
        "1000 บาท",
        tool_choice={"type": "tool", "name": "calculate_tax"},
    )

    # =====  Experiment 4: tool_choice='none' =====
    print("\n" + "▼" * 65)
    print("EXPERIMENT 4: tool_choice='none' — tools defined but disabled")
    print("▼" * 65)
    await chat_with_tools(
        "Frontline Plus ราคาเท่าไหร่",
        tool_choice={"type": "none"},
    )


if __name__ == "__main__":
    asyncio.run(main())