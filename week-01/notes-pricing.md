# Cost Optimization Levers (Anthropic API)

## 1. Model selection
- Default Haiku → escalate Sonnet/Opus เมื่อจำเป็น
- ratio Opus:Sonnet:Haiku = 5 : 3 : 1 (base input + output สัดส่วนเท่ากัน)
- ⚠️ Opus 4.7 tokenizer ใหม่: ข้อความเดียวกันกิน token +35% → effective cost สูงกว่า rate
- Empirical check (Day 1 data): blended Opus/Haiku ≈ 6.8x สำหรับ token mix จริง

## 2. Prompt caching
- Cache write: +25% | Cache read: -90%
- Best for: repeated system prompts (RAG, few-shot)
- Break-even (คุ้มทุน) : หลัง 2 calls (คุ้มทุนตั้งแต่การเรียกใช้งานซ้ำครั้งที่ 2 เป็นต้นไป)

## 3. Batch API
- -50% สำหรับ non-realtime
- Best for: eval, bulk processing

## 4. Token efficiency
- Concise prompts + max_tokens limit
- Thai = ~4x tokens ของ English (จาก Day 1)

## Combined example (RAG chatbot ลูกค้า Package A):
- Haiku default + prompt cache + batch eval
- Potential total savings vs naive Opus: ~90%+

### Tier 1 :: Rate limits: Maximum number of requests per minute (RPM) and tokens per minute (TPM)
- Claude Opus Active : RPM = 50, TPM = 500K
- Claude Sonnet Active : RPM = 50, TPM = 30K
- Claude Haiku Active : RPM = 50, TPM = 50K