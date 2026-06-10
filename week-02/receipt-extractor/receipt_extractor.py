"""
Week 2 Friday project — Receipt Extractor.
Vision API + structured extraction with Pydantic validation.
"""
import asyncio
import base64
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Literal

from anthropic import AsyncAnthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError,field_validator, model_validator

load_dotenv()
client = AsyncAnthropic()


ModelName = Literal[
    "claude-opus-4-7",
    "claude-sonnet-4-6",
    "claude-haiku-4-5-20251001",
]

PRICING: dict[str, dict[str, float]] = {
    "claude-opus-4-7":           {"input": 5.00, "output": 25.00},
    "claude-sonnet-4-6":         {"input": 3.00, "output": 15.00},
    "claude-haiku-4-5-20251001": {"input": 1.00, "output":  5.00},
}


# ===== Pydantic schema =====

class ReceiptItem(BaseModel):
    name: str
    quantity: float = Field(default=1.0, gt=0)   # float สำหรับน้ำมัน, น้ำหนัก
    unit_price: float = Field(ge=0)
    line_total: float = Field(ge=0)


class ReceiptData(BaseModel):
    vendor: str = Field(description="Brand name, not legal entity")
    date: str = Field(description="YYYY-MM-DD in CE")
    items: list[ReceiptItem] = Field(min_length=1)
    subtotal: float = Field(ge=0)
    tax: float = Field(default=0.0, ge=0)
    service_charge: float = Field(default=0.0, ge=0)
    total: float = Field(ge=0)
    currency: str = "THB"

    @model_validator(mode="after")
    def check_total_consistency(self) -> "ReceiptData":
        expected = self.subtotal + self.tax + self.service_charge
        if abs(expected - self.total) > 1.0:
            # ไม่ raise — แต่ logical issue
            self._math_consistent = False
        else:
            self._math_consistent = True
        return self
    
    _math_consistent: bool = True

class ExtractionResult(BaseModel):
    filename: str
    model: ModelName
    data: ReceiptData | None = None
    error: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    latency_seconds: float = 0.0


# ===== Image handling =====

def encode_image(path: Path) -> tuple[str, str]:
    """Return (base64_data, media_type)."""
    media_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    media_type = media_type_map.get(path.suffix.lower(), "image/jpeg")
    data = base64.standard_b64encode(path.read_bytes()).decode("utf-8")
    return data, media_type


# ===== Cost calc =====

def calculate_cost(model: ModelName, input_tokens: int, output_tokens: int) -> float:
    rates = PRICING[model]
    return (input_tokens / 1_000_000) * rates["input"] + \
           (output_tokens / 1_000_000) * rates["output"]


# ===== Prompt =====

SYSTEM_PROMPT = """คุณเป็น receipt OCR system สำหรับใบเสร็จไทย

    หน้าที่: ดึงข้อมูล structured จากภาพใบเสร็จ → ตอบเป็น JSON valid

    ## กฎสำคัญ

    1. **Date conversion (พ.ศ. → ค.ศ.)**:
    - ใบเสร็จไทยใช้พุทธศักราช (BE) — convert เป็น CE เสมอ
    - สูตร: CE = BE - 543
    - ตัวอย่าง: 2568 BE = 2025 CE, 2569 BE = 2026 CE
    - ถ้าปี < 2500 → assume CE แล้ว ไม่ต้องแปลง
    - Format: YYYY-MM-DD เสมอ

    2. **Vendor**:
    - ใช้ brand name (เช่น "PT", "Tops", "7-Eleven", "Mo-Mo Paradise")
    - ห้ามใช้ legal entity name ที่อยู่ใน tax info ส่วน (เช่น "บริษัท ... จำกัด")
    - ถ้าไม่มี brand ชัด → ใช้ชื่อสั้นที่สุดที่ identify ร้านได้

    3. **Items**:
    - Extract ทุก line item ที่อ่านได้ — ห้าม collapse เป็น "สินค้า" generic
    - ถ้าอ่านไม่ออก → ใส่ "[unreadable]" + ราคาที่อ่านได้
    - `quantity × unit_price = line_total` ต้องสัมพันธ์
    - กรณีน้ำมัน: quantity = ลิตร (float), unit_price = บาท/ลิตร

    4. **แยก subtotal / tax / service_charge / total**:
    - subtotal = ผลรวม items
    - tax = VAT (ปกติ 7%) — ถ้าใบเสร็จไม่แสดงแยก ใส่ 0
    - service_charge = service (ปกติ 10%) — ถ้าไม่มีใส่ 0
    - total = ยอดสุดท้าย = subtotal + tax + service_charge

    5. **Output**: valid JSON เท่านั้น ห้ามมี ```json wrapper หรือ explanation

    ## ตัวอย่าง

    <example>
    <receipt_description>คาเฟ่ใน Bangkok, 2 รายการ, มี VAT + service, ปี 2568 BE</receipt_description>
    <output>
    {
    "vendor": "Café X",
    "date": "2025-03-15",
    "items": [
        {"name": "Cappuccino", "quantity": 2, "unit_price": 90.0, "line_total": 180.0},
        {"name": "Croissant", "quantity": 1, "unit_price": 80.0, "line_total": 80.0}
    ],
    "subtotal": 260.0,
    "tax": 18.2,
    "service_charge": 26.0,
    "total": 304.2,
    "currency": "THB"
    }
    </output>
    </example>

    <example>
    <receipt_description>ปั๊ม PT, น้ำมัน 1 รายการ, ปี 2569 BE</receipt_description>
    <output>
    {
    "vendor": "PT",
    "date": "2026-06-08",
    "items": [
        {"name": "GASOHOL 95", "quantity": 35.0, "unit_price": 42.86, "line_total": 1500.0}
    ],
    "subtotal": 1500.0,
    "tax": 0.0,
    "service_charge": 0.0,
    "total": 1500.0,
    "currency": "THB"
    }
    </example>"""

