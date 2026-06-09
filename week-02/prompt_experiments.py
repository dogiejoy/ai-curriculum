"""
Week 2 — Prompt engineering experiments.
Compare prompt variations side-by-side.
"""
import asyncio
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()
client = AsyncAnthropic()


async def run_prompt(prompt: str, model: str = "claude-haiku-4-5-20251001") -> str:
    """Run one prompt, return text only."""
    response = await client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text

async def compare_prompts(label_a: str, prompt_a: str, label_b: str, prompt_b: str):
    """Run 2 prompt variants in parallel, print side-by-side."""
    print(f"\n{'=' * 75}")
    print(f"COMPARING: {label_a}  vs  {label_b}")
    print('=' * 75)

    result_a, result_b = await asyncio.gather(
        run_prompt(prompt_a),
        run_prompt(prompt_b),
    )

    print(f"\n── {label_a} ──")
    print(result_a)
    print(f"\n── {label_b} ──")
    print(result_b)

async def main():
    
    # Experiment 1: Vague vs Clear

    # Call : Experiment 1
    # await compare_prompts(
    #     label_a="VAGUE",
    #     prompt_a="Write something about our company",
    #     label_b="CLEAR + DIRECT",
    #     prompt_b="""You are writing a 100-word "About Us" section for a vet clinic management software company in Thailand.
    #                 Goals:
    #                 - Mention 3 pain points: inventory management, expiry tracking, regulatory compliance
    #                 - Target audience: small-to-medium vet clinic owners
    #                 - Tone: professional but warm

    #                 Format: 2 paragraphs in Thai, no bullet points""",
    # )
    
    # Experiment 2: Negative vs Positive instructions
    # article = """Laravel Eloquent is the ORM that ships with Laravel framework. It provides an active record implementation.
    #             Each table maps to a model class. The N+1 problem is common — use eager loading with with() to avoid it.
    #             For bulk inserts of 10000+ rows use the query builder instead of Eloquent."""
    
    # Call : Experiment 2
    # await compare_prompts(
    #     label_a="NEGATIVE instructions",
    #     prompt_a=f"""Summarize this article. Don't be too long. Don't include opinions. Don't use jargon.

    #         Article:
    #         {article}""",
    #                 label_b="POSITIVE instructions",
    #                 prompt_b=f"""Summarize this article in exactly 3 sentences.
    #         Use only facts from the article.
    #         Use everyday language a high school student would understand.

    #         Article:
    #         {article}""",
    # )

    # Experiment 3: Zero-shot vs Few-shot classification
    # test_messages = [
    #     "พรุ่งนี้ขอนัดวัคซีนหมาให้ Lucky ตอนบ่ายได้ไหมคะ",
    #     "คุณหมอเปิดวันเสาร์ไหมครับ",
    #     "ผมโทรไปเมื่อวานตั้งหลายรอบ ไม่มีใครรับเลย แย่มาก",
    #     "สั่งยาทำหมันแมว 50 เม็ดครับ จัดส่งวันนี้ได้ไหม",
    #     "🎁 ลุ้นรับ iPhone ฟรี! คลิก link ด้านล่างเลย bit.ly/xxxxx",
    # ]

    # zero_shot_template = """Classify this vet clinic message into ONE category: complaint, inquiry, order, spam

    #     Message: {msg}

    #     Output only the category name."""

    # few_shot_template = """Classify vet clinic messages into ONE category: complaint, inquiry, order, spam

    #     <examples>
    #     <example>
    #     <message>ผมโทรไปเมื่อวานก็ไม่มีใครรับ ทำงานยังไงครับ</message>
    #     <category>complaint</category>
    #     </example>

    #     <example>
    #     <message>คุณหมอเปิดวันเสาร์ไหมครับ</message>
    #     <category>inquiry</category>
    #     </example>

    #     <example>
    #     <message>สั่งยาทำหมันแมว 50 เม็ดครับ จัดส่งวันนี้ได้ไหม</message>
    #     <category>order</category>
    #     </example>

    #     <example>
    #     <message>🎉 คุณชนะเงินรางวัล! คลิก link ที่นี่</message>
    #     <category>spam</category>
    #     </example>
    #     </examples>

    #     Now classify this message. Output only the category name.

    #     <message>{msg}</message>"""

    # async def classify_test(messages: list[str]):
    #     """Run all messages through both zero-shot and few-shot prompts."""
    #     print(f"\n{'=' * 75}")
    #     print("CLASSIFICATION: Zero-shot vs Few-shot (5 messages)")
    #     print('=' * 75)
        
    #     for i, msg in enumerate(messages, 1):
    #         zero_task = run_prompt(zero_shot_template.format(msg=msg))
    #         few_task = run_prompt(few_shot_template.format(msg=msg))
    #         zero_result, few_result = await asyncio.gather(zero_task, few_task)
            
    #         print(f"\n[{i}] {msg[:60]}{'...' if len(msg) > 60 else ''}")
    #         print(f"    Zero-shot: {zero_result.strip()}")
    #         print(f"    Few-shot:  {few_result.strip()}")

    # Call : Experiment 3
    # await classify_test(test_messages)

    # # Experiment 4: Zero-shot vs Few-shot v1 vs Few-shot v2 (with appointment example)
    # few_shot_v2_template = """Classify vet clinic messages into ONE category: complaint, inquiry, order, spam

    #     <examples>
    #     <example>
    #     <message>ผมโทรไปเมื่อวานก็ไม่มีใครรับ ทำงานยังไงครับ</message>
    #     <category>complaint</category>
    #     </example>

    #     <example>
    #     <message>คุณหมอเปิดวันเสาร์ไหมครับ</message>
    #     <category>inquiry</category>
    #     </example>

    #     <example>
    #     <message>พรุ่งนี้ขอนัดตรวจแมวตอน 10 โมงได้ไหม</message>
    #     <category>inquiry</category>
    #     </example>

    #     <example>
    #     <message>สั่งยาทำหมันแมว 50 เม็ดครับ จัดส่งวันนี้ได้ไหม</message>
    #     <category>order</category>
    #     </example>

    #     <example>
    #     <message>ขอสั่งอาหารแมว Royal Canin 5kg 2 ถุงครับ</message>
    #     <category>order</category>
    #     </example>

    #     <example>
    #     <message>🎉 คุณชนะเงินรางวัล! คลิก link ที่นี่</message>
    #     <category>spam</category>
    #     </example>
    #     </examples>

    #     Now classify this message. Output only the category name.

    #     <message>{msg}</message>"""

    # async def classify_abc(messages: list[str]):
    #     """A/B/C: zero-shot vs few-shot v1 vs few-shot v2."""
    #     print(f"\n{'=' * 75}")
    #     print("A/B/C TEST: Zero-shot | Few-shot v1 | Few-shot v2 (with appointment example)")
    #     print('=' * 75)
        
    #     for i, msg in enumerate(messages, 1):
    #         # Run all 3 variants in parallel
    #         zero, v1, v2 = await asyncio.gather(
    #             run_prompt(zero_shot_template.format(msg=msg)),
    #             run_prompt(few_shot_template.format(msg=msg)),
    #             run_prompt(few_shot_v2_template.format(msg=msg)),
    #         )
            
    #         print(f"\n[{i}] {msg[:60]}{'...' if len(msg) > 60 else ''}")
    #         print(f"    Zero-shot:   {zero.strip()}")
    #         print(f"    Few-shot v1: {v1.strip()}")
    #         print(f"    Few-shot v2: {v2.strip()}")
    
    # Call : Experiment 4
    # await classify_abc(test_messages)

    # Experiment 5: No-CoT vs Basic CoT vs Structured CoT
    # math_problem = """คลินิกแห่งหนึ่งรับสัตว์ 100 ตัวต่อสัปดาห์ เป็นแมว 60% สุนัข 40%
    #     ลูกค้าส่วนใหญ่มาจากย่านอารีย์และทองหล่อ คลินิกเปิด 6 วันต่อสัปดาห์
    #     ราคาวัคซีนปกติ 400 บาท ในจำนวนแมว 25% เป็นแมวพันธุ์เปอร์เซีย
    #     แมวพันธุ์เปอร์เซียได้ส่วนลด 20% เจ้าของแมวพันธุ์เปอร์เซียมักนำลูกหลายตัวมาด้วย
    #     ถ้าทุกตัวฉีดวัคซีน รายได้รวมต่อสัปดาห์เท่าไหร่?"""

    # no_cot_prompt = f"""{math_problem}

    #     ตอบเป็นตัวเลขรายได้รวม (บาท) เท่านั้น"""

    # basic_cot_prompt = f"""{math_problem}

    #     คิดทีละขั้นตอนก่อน แล้วตอบรายได้รวม (บาท)"""

    # structured_cot_prompt = f"""{math_problem}

    #     วิเคราะห์ในแท็ก <thinking> แล้วตอบสุดท้ายในแท็ก <answer> เป็นตัวเลขเท่านั้น

    #     ตัวอย่าง format:
    #     <thinking>
    #     1. คำนวณ X = ...
    #     2. คำนวณ Y = ...
    #     </thinking>
    #     <answer>12345</answer>"""

    # async def cot_compare():
    #     """Compare 3 CoT levels on same math problem."""
    #     print(f"\n{'=' * 75}")
    #     print("CoT COMPARISON: No-CoT vs Basic CoT vs Structured CoT")
    #     print(f"Correct answer: 38,800 บาท")
    #     print('=' * 75)

    #     # Use full client to also get token usage
    #     async def run_with_usage(prompt: str):
    #         response = await client.messages.create(
    #             model="claude-haiku-4-5-20251001",
    #             max_tokens=2048,
    #             messages=[{"role": "user", "content": prompt}],
    #         )
    #         return {
    #             "text": response.content[0].text,
    #             "in_tokens": response.usage.input_tokens,
    #             "out_tokens": response.usage.output_tokens,
    #         }

    #     no_cot, basic, structured = await asyncio.gather(
    #         run_with_usage(no_cot_prompt),
    #         run_with_usage(basic_cot_prompt),
    #         run_with_usage(structured_cot_prompt),
    #     )

    #     for label, result in [
    #         ("NO-CoT", no_cot),
    #         ("BASIC CoT (think step by step)", basic),
    #         ("STRUCTURED CoT (<thinking> tags)", structured),
    #     ]:
    #         print(f"\n── {label} ──")
    #         print(f"Output ({result['out_tokens']} tokens):")
    #         print(result["text"][:500])
    #         if len(result["text"]) > 500:
    #             print(f"... [truncated, total {len(result['text'])} chars]")

    # # Call : Experiment 5
    # await cot_compare()

    # Experiment 6: Without XML structure vs With XML structure
    # review_text = """ซื้อยาฆ่าเห็บมาจากคลินิกนี้ตั้ง 3 อาทิตย์แล้ว แต่หมายังเกาหนักมาก
    #     สงสัยจะไม่ work หรือเปล่า ราคาก็แพงกว่าที่อื่น 200 บาท พนักงานน่ารักดีนะ
    #     แต่คุณหมอดูยุ่งๆ ไม่ค่อยตอบคำถาม คงไม่มาอีกแล้ว"""

    # clinic_context = """คลินิกสัตว์ขนาดเล็ก ย่านอารีย์ เปิดมา 2 ปี
    #     มีหมอประจำ 1 คน ผู้ช่วย 2 คน
    #     ขาย product + treatment"""


    # prompt_no_xml = f"""วิเคราะห์ review ของลูกค้าจากบริบทคลินิกนี้ ตอบ sentiment overall, top 3 issues, และ 2 recommendations

    #     Context: {clinic_context}

    #     Review: {review_text}

    #     ตอบเป็น JSON: {{"sentiment": "positive/neutral/negative", "issues": [...], "recommendations": [...]}}"""


    # prompt_with_xml = f"""<context>
    #     {clinic_context}
    #     </context>

    #     <review>
    #     {review_text}
    #     </review>

    #     วิเคราะห์ review จากบริบทคลินิก ตอบในรูปแบบ:

    #     <output>
    #     <sentiment>positive | neutral | negative</sentiment>
    #     <issues>
    #     <issue>...</issue>
    #     <issue>...</issue>
    #     <issue>...</issue>
    #     </issues>
    #     <recommendations>
    #     <recommendation>...</recommendation>
    #     <recommendation>...</recommendation>
    #     </recommendations>
    #     </output>"""


    # async def xml_compare():
    #     print(f"\n{'=' * 75}")
    #     print("XML STRUCTURE: No tags vs With tags")
    #     print('=' * 75)

    #     no_xml, with_xml = await asyncio.gather(
    #         run_prompt(prompt_no_xml),
    #         run_prompt(prompt_with_xml),
    #     )

    #     print(f"\n── NO XML ──\n{no_xml}")
    #     print(f"\n── WITH XML ──\n{with_xml}")


    # # ใน main() เพิ่ม:
    # await xml_compare()

    # Experiment 7: No system prompt vs With well-crafted system prompt
    # user_question = "หมาผมท้องเสีย 2 วันแล้ว ให้ยาอะไรดี"

    # vet_clinic_system = """คุณเป็น AI assistant ของคลินิกสัตวแพทย์ "PetCare Vet Clinic" ในไทย

    #     บทบาท:
    #     - ตอบคำถามเบื้องต้นเกี่ยวกับการดูแลสัตว์เลี้ยง
    #     - แนะนำเมื่อต้องพบสัตวแพทย์
    #     - ให้ข้อมูลคลินิก: เปิด 9:00-20:00 ทุกวัน, นัดล่วงหน้าผ่าน LINE @petcare

    #     กฎห้ามทำ:
    #     - ห้าม diagnose โรคหรือสั่งยาเอง — ทุกอาการต้อง refer ให้สัตวแพทย์
    #     - ห้ามให้ dosage หรือชื่อยา specific
    #     - ห้ามรับประกันผลการรักษา

    #     กฎต้องทำ:
    #     - ถ้าอาการรุนแรง (อาเจียน 3+ ครั้ง, ไม่กินอาหาร 24ชม.+, เลือดออก, ซึม) — แนะนำมาคลินิกทันที
    #     - ถามอาการเพิ่มเติม (ระยะเวลา, น้ำหนัก, พฤติกรรม) ก่อนแนะนำ
    #     - ใช้ภาษาไทย warm + professional
    #     - ตอบกระชับ ไม่เกิน 5 ประโยค

    #     Format: text ธรรมดา ไม่ใช้ markdown"""

    # async def system_prompt_compare():
    #     """Compare same user question with/without system prompt."""
    #     print(f"\n{'=' * 75}")
    #     print("SYSTEM PROMPT: None vs Vet clinic assistant")
    #     print(f"Question: {user_question}")
    #     print('=' * 75)

    #     # No system prompt
    #     no_sys_task = client.messages.create(
    #         model="claude-haiku-4-5-20251001",
    #         max_tokens=512,
    #         messages=[{"role": "user", "content": user_question}],
    #     )
        
    #     # With system prompt
    #     with_sys_task = client.messages.create(
    #         model="claude-haiku-4-5-20251001",
    #         max_tokens=512,
    #         system=vet_clinic_system,
    #         messages=[{"role": "user", "content": user_question}],
    #     )
        
    #     no_sys_resp, with_sys_resp = await asyncio.gather(no_sys_task, with_sys_task)
        
    #     print(f"\n── NO SYSTEM PROMPT ──")
    #     print(no_sys_resp.content[0].text)
    #     print(f"\n[in: {no_sys_resp.usage.input_tokens}, out: {no_sys_resp.usage.output_tokens}]")
        
    #     print(f"\n── WITH SYSTEM PROMPT ──")
    #     print(with_sys_resp.content[0].text)
    #     print(f"\n[in: {with_sys_resp.usage.input_tokens}, out: {with_sys_resp.usage.output_tokens}]")

    # # ใน main() เพิ่ม:
    # await system_prompt_compare()

    # Experiment 8: Without prefill vs With prefill (force JSON)
    # extract_task = """ดึงข้อมูลต่อไปนี้จากใบเสร็จและตอบเป็น JSON:
    #     - vendor: ชื่อร้าน
    #     - date: วันที่
    #     - total: ยอดรวม (ตัวเลข)

    #     ใบเสร็จ:
    #     ร้านยา PetCare เลขที่ 123 ถ.อารีย์
    #     วันที่: 5/6/2026
    #     รายการ:
    #     - Frontline Plus 1 ขวด - 850.00
    #     - อาหารแมว 2 กก. - 320.00
    #     รวม: 1,170.00 บาท
    #     """

    # async def prefill_compare():
    #     print(f"\n{'=' * 75}")
    #     print("PREFILL: Without vs With")
    #     print('=' * 75)

    #     # Without prefill
    #     no_prefill_task = client.messages.create(
    #         model="claude-haiku-4-5-20251001",
    #         max_tokens=256,
    #         messages=[{"role": "user", "content": extract_task}],
    #     )
        
    #     # With prefill (force start with {)
    #     with_prefill_task = client.messages.create(
    #         model="claude-haiku-4-5-20251001",
    #         max_tokens=256,
    #         messages=[
    #             {"role": "user", "content": extract_task},
    #             {"role": "assistant", "content": "{"},  # ← prefill
    #         ],
    #     )
        
    #     no_prefill, with_prefill = await asyncio.gather(no_prefill_task, with_prefill_task)
        
    #     print(f"\n── WITHOUT PREFILL ──")
    #     print(no_prefill.content[0].text)
        
    #     print(f"\n── WITH PREFILL ──")
    #     # ใส่ { กลับมาที่ output (เพราะ prefill ไม่อยู่ใน response)
    #     print("{" + with_prefill.content[0].text)

    # # ใน main() เพิ่ม:
    # await prefill_compare()

    # Experiment 9: Single monolithic prompt vs Chain prompts
    receipt_text = """ร้านยา PetCare เลขที่ 123 ถ.อารีย์
        วันที่: 5/6/2026
        รายการ:
        - Frontline Plus 1 ขวด - 850.00
        - อาหารแมว Royal Canin 5kg - 1,250.00
        - วิตามินสุนัข 60 เม็ด - 450.00
        - ปลอกคอกันเห็บ - 320.00
        - ทรายแมว 10L - 280.00
        รวม: 3,150.00 บาท
        """

    # ===== Approach 1: Single monolithic prompt =====
    monolithic_prompt = f"""วิเคราะห์ใบเสร็จนี้และตอบเป็น JSON ที่มี:
        - vendor: ชื่อร้าน
        - date: วันที่
        - items: รายการสินค้า (array ของ {{name, price}})
        - total: ยอดรวม
        - categories: dict จำแนกสินค้าตามหมวด (parasite_control, food, vitamins, accessories, hygiene)
        - anomaly: ถ้ามียอดผิดปกติ (เช่น item ราคาสูงมาก, total ไม่ตรงกับผลรวม) ระบุ otherwise null

        ใบเสร็จ:
        {receipt_text}

        ตอบเป็น JSON valid เท่านั้น ห้ามมี ```json wrapper หรือ explanation อื่นๆ"""

    # ===== Approach 2: Chain (2 steps) =====
    extract_prompt = f"""ดึงข้อมูลจากใบเสร็จเป็น JSON:
        - vendor, date, items: [{{name, price}}], total

        ใบเสร็จ:
        {receipt_text}

        ตอบเป็น JSON valid เท่านั้น ห้ามมี ```json wrapper หรือ explanation อื่นๆ"""

    async def call_anthropic(prompt: str, model: str) -> str:
        """Auto-select prefill strategy based on model capability."""
        # Models ที่ support prefill (verify ทุกครั้งใน docs)
        supports_prefill = "haiku" in model
        
        if supports_prefill:
            response = await client.messages.create(
                model=model,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": "{"},
                ],
            )
            return "{" + response.content[0].text
        else:
            # Sonnet/Opus 4.6+ → rely on prompt instruction
            # เพิ่ม explicit "ตอบ JSON only ไม่มี markdown" ใน prompt
            response = await client.messages.create(
                model=model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text

    def strip_code_fence(text: str) -> str:
        """Remove ```json ... ``` wrapper if Sonnet/Opus adds it."""
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return text

    def make_analyze_prompt(extracted_json: str) -> str:
        return f"""วิเคราะห์ข้อมูลใบเสร็จที่ extract มาแล้ว เพิ่ม fields:
            - categories: dict จำแนกสินค้าตามหมวด (parasite_control, food, vitamins, accessories, hygiene)
            - anomaly: ระบุถ้ายอด total ไม่ตรงกับผลรวม items หรือมี item ผิดปกติ otherwise null

            ข้อมูลที่ extract:
            {extracted_json}

            ตอบเป็น JSON ที่รวม fields เดิม + 2 fields ใหม่ เริ่มด้วย {{"""

    async def call_with_prefill(prompt: str, model: str = "claude-haiku-4-5-20251001") -> str:
        """Run prompt with prefill = '{' for clean JSON output."""
        response = await client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": "{"},
            ],
        )
        return "{" + response.content[0].text

    async def chain_compare():
        import time

        print(f"\n{'=' * 75}")
        print("MONOLITHIC vs CHAIN — Receipt analysis")
        print('=' * 75)

        # Approach 1: Monolithic (Sonnet without prefill)
        print("\n── MONOLITHIC (Sonnet, 1 call, no prefill) ──")
        t1 = time.time()
        mono_raw = await call_anthropic(monolithic_prompt, "claude-sonnet-4-6")
        mono_result = strip_code_fence(mono_raw)
        print(f"Latency: {time.time() - t1:.2f}s")
        print(mono_result[:600])

        # Approach 2: Chain (Haiku extract → Sonnet analyze)
        print("\n── CHAIN (Haiku extract → Sonnet analyze) ──")
        t2 = time.time()
        extracted = await call_anthropic(extract_prompt, "claude-haiku-4-5-20251001")
        print(f"Step 1 (Haiku extract): {time.time() - t2:.2f}s")
        print(f"Step 1 output:\n{extracted[:300]}")

        t3 = time.time()
        analyzed_raw = await call_anthropic(
            make_analyze_prompt(extracted), "claude-sonnet-4-6"
        )
        analyzed = strip_code_fence(analyzed_raw)
        print(f"\nStep 2 (Sonnet analyze): {time.time() - t3:.2f}s")
        print(f"Total chain latency: {time.time() - t2:.2f}s")
        print(f"\nStep 2 output:\n{analyzed[:600]}")

    # ใน main() เพิ่ม:
    await chain_compare()

if __name__ == "__main__":
    asyncio.run(main())