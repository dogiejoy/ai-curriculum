"""
Week 1 — Compare Opus 4.7 vs Haiku 4.5 on quality, speed, cost.
Goal: build intuition for which model fits which use case.
"""
import time
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

PRICING = {
    "claude-opus-4-7":           {"input": 5.00, "output": 25.00},
    "claude-sonnet-4-6":         {"input": 3.00, "output": 15.00},
    "claude-haiku-4-5-20251001": {"input": 1.00, "output": 5.00},
}

MODELS = ["claude-opus-4-7", "claude-sonnet-4-6", "claude-haiku-4-5-20251001"]

# Test prompts — เลือกให้เห็นความต่าง: factual, technical, reasoning, ภาษาไทย
TEST_PROMPTS = [
    "เมืองหลวงของประเทศไทยคืออะไร? ตอบสั้นๆ",
    "อธิบาย event loop ใน JavaScript ใน 3 ประโยคภาษาไทย",
    "Laravel migration สำหรับ table 'orders' มี columns: id, user_id (FK to users), total (decimal 10,2), status (enum: pending/paid/cancelled). เขียนเป็น code",
    "ถ้า x=3, y=x*2+1, z=y-x และ w=z*z แล้ว w เท่ากับเท่าไหร่? โชว์ขั้นตอนการคิด",
]


def calculate_cost(model, input_tokens, output_tokens):
    rates = PRICING[model]
    return (input_tokens / 1_000_000) * rates["input"] + \
           (output_tokens / 1_000_000) * rates["output"]


def call_model(model: str, prompt: str) -> dict:
    start = time.time()
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    latency = time.time() - start

    return {
        "model": model,
        "text": response.content[0].text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "latency_s": latency,
        "cost_usd": calculate_cost(model, response.usage.input_tokens, response.usage.output_tokens),
    }


def main():
    total_opus_cost = 0.0
    total_haiku_cost = 0.0
    total_sonnet_cost = 0.0

    for i, prompt in enumerate(TEST_PROMPTS, 1):
        print(f"\n{'=' * 75}")
        print(f"[{i}/{len(TEST_PROMPTS)}] PROMPT: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        print('=' * 75)

        results = []
        for model in MODELS:
            short_name = "Opus" if "opus" in model else ("Sonnet" if "sonnet" in model else "Haiku")
            print(f"\n→ {short_name} ({model})")
            try:
                r = call_model(model, prompt)
                results.append(r)
                print(f"  Latency: {r['latency_s']:.2f}s | "
                      f"In/Out tokens: {r['input_tokens']}/{r['output_tokens']} | "
                      f"Cost: ${r['cost_usd']:.5f}")
                print(f"  --- Output ---")
                print(f"  {r['text']}")
            except Exception as e:
                print(f"  ERROR: {e}")

        # Side-by-side comparison
        if len(results) == 3:
            opus, sonnet, haiku = results
            #cost_ratio = opus["cost_usd"] / haiku["cost_usd"] if haiku["cost_usd"] > 0 else 0
            #speed_ratio = opus["latency_s"] / haiku["latency_s"] if haiku["latency_s"] > 0 else 0
            #print(f"\n  → Opus is {cost_ratio:.1f}x more expensive, {speed_ratio:.1f}x slower")
            total_opus_cost += opus["cost_usd"]
            total_haiku_cost += haiku["cost_usd"]
            total_sonnet_cost += sonnet["cost_usd"]


    # Summary
    print(f"\n{'=' * 75}")
    print("TOTAL COST FOR THIS RUN")
    print('=' * 75)
    print(f"  Opus 4.7:  ${total_opus_cost:.5f}")
    print(f"  Sonnet 4.6: ${total_sonnet_cost:.5f}")
    print(f"  Haiku 4.5: ${total_haiku_cost:.5f}")
    print(f"\n  ถ้ารัน 1,000 ครั้งต่อวัน:")
    print(f"    Opus  → ${total_opus_cost * 1000:.2f}/วัน = ${total_opus_cost * 30000:.2f}/เดือน")
    print(f"    Sonnet → ${total_sonnet_cost * 1000:.2f}/วัน = ${total_sonnet_cost * 30000:.2f}/เดือน")
    print(f"    Haiku → ${total_haiku_cost * 1000:.2f}/วัน = ${total_haiku_cost * 30000:.2f}/เดือน")
    print(f"  Difference opus / haiku : {total_opus_cost / total_haiku_cost:.1f}x")
    print(f"  Difference sonnet / haiku: {total_sonnet_cost / total_haiku_cost:.1f}x")



if __name__ == "__main__":
    main()