USER_PROMPT = "ดึงข้อมูลจากใบเสร็จในภาพนี้ ตอบเป็น JSON ตาม schema"


# ===== Extraction =====

def strip_code_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return text


async def extract_receipt(image_path: Path, model: ModelName) -> ExtractionResult:
    """Extract receipt data from one image using one model."""
    image_data, media_type = encode_image(image_path)
    start = time.time()

    try:
        response = await client.messages.create(
            model=model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": USER_PROMPT,
                    },
                ],
            }],
        )

        latency = time.time() - start
        raw_text = strip_code_fence(response.content[0].text)
        parsed = json.loads(raw_text)
        receipt = ReceiptData(**parsed)

        return ExtractionResult(
            filename=image_path.name,
            model=model,
            data=receipt,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            cost_usd=calculate_cost(
                model, response.usage.input_tokens, response.usage.output_tokens
            ),
            latency_seconds=latency,
        )

    except (json.JSONDecodeError, ValidationError) as e:
        return ExtractionResult(
            filename=image_path.name,
            model=model,
            error=f"{type(e).__name__}: {e}",
            latency_seconds=time.time() - start,
        )
    except Exception as e:
        return ExtractionResult(
            filename=image_path.name,
            model=model,
            error=f"API error: {e}",
            latency_seconds=time.time() - start,
        )

async def extract_with_routing(image_path: Path) -> ExtractionResult:
    """Sonnet default → escalate to Opus if validation issue."""
    result = await extract_receipt(image_path, "claude-sonnet-4-6")
    
    needs_escalation = (
        result.error is not None or
        (result.data and not getattr(result.data, "_math_consistent", True))
    )
    
    if needs_escalation:
        print(f"  ↑ Escalating {image_path.name} to Opus")
        opus_result = await extract_receipt(image_path, "claude-opus-4-7")
        # Track cost ของทั้ง 2 calls
        opus_result.cost_usd += result.cost_usd
        opus_result.latency_seconds += result.latency_seconds
        return opus_result
    
    return result

async def main():
    folder = Path("test-receipts")
    image_files = sorted(
        f for f in folder.iterdir()
        if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")
    )
    print(f"Found {len(image_files)} receipt images")

    # ========== Phase 3: Smart routing บนทั้ง 6 ใบ ==========
    print(f"\n{'=' * 70}")
    print("Phase 3: Smart routing (Sonnet default → Opus on validation fail)")
    print('=' * 70)

    tasks = [extract_with_routing(f) for f in image_files]
    results = await asyncio.gather(*tasks)

    for r in results:
        print(f"\n── {r.filename} ── ({r.model.split('-')[1]})")
        if r.error:
            print(f"  ❌ ERROR: {r.error[:100]}")
            continue
        consistent = getattr(r.data, "_math_consistent", True)
        flag = "✓" if consistent else "⚠️ math inconsistent"
        print(f"  {flag}")
        print(f"  Vendor: {r.data.vendor} | Date: {r.data.date}")
        print(f"  Items:  {len(r.data.items)} | Total: ฿{r.data.total:,.2f}")
        print(f"  Subtotal/Tax/Svc: ฿{r.data.subtotal:.2f} / ฿{r.data.tax:.2f} / ฿{r.data.service_charge:.2f}")
        print(f"  Cost: ${r.cost_usd:.5f} | Latency: {r.latency_seconds:.2f}s")

    # Summary
    total_cost = sum(r.cost_usd for r in results)
    escalated = sum(1 for r in results if r.model == "claude-opus-4-7")
    inconsistent = sum(
        1 for r in results
        if r.data and not getattr(r.data, "_math_consistent", True)
    )

    print(f"\n{'=' * 70}")
    print(f"Smart routing summary:")
    print(f"  Total receipts:        {len(results)}")
    print(f"  Escalated to Opus:     {escalated} ({escalated/len(results)*100:.0f}%)")
    print(f"  Math inconsistent:     {inconsistent}")
    print(f"  Total cost:            ${total_cost:.5f}")
    print(f"  Avg per receipt:       ${total_cost/len(results):.5f}")
    print(f"  Per 1000 receipts:     ${total_cost*1000/len(results):.2f}")

if __name__ == "__main__":
    asyncio.run(main())