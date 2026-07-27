"""
Golden Dataset v2 — expanded with 15 harder questions (Q16-Q30).
Includes multi_hop, ambiguous, no_answer, precise_value question types.

Original 15 questions (Q01-Q15) preserved from Week 6.
"""
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

# Load original dataset
ORIGINAL_PATH = Path(__file__).parent.parent / "week-06" / "golden_dataset.json"
original_data = json.loads(ORIGINAL_PATH.read_text())


@dataclass
class GoldenQuestion:
    id: str
    query: str
    ground_truth_doc_ids: list[str]
    difficulty: Literal["easy", "medium", "hard"]
    doc_type: str  # extended: product, faq, guide, multiple
    language: Literal["th", "en", "mixed"]
    question_type: Literal[
        "single_doc", "multi_hop", "ambiguous", "no_answer", "precise_value"
    ] = "single_doc"
    expected_answer_contains: list[str] = field(default_factory=list)
    expected_refusal: bool = False
    notes: str = ""


# Convert originals — mark as single_doc
ORIGINAL_QUESTIONS = [
    GoldenQuestion(
        id=q["id"],
        query=q["query"],
        ground_truth_doc_ids=q["ground_truth_doc_ids"],
        difficulty=q["difficulty"],
        doc_type=q["doc_type"],
        language=q["language"],
        question_type="single_doc",
        expected_answer_contains=[],  # not defined for v1
        notes=q.get("notes", ""),
    )
    for q in original_data
]


