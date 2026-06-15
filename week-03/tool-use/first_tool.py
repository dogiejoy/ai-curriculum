"""
Week 3 Day 1 — First tool use call.
Demonstrates the full multi-turn loop:
  Claude requests tool → we execute → return result → Claude responds.
"""
import asyncio
import json

from anthropic import AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()
client = AsyncAnthropic()

MODEL = "claude-sonnet-4-6"


# ===== 1. Tool definition (JSON Schema) =====

TOOLS = [
    {
        "name": "get_weather",
        "description": (
            "Get current weather for a city. "
            "Returns temperature, condition, and humidity."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": (
                        "City name and country, e.g., 'Bangkok, Thailand' "
                        "or 'Tokyo, Japan'"
                    ),
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit. Default is celsius.",
                },
            },
            "required": ["location"],
        },
    },
]


# ===== 2. Tool implementation (mock data) =====

MOCK_WEATHER = {
    "bangkok":    {"temp_c": 32, "condition": "Partly cloudy, afternoon storms", "humidity": 78},
    "tokyo":      {"temp_c": 22, "condition": "Clear",  "humidity": 55},
    "chiang mai": {"temp_c": 28, "condition": "Sunny",  "humidity": 65},
    "london":     {"temp_c": 14, "condition": "Rainy",  "humidity": 85},
}


def get_weather(location: str, unit: str = "celsius") -> dict:
    """Mock weather function — in production would call real API."""
    key = location.lower().split(",")[0].strip()
    data = MOCK_WEATHER.get(key, {
        "temp_c": 25, "condition": "Unknown", "humidity": 60
    })

    if unit == "fahrenheit":
        temp = data["temp_c"] * 9 / 5 + 32
        return {
            "location": location,
            "temperature": f"{temp:.1f}°F",
            "condition": data["condition"],
            "humidity": f"{data['humidity']}%",
        }

    return {
        "location": location,
        "temperature": f"{data['temp_c']}°C",
        "condition": data["condition"],
        "humidity": f"{data['humidity']}%",
    }


# ===== 3. Tool dispatcher =====

TOOL_FUNCTIONS = {
    "get_weather": get_weather,
}


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Run the requested tool and return result as JSON string."""
    func = TOOL_FUNCTIONS.get(tool_name)
    if not func:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    try:
        result = func(**tool_input)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ===== 4. Multi-turn conversation loop =====

async def chat_with_tools(user_message: str):
    """Run multi-turn conversation with tool support."""
    messages = [{"role": "user", "content": user_message}]

    print(f"\n{'=' * 65}")
    print(f"USER: {user_message}")
    print('=' * 65)

    turn = 0
    while True:
        turn += 1
        response = await client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )

        print(f"\n── Turn {turn} [stop_reason: {response.stop_reason}] ──")

        # Case 1: Claude finished
        if response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    print(f"\n💬 CLAUDE: {block.text}")
            break

        # Case 2: Claude wants tools
        if response.stop_reason == "tool_use":
            # Save Claude's full response to conversation history
            messages.append({"role": "assistant", "content": response.content})

            # Process each tool call in this turn
            tool_results = []
            for block in response.content:
                if block.type == "text" and block.text:
                    print(f"\n💬 CLAUDE (text): {block.text}")
                if block.type == "tool_use":
                    print(f"\n🔧 TOOL REQUEST")
                    print(f"   name:  {block.name}")
                    print(f"   input: {json.dumps(block.input, ensure_ascii=False)}")

                    result = execute_tool(block.name, block.input)
                    print(f"   ↓ result: {result}")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            # Send all tool results back as next user message
            messages.append({"role": "user", "content": tool_results})
            continue

        # Unexpected stop reason
        print(f"⚠️ Unexpected stop_reason: {response.stop_reason}")
        break


async def main():
    # Test 1: Simple weather query — should trigger 1 tool call
    await chat_with_tools("อากาศกรุงเทพวันนี้เป็นยังไง?")

    # Test 2: Out of scope — should NOT trigger tool
    await chat_with_tools("Python คืออะไร? อธิบายสั้นๆ ใน 2 ประโยค")

    # Test 3: Multi-city — may trigger 2 tool calls (parallel or sequential)
    await chat_with_tools("เทียบอากาศ Bangkok กับ Tokyo ตอนนี้")


if __name__ == "__main__":
    asyncio.run(main())