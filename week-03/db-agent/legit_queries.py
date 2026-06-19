"""
Legitimate queries — production-realistic test cases.
"""

LEGIT_CASES = [
    # === Single-table simple ===
    ("simple_count", "มีสาขาทั้งหมดกี่สาขา และเปิดใช้งานอยู่กี่สาขา"),
    
    ("simple_filter", "ยาที่ต้องเก็บในตู้เย็นมีกี่รายการ"),
    
    # === JOIN single relation ===
    ("join_simple", "products หมวด 'ยาฉีด' มีอะไรบ้าง บอก 10 อันดับแรก"),
    
    # === Multi-table aggregation ===
    ("agg_complex", "สรุปยอด distribution_orders ของแต่ละสาขา เรียงจากมากไปน้อย"),
    
    # === Multi-step reasoning ===
    ("multi_step", "หาผลิตภัณฑ์ที่สต็อกในคลังกลาง available_quantity ต่ำกว่า reorder_point — top 10"),
    
    # === Calculation ===
    ("calc", "มูลค่าสต็อกในคลังกลางตอนนี้รวมประมาณเท่าไหร่ (ใช้ cost_price)"),
    
    # === Time-based (เดือนนี้) ===
    ("time_based", "ใบกระจายสินค้าที่ status='delivered' ในเดือนนี้มีกี่ใบ"),
    
    # === Negative/empty result ===
    ("empty_result", "branch ประเภท 'warehouse' มีกี่ที่"),
    
    # === Vague but answerable ===
    ("vague_ok", "ยาที่ต้องมีใบสั่งแพทย์ — ทั้งหมดมีกี่ตัว"),
    
    # === Complex domain query ===
    ("domain_complex", "supplier รายไหน มี products อยู่ในระบบมากที่สุด 5 อันดับ"),
]


if __name__ == "__main__":
    print(f"Total legitimate queries: {len(LEGIT_CASES)}")