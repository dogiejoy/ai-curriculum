# Week 2 — Prompt Engineering Notes
# Day 1
## Block 1: Be clear and direct

Top 3 takeaways:
1. Specific > vague — "100 words about X with goal Y" > "Write something"
2. Positive > negative — "Use formal tone" > "Don't be casual"
3. Golden rule — show prompt to colleague: ทำตามได้ไหมโดยไม่ต้องถาม

Pattern ที่จะเอาไปใช้ใน week-01 code:
- doc_summarizer SUMMARIZE_PROMPT มี clear principles (specific bullet count, exact JSON format) ครบแล้ว
- compare_models prompts ที่ใช้ทดสอบ — สามารถ refactor ใส่ context + format ชัดเจนขึ้นได้

Workbench experiment finding:
- Experiment 1 :
Vague prompt → generic English boilerplate
Clear prompt with goals + format + audience → Thai 2-paragraph copy ตรงตาม spec
- Experiment 2 :
Negative: Claude อาจจะ "ลืม" บาง constraint (negative instructions ยากกว่า)
Positive: ตอบ 3 ประโยคพอดี ภาษา friendly

## Block 2: Multishot prompting

ให้ Claude ดู examples ก่อนทำ task จริง → accuracy + consistency เพิ่ม โดยเฉพาะงาน classification + structured output

Top 3 takeaways:
- 3-5 examples , XML tags wrap examples
- Examples ต้อง diverse , Bad examples = bad output
- Format teaching — examples บอก "ตอบยังไง" ดีกว่า explanation, Order matters — examples ที่ใกล้ task มากสุดวางท้ายสุด

Key principles:
- 3-5 examples ปกติพอ
- Wrap ด้วย <example>...</example> tags
- Examples ต้อง diverse covering edge cases ของแต่ละ category
- Order: closest to task = last

