# When to use which model (first draft)

## Use Haiku 4.5 (cheap, fast) for:
- Classification, tagging, simple Q&A
- Format conversion (JSON ↔ text, sentence → SQL)
- High-volume background processing (1000s/day)
- Smoke tests in dev
- Initial routing layer (decide "should I escalate to Opus?")

## Use Sonnet 4.6 (balanced) for:
- Production default — most Laravel app features
- RAG generation step (after retrieval)
- Customer-facing chat that needs reasonable quality
- (จะลองตัวนี้ในสัปดาห์ต่อๆ ไป)

## Use Opus 4.7 (premium) for:
- Complex reasoning, multi-step plans
- Critical accuracy required (medical, legal — careful)
- Hard edge cases ที่ Sonnet ตอบไม่ดี
- Code generation ที่ซับซ้อน, long context analysis

## Smart routing pattern (Week 9+):
- Default → Haiku
- Confidence < threshold หรือ task complexity > X → escalate to Sonnet
- Critical path / explicit escalate → Opus


# ควรใช้รุ่นไหน (ร่างแรก)

## ใช้ Haiku 4.5 (ถูก เร็ว) สำหรับ:
- การจำแนกประเภท การแท็ก คำถามและคำตอบง่ายๆ
- การแปลงรูปแบบ (JSON ↔ ข้อความ, ประโยค → SQL)
- การประมวลผลพื้นหลังปริมาณมาก (1,000 วินาที/วัน)
- การทดสอบควันใน dev
- เลเยอร์การกำหนดเส้นทางเริ่มต้น (ตัดสินใจว่า "ฉันควรเพิ่มระดับเป็น Opus หรือไม่")

## ใช้ Sonnet 4.6 (สมดุล) สำหรับ:
- ค่าเริ่มต้นที่ใช้งานจริง — ฟีเจอร์แอป Laravel ส่วนใหญ่
- ขั้นตอนการสร้าง RAG (หลังการดึงข้อมูล)
- การแชทต่อหน้าลูกค้าที่ต้องการคุณภาพที่สมเหตุสมผล
- (จะลองนี่ในสัปดาห์ต่อๆ ไป)

## ใช้ Opus 4.7 (พรีเมียม) สำหรับ:
- การใช้เหตุผลที่ซับซ้อน แผนหลายขั้นตอน
- ต้องการความแม่นยำที่สำคัญ (ทางการแพทย์ กฎหมาย — ระมัดระวัง)
- เคสขอบแข็งที่ Sonnet ตอบไม่ดี
- การสร้างโค้ด วิเคราะห์บริบทแบบยาว

## รูปแบบการกำหนดเส้นทางอัจฉริยะ (สัปดาห์ที่ 9+):
- ค่าเริ่มต้น → Haiku
- ความมั่นใจ < เกณฑ์หรือความซับซ้อนของงาน > X → ยกระดับเป็น Sonnet
- เส้นทางวิกฤต / ยกระดับอย่างชัดเจน → Opus
