"""
Week 6 Golden Dataset — 15 questions with ground-truth doc_id answers.
Used for measuring retrieval quality across 4 chunking strategies.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class GoldenQuestion:
    id: str
    query: str
    ground_truth_doc_ids: list[str]  # Which doc(s) contain the answer
    difficulty: Literal["easy", "medium", "hard"]
    doc_type: Literal["product", "faq", "guide"]
    language: Literal["th", "en", "mixed"]
    notes: str = ""


GOLDEN_QUESTIONS: list[GoldenQuestion] = [
    # === Products (6) ===
    GoldenQuestion(
        id="Q01",
        query="NexGard Spectra สำหรับสุนัขน้ำหนักเท่าไหร่",
        ground_truth_doc_ids=["prod_001"],
        difficulty="easy", doc_type="product", language="th",
    ),
    GoldenQuestion(
        id="Q02",
        query="อาหารแมวโรคไต Royal Canin ต้องใบสั่งไหม",
        ground_truth_doc_ids=["prod_003"],
        difficulty="easy", doc_type="product", language="th",
    ),
    GoldenQuestion(
        id="Q03",
        query="Metacam คือยาอะไร ใช้กับสัตว์ประเภทไหน",
        ground_truth_doc_ids=["prod_005"],
        difficulty="easy", doc_type="product", language="th",
    ),
    GoldenQuestion(
        id="Q04",
        query="ยาป้องกันเห็บสำหรับแมวแบบฉีดตัวไหน",
        ground_truth_doc_ids=["prod_004"],
        difficulty="medium", doc_type="product", language="th",
        notes="Bravecto Plus injectable — form-factor match required",
    ),
    GoldenQuestion(
        id="Q05",
        query="prescription diet สำหรับหมาท้องเสียง่าย",
        ground_truth_doc_ids=["prod_006"],
        difficulty="medium", doc_type="product", language="mixed",
        notes="Hill's Sensitive Stomach — 'prescription' keyword may confuse with prod_003/prod_005",
    ),
    GoldenQuestion(
        id="Q06",
        query="ยาแก้ปวดสำหรับสุนัข ไม่ใช่ steroid",
        ground_truth_doc_ids=["prod_005"],
        difficulty="hard", doc_type="product", language="th",
        notes="Requires understanding NSAID = non-steroid",
    ),
    
    # === FAQs (5) ===
    GoldenQuestion(
        id="Q07",
        query="สาขาใหม่จะเปิด account สั่งซื้อยังไง",
        ground_truth_doc_ids=["faq_002"],
        difficulty="easy", doc_type="faq", language="th",
    ),
    GoldenQuestion(
        id="Q08",
        query="สินค้า cold chain ต้องเก็บอุณหภูมิเท่าไหร่",
        ground_truth_doc_ids=["faq_003"],
        difficulty="easy", doc_type="faq", language="th",
    ),
    GoldenQuestion(
        id="Q09",
        query="ต้องส่งเอกสารอะไรบ้างสำหรับสั่งยาควบคุมพิเศษ",
        ground_truth_doc_ids=["faq_004"],
        difficulty="easy", doc_type="faq", language="th",
    ),
    GoldenQuestion(
        id="Q10",
        query="สินค้าเสียหายตอนขนส่ง ทำยังไง",
        ground_truth_doc_ids=["faq_005"],
        difficulty="medium", doc_type="faq", language="th",
    ),
    GoldenQuestion(
        id="Q11",
        query="เงื่อนไขการชำระเงินสำหรับลูกค้าเก่า",
        ground_truth_doc_ids=["faq_002"],
        difficulty="medium", doc_type="faq", language="th",
        notes="Payment terms mentioned in faq_002 (ordering doc)",
    ),
    
    # === Guides (4) ===
    GoldenQuestion(
        id="Q12",
        query="ต้องนับสต็อกเดือนละครั้งใช่ไหม ทำยังไง",
        ground_truth_doc_ids=["guide_002"],
        difficulty="easy", doc_type="guide", language="th",
    ),
    GoldenQuestion(
        id="Q13",
        query="วัคซีนอุณหภูมิผิด ต้องทำยังไง",
        ground_truth_doc_ids=["guide_003"],
        difficulty="easy", doc_type="guide", language="th",
    ),
    GoldenQuestion(
        id="Q14",
        query="สั่งด่วนหลังเลิกงานได้ไหม",
        ground_truth_doc_ids=["guide_001"],
        difficulty="medium", doc_type="guide", language="th",
    ),
    GoldenQuestion(
        id="Q15",
        query="SOP for temperature excursion incident reporting",
        ground_truth_doc_ids=["guide_003"],
        difficulty="hard", doc_type="guide", language="en",
        notes="English query vs Thai doc — cross-language test",
    ),
]


def summary() -> None:
    from collections import Counter
    print(f"Total questions: {len(GOLDEN_QUESTIONS)}\n")
    print(f"By difficulty: {dict(Counter(q.difficulty for q in GOLDEN_QUESTIONS))}")
    print(f"By doc type:   {dict(Counter(q.doc_type for q in GOLDEN_QUESTIONS))}")
    print(f"By language:   {dict(Counter(q.language for q in GOLDEN_QUESTIONS))}")


if __name__ == "__main__":
    summary()