Pattern แม่บท XML structure:
\```
<examples>
<example>
<input>...</input>
<output>...</output>
</example>
</examples>
\```

Surprising finding:
- v1 few-shot: 4/5 (ผิด appointment booking → order)
- v2 few-shot (+appointment example): 5/5 ✓
- Few-shot ไม่ใช่ silver bullet — examples quality = output quality

Failure mode caught: spurious pattern matching
- "สั่ง...ได้ไหม" → "ขอนัด...ได้ไหม" ถูก infer เป็น order pattern เดียวกัน
- Fix: เพิ่ม appointment booking ที่ inquiry category ให้ explicit

Lessons:
1. Few-shot is not silver bullet — has failure modes
2. Examples must cover edge cases of EACH category
3. Category schema itself may need redesign (appointment ≠ order)
4. Eval framework essential — would catch this regression (Week 9)

Production workflow ที่ทำจริง:
1. Hypothesis → implement → measure → root-cause → fix → verify
2. Examples = production code → version control + eval

Business application:
- Week 4 message classifier — ใช้ pattern นี้แน่ๆ
- Receipt extractor (Day 5) — few-shot examples ของ vendor + amount format
- Doc summarizer — few-shot ให้ bullets follow style เดียวกัน

Cost note:
- 4 examples × 50 tokens = +200 input tokens ต่อ call
- Trade-off: ถ้าใช้ prompt caching → cost เพิ่มน้อย (10% rate)
- ROI: accuracy เพิ่ม → ลูกค้าพอใจ → ลด rework

## Block 3: Chain of thought

Surprising finding:
- Haiku 4.5 ฝ่าฝืน "ตอบตัวเลขเท่านั้น" — ยังคงโชว์ work
- 3 approaches accuracy เท่ากัน (38,800) บนปัญหานี้
- Modern frontier models = CoT internal โดย default

When CoT matters:
- Hard multi-hop reasoning (ไม่ใช่ basic math)
- Auditability requirement
- Format isolation via tags

Production pattern:
- Structured CoT (<thinking>...</thinking><answer>...</answer>) > "step by step" prose
- Parse <answer> tag with regex
- Strip thinking from user-facing output

Cost: +180 output tokens ต่อ call ≈ +$0.0009 บน Haiku
ROI positive ถ้า single wrong answer costs >$1 to fix

## Cross-cutting lessons

1. Format compliance ไม่แน่นอน — ต้องมี post-processing layer
2. ทุก technique มี trade-off — measure before/after, อย่า assume
3. Workbench down → Python script ดีกว่า (reproducible + versioned)

# Day 2
## Block 1 XML tags

Insight: Template structure ≠ count enforcement
- 3 <issue> slots ใน template → model อาจให้ 4-5 ตัว
- ต้อง explicit ใน instruction "exactly 3" ถ้าจำเป็น

Universal pitfall: Claude wrap structured output ใน ```code fences``` แม้ไม่ขอ
- Fix: strip_code_fence() ก่อน parse — ใช้ทุก project

When to use XML vs JSON:
- Strict schema + API/DB → JSON + Pydantic
- Mixed content + analysis → XML
- Tool use → JSON (forced by SDK)
- Thai content → XML นิดเดียวปลอดภัยกว่า (less escaping issues)

## Block 2 Day 2: System prompts

Differential ที่ system prompt ทำงาน:
- Persona ✓ (clinic assistant แทน generic AI)
- Behavior boundaries ✓ (refused to prescribe specific meds)
- Format defaults ✓ (plain text, no markdown)
- Multilingual lock ✓ (Thai only, no random Chinese chars)
- Domain knowledge inject ✓ (offered booking + clinic context)

Business value:
- System prompt = AI personality + safety layer
- = backbone ของ Package A deliverable
- = legal/liability protection สำหรับ vet/medical/financial use cases

Cost economics:
- 500-token system prompt = +$0.0001-0.0002 per call (no cache)
- WITH prompt caching → lower than no-system (cached input -90%)
- → Long system prompts viable only with caching strategy

Production pattern:
- system="..." parameter ใน Anthropic SDK (separate from messages)
- Different from OpenAI which puts system as a message role
- Keep system prompt stable across session → maximizes cache hits

# Day 3
## Tutorial reinforcement

Chapters 1-5 completed (Anthropic Interactive Tutorial):
- Ch 1: Basic prompt structure (familiar)
- Ch 2: Be clear and direct (familiar)
- Ch 3: Role assignment via system prompt (familiar)
- Ch 4: Data + instructions separation via XML (familiar)
- Ch 5: Output formatting + prefilling (NEW pattern: prefilling)

Key new technique from Ch 5: Prefilling Claude's response
- Pre-populate first part of assistant turn → forces format compliance
- Pattern: messages=[{"role": "user", "content": ...},
                   {"role": "assistant", "content": "<expected_start>"}]
- Use case: force JSON, force specific tone, skip preamble
- ⚠️ Production caution: Claude continues from prefill literally — must verify output format

Workflow lessons:
- Concepts from Day 1-2 transferred to tutorial exercises smoothly
- Tutorial value = standardized graders + new pattern (prefilling)

# Day 4
## Prefill + Chain prompts

Prefill response:
- Force JSON output by prefilling assistant message with "{"
- Cleaner output, no markdown wrapper
- ⚠️ Model-specific: Haiku 4.5 ✓, Sonnet 4.6 ❌ (newer models reserve reasoning phase)
- Production pattern: combine with stop_sequences for bounded output

Chain prompts:
- Break monolithic task → focused steps
- ⚠️ Sequential = wall time accumulate (NOT always faster)
- Benefits: quality (focused thinking), debuggability, cost optimization (mix models),
  modularity, caching step outputs for reuse
- Real production value: cache step 1 (extraction) → re-run step 2 (analysis) anytime

Production guidelines:
- Mix models in chain: Haiku for extract (cheap+fast), Sonnet/Opus for reasoning
- Cache extracted data — analyze on demand
- Both steps need explicit JSON instruction (Sonnet doesn't prefill)
- max_tokens needs tuning per step — monolithic needs much more

Lessons:
- Feature support varies by model version → verify in docs per model
- Don't assume cross-model compatibility (Haiku ≠ Sonnet ≠ Opus)
- Chain isn't free — adds latency + code complexity, weigh trade-off

# Day 5
## Project: Receipt Extractor

Pipeline shipped: 6 receipts × vision API + Pydantic + smart routing

Quality findings (Phase 1 → Phase 2 → Phase 3):
- Phase 1 (Sonnet only): 4/6 quality issues — collapsed items, BE date misread, 
  legal vs brand vendor, tax hallucination
- Phase 2 (multi-model): Opus best on date/vendor, Sonnet cautious with [unreadable],
  Haiku DANGEROUS (hallucinated brand 7-Eleven on Tops receipt)
- Phase 3 (smart routing + validator): fixed BE→CE, fixed brand vs legal, BUT
  validator over-triggers on hallucinated tax → 50% escalation = 3.4x cost

Production-critical lessons:
1. Haiku NOT suitable for vision OCR business-critical — hallucinates entities
2. Model invents 7% VAT even when receipt doesn't show — Thai context awareness wrong
3. Smart routing only valuable if validator precision is high
4. Tax/service field extraction = real engineering problem (Thai has multiple patterns)
5. Item granularity trade-off: detail vs honest "[unreadable]"

Cost reality for Package A:
- Sonnet only: $3.82/1000 receipts = ~130 THB/1000
- Smart routing: $12.99/1000 = ~440 THB/1000
- Vet clinic doing ~100 receipts/month = $0.38-1.30/month — easy to absorb

Approach for client work:
- Start simple (Sonnet, no separate tax/svc) → measure pain
- Iterate schema based on real receipt corpus
- Build golden dataset of 30+ verified examples for eval