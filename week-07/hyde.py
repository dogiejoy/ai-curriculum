"""
HyDE — generate hypothetical answer to boost retrieval on abstract queries.
"""
from __future__ import annotations
import time
from dataclasses import dataclass

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()


HYDE_SYSTEM_PROMPT = """คุณคือผู้ช่วยที่ตอบคำถามเกี่ยวกับสินค้าและระบบคลังสัตวแพทย์ Depot RTB

Task: อ่านคำถาม แล้วเขียน "คำตอบสมมติ" ที่ **ยังไม่เห็นเอกสารจริง** — จินตนาการว่าเอกสารตอบคำถามนี้จะพูดถึงอะไร

กฎ:
- ตอบให้ครอบคลุมประเด็นที่คำถามน่าจะสนใจ (ชื่อยา, ปริมาณ, วิธีใช้, ราคา, ฯลฯ)
- ใช้ vocabulary ที่เอกสารสัตวแพทย์/คลังสินค้าจะใช้ (technical terms)
- ตอบ 3-5 ประโยค ไม่เกิน 200 คำ
- ห้าม hedge ("อาจจะ", "น่าจะ", "ไม่แน่ใจ") — ตอบแบบมั่นใจ
- ห้ามบอกว่าเป็น hypothetical — ตอบเหมือนรู้จริง
- ภาษาไทยเป็นหลัก, technical terms อังกฤษได้"""


@dataclass
class HyDEResult:
    query: str
    hypothetical_answer: str
    tokens: int
    latency: float
    cost_usd: float


def generate_hyde(query: str, model: str = "claude-haiku-4-5") -> HyDEResult:
    """Generate hypothetical answer for a query."""
    start = time.time()
    response = client.messages.create(
        model=model,
        max_tokens=400,
        system=HYDE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": query}],
    )
    latency = time.time() - start
    
    answer = response.content[0].text.strip()
    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens
    
    # Haiku 4.5: $1/1M input, $5/1M output
    cost = (input_tokens / 1_000_000) * 1.00 + (output_tokens / 1_000_000) * 5.00
    
    return HyDEResult(
        query=query,
        hypothetical_answer=answer,
        tokens=input_tokens + output_tokens,
        latency=latency,
        cost_usd=cost,
    )


if __name__ == "__main__":
    # Quick test
    result = generate_hyde("ยาแก้ปวดสำหรับสุนัข ไม่ใช่ steroid")
    print(f"Query: {result.query}\n")
    print(f"Hypothetical answer:\n{result.hypothetical_answer}\n")
    print(f"Tokens: {result.tokens} | Latency: {result.latency:.2f}s | Cost: ${result.cost_usd:.6f}")