# NEW: 15 expanded questions
NEW_QUESTIONS: list[GoldenQuestion] = [
    # Multi-hop (5)
    GoldenQuestion(
        id="Q16",
        query="ยาป้องกันเห็บสำหรับแมวแบบฉีด ต้องใบสั่งไหม",
        ground_truth_doc_ids=["prod_004", "faq_004"],
        difficulty="medium", doc_type="multiple", language="th",
        question_type="multi_hop",
        expected_answer_contains=["Bravecto Plus", "ใบสั่ง"],
        notes="Product + Rx policy integration",
    ),
    GoldenQuestion(
        id="Q17",
        query="อาหารแมวโรคไต เก็บที่อุณหภูมิเท่าไหร่",
        ground_truth_doc_ids=["prod_003", "faq_003"],
        difficulty="medium", doc_type="multiple", language="th",
        question_type="multi_hop",
        expected_answer_contains=["Royal Canin", "อุณหภูมิ"],
        notes="Product spec + cold-chain policy",
    ),
    GoldenQuestion(
        id="Q18",
        query="Bravecto Plus ต้องส่งเอกสารอะไรบ้างในการสั่ง",
        ground_truth_doc_ids=["prod_004", "faq_004"],
        difficulty="hard", doc_type="multiple", language="th",
        question_type="multi_hop",
        expected_answer_contains=["Bravecto Plus", "ใบอนุญาต"],
        notes="Product-specific docs + Rx documentation",
    ),
    GoldenQuestion(
        id="Q19",
        query="วัคซีนถ้าอุณหภูมิเกินต้องรายงานภายในกี่นาที และใช้แบบฟอร์มอะไร",
        ground_truth_doc_ids=["guide_003"],
        difficulty="hard", doc_type="guide", language="th",
        question_type="multi_hop",
        expected_answer_contains=["15", "BREACH-RPT-03"],
        notes="2 facts from same guide — timing + form ID",
    ),
    GoldenQuestion(
        id="Q20",
        query="สั่งซื้อ Metacam ต้องเตรียมอะไรบ้าง และจัดส่งกี่วัน",
        ground_truth_doc_ids=["prod_005", "faq_004", "faq_002"],
        difficulty="hard", doc_type="multiple", language="th",
        question_type="multi_hop",
        expected_answer_contains=["Metacam", "ใบสั่ง", "จัดส่ง"],
        notes="3-doc integration",
    ),
    
    # Ambiguous (5)
    GoldenQuestion(
        id="Q21",
        query="อาหารสำหรับสุนัข",
        ground_truth_doc_ids=["prod_006"],
        difficulty="medium", doc_type="product", language="th",
        question_type="ambiguous",
        expected_answer_contains=["Hill's", "Sensitive Stomach"],
        notes="prod_003 is CAT food — test species disambiguation",
    ),
    GoldenQuestion(
        id="Q22",
        query="ยาสำหรับสุนัขที่มีอาการอักเสบ",
        ground_truth_doc_ids=["prod_005"],
        difficulty="medium", doc_type="product", language="th",
        question_type="ambiguous",
        expected_answer_contains=["Metacam", "NSAID"],
        notes="Anti-inflammatory keyword ambiguity",
    ),
    GoldenQuestion(
        id="Q23",
        query="สินค้าที่ต้องเก็บเย็น",
        ground_truth_doc_ids=["prod_004", "faq_003"],
        difficulty="medium", doc_type="multiple", language="th",
        question_type="ambiguous",
        expected_answer_contains=["Bravecto Plus", "cold-chain"],
        notes="Test metadata-aware retrieval",
    ),
    GoldenQuestion(
        id="Q24",
        query="การสั่งซื้อทำยังไง",
        ground_truth_doc_ids=["faq_002"],
        difficulty="easy", doc_type="faq", language="th",
        question_type="ambiguous",
        expected_answer_contains=["account", "สั่งซื้อ"],
        notes="Broad ordering query",
    ),
    GoldenQuestion(
        id="Q25",
        query="ยาป้องกันสำหรับสัตว์เลี้ยง",
        ground_truth_doc_ids=["prod_001", "prod_002", "prod_004"],
        difficulty="hard", doc_type="product", language="th",
        question_type="ambiguous",
        expected_answer_contains=["NexGard", "Revolution", "Bravecto"],
        notes="Broad query should list multiple parasite control products",
    ),
    
    # No-answer (3)
    GoldenQuestion(
        id="Q26",
        query="Metacam ราคาต่อขวดเท่าไหร่",
        ground_truth_doc_ids=[],
        difficulty="medium", doc_type="product", language="th",
        question_type="no_answer",
        expected_refusal=True,
        notes="Corpus omits prices",
    ),
    GoldenQuestion(
        id="Q27",
        query="สาขาไหนของ Depot RTB มีสต็อกวัคซีน rabies เยอะสุด",
        ground_truth_doc_ids=[],
        difficulty="hard", doc_type="faq", language="th",
        question_type="no_answer",
        expected_refusal=True,
        notes="No inventory data",
    ),
    GoldenQuestion(
        id="Q28",
        query="สั่ง COVID-19 vaccine สำหรับสัตว์ได้ไหม",
        ground_truth_doc_ids=[],
        difficulty="medium", doc_type="product", language="th",
        question_type="no_answer",
        expected_refusal=True,
        notes="Non-existent product",
    ),
    
    # Precise value (2)
    GoldenQuestion(
        id="Q29",
        query="High alarm ตั้งที่กี่องศา",
        ground_truth_doc_ids=["guide_003"],
        difficulty="medium", doc_type="guide", language="th",
        question_type="precise_value",
        expected_answer_contains=["+9°C", "9"],
        notes="Specific threshold value",
    ),
    GoldenQuestion(
        id="Q30",
        query="Metacam Loading dose คือกี่ mg per kg",
        ground_truth_doc_ids=["prod_005"],
        difficulty="medium", doc_type="product", language="mixed",
        question_type="precise_value",
        expected_answer_contains=["0.2 mg/kg", "0.2"],
        notes="Specific dose value",
    ),
]


ALL_QUESTIONS = ORIGINAL_QUESTIONS + NEW_QUESTIONS


def summary():
    from collections import Counter
    print(f"Total: {len(ALL_QUESTIONS)}")
    print(f"By type: {dict(Counter(q.question_type for q in ALL_QUESTIONS))}")
    print(f"By difficulty: {dict(Counter(q.difficulty for q in ALL_QUESTIONS))}")
    print(f"Expected refusals: {sum(1 for q in ALL_QUESTIONS if q.expected_refusal)}")


def save_json(path: str):
    data = [asdict(q) for q in ALL_QUESTIONS]
    Path(path).write_text(
        json.dumps(data, ensure_ascii=False, indent=2)
    )
    print(f"Saved {len(data)} questions → {path}")


if __name__ == "__main__":
    summary()
    save_json(str(Path(__file__).parent / "golden_dataset_v2.json"))