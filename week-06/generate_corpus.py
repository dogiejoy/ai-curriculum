"""
Week 6 Day 3 — Generate Depot RTB sample corpus via Claude.
Output: JSON list of {id, content, metadata} dicts.
"""
import asyncio
import json
import os
from pathlib import Path
from typing import Literal

from anthropic import AsyncAnthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()
client = AsyncAnthropic()

MODEL = "claude-sonnet-4-6"


# ===== Schema for structured output =====

class DocSpec(BaseModel):
    """Specification for one document to generate."""
    doc_id: str
    doc_type: Literal["product", "faq", "guide"]
    topic: str
    metadata_hints: dict = Field(default_factory=dict)


class GeneratedDoc(BaseModel):
    id: str
    content: str
    metadata: dict


# ===== Corpus specifications (curated for realistic vet WMS) =====

SPECS: list[DocSpec] = [
    # Product catalog (6)
    DocSpec(doc_id="prod_001", doc_type="product", topic="NexGard Spectra 30-60kg dogs — chewable flea/tick/heartworm",
            metadata_hints={"brand": "NexGard", "species": "dog", "category": "parasite_control"}),
    DocSpec(doc_id="prod_002", doc_type="product", topic="Revolution Plus for cats 5-10kg — 6-in-1 topical parasite prevention",
            metadata_hints={"brand": "Revolution", "species": "cat", "category": "parasite_control"}),
    DocSpec(doc_id="prod_003", doc_type="product", topic="Royal Canin Renal SO wet food — prescription diet for cats with kidney disease",
            metadata_hints={"brand": "Royal Canin", "species": "cat", "category": "food", "requires_prescription": True}),
    DocSpec(doc_id="prod_004", doc_type="product", topic="Bravecto Plus injectable for cats — 2-month tick/flea/heartworm protection",
            metadata_hints={"brand": "Bravecto", "species": "cat", "category": "parasite_control", "cold_chain": True}),
    DocSpec(doc_id="prod_005", doc_type="product", topic="Metacam oral suspension 32ml — NSAID pain relief for dogs",
            metadata_hints={"brand": "Metacam", "species": "dog", "category": "medication", "requires_prescription": True}),
    DocSpec(doc_id="prod_006", doc_type="product", topic="Hill's Science Diet Adult Sensitive Stomach for dogs 12kg",
            metadata_hints={"brand": "Hill's", "species": "dog", "category": "food"}),

    # FAQ documents (4)
    DocSpec(doc_id="faq_002", doc_type="faq", topic="Ordering process, payment terms, and account setup for new clinic branches",
            metadata_hints={"topic": "ordering"}),
    DocSpec(doc_id="faq_003", doc_type="faq", topic="Cold-chain products handling, storage requirements, and quality guarantee",
            metadata_hints={"topic": "cold_chain"}),
    DocSpec(doc_id="faq_004", doc_type="faq", topic="Prescription drug ordering — required documentation and controlled substance protocols",
            metadata_hints={"topic": "prescription"}),
    DocSpec(doc_id="faq_005", doc_type="faq", topic="Return policy, product warranty, and damaged goods claims",
            metadata_hints={"topic": "returns"}),

    # Operation guides (3)
    DocSpec(doc_id="guide_001", doc_type="guide", topic="Emergency stock request procedure for urgent clinical needs — after-hours contact and priority shipping",
            metadata_hints={"topic": "emergency_stock"}),
    DocSpec(doc_id="guide_002", doc_type="guide", topic="Monthly inventory count SOP for clinic branches — what to count, how to reconcile discrepancies",
            metadata_hints={"topic": "inventory_count"}),
    DocSpec(doc_id="guide_003", doc_type="guide", topic="Vaccine storage protocol — temperature monitoring, breach reporting, and viability testing",
            metadata_hints={"topic": "vaccine_storage"}),
]


# ===== Generation prompts =====

SYSTEM_PROMPT = """คุณเป็น content writer สำหรับ Depot RTB — warehouse ที่จัดจำหน่ายสินค้าสัตวแพทย์ในไทย

หน้าที่: สร้างเอกสารตามที่ user กำหนด format และเนื้อหาให้ realistic สำหรับ vet clinic operations

กฎ:
- ภาษาไทยเป็นหลัก มี technical terms อังกฤษได้
- ใช้ markdown format สำหรับ FAQ และ guide (headings, lists)
- Product descriptions: 200-400 คำ, มี usage, storage, contraindications ที่ realistic
- FAQ: 400-700 คำ, มี section headings ชัด
- Guide: 500-800 คำ, step-by-step หรือ SOP structure
- ห้ามใช้ราคาจริง — ใช้ "ราคาตามใบเสนอราคา" แทน
- ห้ามใช้ชื่อคนจริง — ใช้ role แทน (เจ้าหน้าที่, ผู้จัดการคลัง, สัตวแพทย์ประจำสาขา)"""


def build_user_prompt(spec: DocSpec) -> str:
    return f"""สร้างเอกสารประเภท **{spec.doc_type}** เกี่ยวกับ:

{spec.topic}

Metadata hints: {json.dumps(spec.metadata_hints, ensure_ascii=False)}

Format: markdown
Length: ตามที่กำหนดใน system prompt
ตอบ content เอกสารเลย ไม่ต้องมี preamble"""


async def generate_one(spec: DocSpec) -> GeneratedDoc:
    response = await client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_prompt(spec)}],
    )
    content = response.content[0].text.strip()
    return GeneratedDoc(
        id=spec.doc_id,
        content=content,
        metadata={"doc_type": spec.doc_type, "language": "th", **spec.metadata_hints},
    )


async def main():
    print(f"Generating {len(SPECS)} documents in parallel...")
    
    tasks = [generate_one(s) for s in SPECS]
    docs = await asyncio.gather(*tasks)
    
    output_path = Path(__file__).parent / "corpus" / "depot_corpus.json"
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(
        json.dumps([d.model_dump() for d in docs], ensure_ascii=False, indent=2)
    )
    
    # Summary
    print(f"\n{'=' * 65}")
    print(f"Generated {len(docs)} documents → {output_path}")
    print('=' * 65)
    for d in docs:
        print(f"  [{d.metadata['doc_type']:8s}] {d.id} — {len(d.content)} chars")
    
    total_chars = sum(len(d.content) for d in docs)
    print(f"\n  Total: {total_chars:,} chars")


if __name__ == "__main__":
    asyncio.run(main())