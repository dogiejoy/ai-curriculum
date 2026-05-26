## Day 1
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

## Day 2
- Parameters มีให้ setting เยอะมาก
- การใช้ Python SDK connect ง่ายกว่าเยอะ
- messages ใช้เป็น multi และสามารถ set role ได้
- Sonnet 4.6 อยู่ตรงกลางระหว่าง Claude Opus 4.7 กับ Claude Haiku 4.5
- Extended thinking : การคิดแบบมีเหตุผลสำหรับงานที่ซับซ้อนและคิดเป็นลำดับขั้นตอน
- Prompt caching ช่วยลดเวลาและค่าใช้จ่ายในการประมวลผลในงานที่ทำซ้ำๆ 

# push 3 concept ที่จะใช้บ่อยใน 16 สัปดาห์
1. Extended thinking — รู้แค่ "คิดเป็นขั้นตอน" ไม่พอ
ต่างจาก chain-of-thought prompting (CoT) ยังไง? 
— CoT คือ prompt ให้ Claude "think step by step" → output ออกมาทั้ง thinking + answer ปนกัน
- Extended thinking → Claude คิดใน separate hidden tokens ที่เราเห็น (หรือไม่เห็น) ได้ผ่าน parameter thinking ก่อนสรุปเป็น final answer
Cost implication: thinking tokens คิดเงิน เหมือน output tokens — งานเดียวกันอาจเสียค่า 2-5x ของ normal call
เมื่อไหร่ใช้คุ้ม: ปัญหาที่ต้อง multi-step reasoning + accuracy สำคัญกว่า cost — เช่น code generation ซับซ้อน, math, multi-hop RAG query
เมื่อไหร่ไม่ใช้: classification, simple Q&A, format conversion → เปลือง

2. Prompt caching — ของชิ้นนี้เปลี่ยน economics ของ business นี้
ในใจคุณจดว่า "ลดเวลาและค่าใช้จ่ายในงานที่ทำซ้ำๆ" — ถูก แต่ scale ของการลด เปลี่ยน business model เลย

ปกติ input tokens คิด full rate (Sonnet 4.6 = $3/M, Opus = $15/M)
Cached input tokens คิดที่ ~10% ของ rate (อ่านยืนยันใน docs)
Cache writes แพงกว่า normal นิดหน่อย (~25%) แต่ break-even เร็วมาก

Use case ที่ critical สำหรับ Package A:
RAG chatbot ของลูกค้า → system prompt มี:

Instructions (1,000 tokens)
Few-shot examples (2,000 tokens)
Retrieved documents (5,000 tokens)
= 8,000 input tokens ทุก query

ถ้า user ถาม 10 query ติด ๆ ใน session เดียว:

Without cache: 8,000 × 10 × $3 / 1M = $0.24 (just input!)
With cache (first call writes, 9 read): 8,000 × $3.75/M + 8,000 × 9 × $0.30/M = $0.052
ลด ~78% ใน input cost

→ ลูกค้าจ่าย API bill น้อยลง → คุณ market ได้ว่า "เรา cost-engineer" → differentiator
Week 12 จะ deep dive prompt caching อีกที — ตอนนี้แค่จำว่ามี + impact ใหญ่

3. Model aliases vs dated versions
อันนี้ดูเหมือนเรื่องเล็ก แต่ trap ใหญ่ใน production:

Alias เช่น claude-opus-4-7 → Anthropic ชี้ไปยัง latest version ใน family นี้ ถ้าเขา release claude-opus-4-7-XXXXXXXX ใหม่ alias auto-updates
Dated version เช่น claude-haiku-4-5-20251001 → lock ที่ version เฉพาะ ไม่เปลี่ยนแม้ Anthropic ออก minor update

Trade-off:

Alias → ได้ improvements ฟรี แต่ behavior อาจเปลี่ยนนิดหน่อย → eval ที่ pass อาทิตย์ที่แล้วอาจ fail วันนี้
Dated → reproducibility 100% แต่ ตกขบวน improvements + Anthropic อาจ deprecate version เก่า

Production best practice (จะเข้าใจชัดเจน Week 12):

Dev/test → alias OK ลื่นไหล
Production → dated version pin ไว้ + plan upgrade path เป็น sprint งาน
