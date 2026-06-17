"""
Schema info for DB Query Agent.
Defines which tables and columns the agent can access.
"""
from typing import TypedDict


class ColumnDef(TypedDict):
    name: str
    type: str
    description: str
    nullable: bool


class TableDef(TypedDict):
    description: str
    columns: list[ColumnDef]
    foreign_keys: dict[str, str]  # column -> referenced_table


SCHEMA: dict[str, TableDef] = {
    "products": {
        "description": "สินค้าในคลัง (ยา, อาหาร, อุปกรณ์สำหรับสัตวแพทย์)",
        "columns": [
            {"name": "id", "type": "bigint", "description": "Primary key", "nullable": False},
            {"name": "sku", "type": "varchar(50)", "description": "รหัสสินค้า unique", "nullable": False},
            {"name": "barcode", "type": "varchar(100)", "description": "บาร์โค้ด", "nullable": True},
            {"name": "name", "type": "varchar(255)", "description": "ชื่อสินค้า", "nullable": False},
            {"name": "name_en", "type": "varchar(255)", "description": "ชื่อภาษาอังกฤษ", "nullable": True},
            {"name": "name_th", "type": "varchar(255)", "description": "ชื่อภาษาไทย", "nullable": True},
            {"name": "description", "type": "text", "description": "คำอธิบาย", "nullable": True},
            {"name": "category_id", "type": "bigint", "description": "FK → categories", "nullable": True},
            {"name": "supplier_id", "type": "bigint", "description": "FK → suppliers", "nullable": True},
            {"name": "base_unit_id", "type": "bigint", "description": "FK → units", "nullable": False},
            {"name": "registration_number", "type": "varchar(50)", "description": "เลขทะเบียนยา", "nullable": True},
            {"name": "is_controlled_drug", "type": "tinyint", "description": "ยาควบคุมพิเศษ (0/1)", "nullable": False},
            {"name": "require_prescription", "type": "tinyint", "description": "ต้องมีใบสั่งแพทย์ (0/1)", "nullable": False},
            {"name": "active_ingredient", "type": "text", "description": "สารออกฤทธิ์", "nullable": True},
            {"name": "storage_zone_type", "type": "enum", "description": "normal/cold/refrigerated/controlled", "nullable": True},
            {"name": "min_stock_level", "type": "int", "description": "สต็อกขั้นต่ำ", "nullable": False},
            {"name": "reorder_point", "type": "int", "description": "จุดสั่งซื้อใหม่", "nullable": False},
            {"name": "cost_price", "type": "decimal(10,2)", "description": "ราคาทุน", "nullable": True},
            {"name": "selling_price", "type": "decimal(10,2)", "description": "ราคาขาย", "nullable": True},
            {"name": "is_active", "type": "tinyint", "description": "สถานะใช้งาน (0/1)", "nullable": False},
            {"name": "created_at", "type": "timestamp", "description": "วันที่สร้าง", "nullable": True},
            {"name": "updated_at", "type": "timestamp", "description": "วันที่แก้ไข", "nullable": True},
        ],
        "foreign_keys": {
            "category_id": "categories",
            "supplier_id": "suppliers",
            "base_unit_id": "units",
        },
    },
    "categories": {
        "description": "หมวดหมู่สินค้า (มี hierarchy ผ่าน parent_id)",
        "columns": [
            {"name": "id", "type": "bigint", "description": "Primary key", "nullable": False},
            {"name": "parent_id", "type": "bigint", "description": "FK → categories.id (self-reference)", "nullable": True},
            {"name": "code", "type": "varchar(20)", "description": "รหัสหมวดหมู่ unique", "nullable": False},
            {"name": "name", "type": "varchar(100)", "description": "ชื่อหมวดหมู่", "nullable": False},
            {"name": "is_active", "type": "tinyint", "description": "สถานะใช้งาน (0/1)", "nullable": False},
        ],
        "foreign_keys": {"parent_id": "categories"},
    },
    "units": {
        "description": "หน่วยนับสินค้า (ขวด, กล่อง, ml, mg)",
        "columns": [
            {"name": "id", "type": "bigint", "description": "Primary key", "nullable": False},
            {"name": "unit_code", "type": "varchar(20)", "description": "รหัสหน่วย unique", "nullable": False},
            {"name": "unit_name", "type": "varchar(50)", "description": "ชื่อหน่วย", "nullable": False},
            {"name": "unit_type", "type": "enum", "description": "base | packaging", "nullable": False},
            {"name": "is_active", "type": "tinyint", "description": "สถานะใช้งาน (0/1)", "nullable": False},
        ],
        "foreign_keys": {},
    },
    "inventory": {
        "description": "สต็อกในคลังกลาง (per product per batch per location)",
        "columns": [
            {"name": "id", "type": "bigint", "description": "Primary key", "nullable": False},
            {"name": "product_id", "type": "bigint", "description": "FK → products", "nullable": False},
            {"name": "batch_id", "type": "bigint", "description": "Batch reference (opaque ID)", "nullable": True},
            {"name": "location_id", "type": "bigint", "description": "Storage location (opaque ID)", "nullable": False},
            {"name": "quantity", "type": "decimal(10,3)", "description": "จำนวนทั้งหมด (base unit)", "nullable": False},
            {"name": "reserved_quantity", "type": "decimal(10,3)", "description": "จำนวนที่จองไว้", "nullable": False},
            {"name": "available_quantity", "type": "decimal(10,3)", "description": "พร้อมใช้ = quantity - reserved (computed)", "nullable": False},
            {"name": "last_count_date", "type": "date", "description": "วันที่นับสต็อกล่าสุด", "nullable": True},
            {"name": "updated_at", "type": "timestamp", "description": "วันที่ update", "nullable": True},
        ],
        "foreign_keys": {"product_id": "products"},
    },
    "branches": {
        "description": "สาขา/คลินิก (ลูกค้า — ที่รับสินค้าจาก depot)",
        "columns": [
            {"name": "id", "type": "bigint", "description": "Primary key", "nullable": False},
            {"name": "branch_code", "type": "varchar(20)", "description": "รหัสสาขา unique", "nullable": False},
            {"name": "branch_name", "type": "varchar(100)", "description": "ชื่อสาขา", "nullable": False},
            {"name": "branch_type", "type": "enum", "description": "clinic | hospital | retail | warehouse", "nullable": False},
            {"name": "province", "type": "varchar(100)", "description": "จังหวัด", "nullable": True},
            {"name": "district", "type": "varchar(100)", "description": "อำเภอ", "nullable": True},
            {"name": "is_active", "type": "tinyint", "description": "สถานะใช้งาน (0/1)", "nullable": False},
        ],
        "foreign_keys": {},
    },
    "branch_inventory": {
        "description": "สต็อกของแต่ละสาขา (per branch per product per batch)",
        "columns": [
            {"name": "id", "type": "bigint", "description": "Primary key", "nullable": False},
            {"name": "branch_id", "type": "bigint", "description": "FK → branches", "nullable": False},
            {"name": "product_id", "type": "bigint", "description": "FK → products", "nullable": False},
            {"name": "batch_id", "type": "bigint", "description": "Batch reference (opaque)", "nullable": True},
            {"name": "quantity", "type": "decimal(10,3)", "description": "คงเหลือ (base unit)", "nullable": False},
            {"name": "reserved_quantity", "type": "decimal(10,3)", "description": "จองไว้", "nullable": False},
            {"name": "available_quantity", "type": "decimal(10,3)", "description": "พร้อมขาย = quantity - reserved (computed)", "nullable": False},
            {"name": "last_count_date", "type": "date", "description": "วันที่นับล่าสุด", "nullable": True},
            {"name": "updated_at", "type": "timestamp", "description": "วันที่ update", "nullable": True},
        ],
        "foreign_keys": {"branch_id": "branches", "product_id": "products"},
    },
    "distribution_orders": {
        "description": "ใบกระจายสินค้า (depot → branch)",
        "columns": [
            {"name": "id", "type": "bigint", "description": "Primary key", "nullable": False},
            {"name": "do_number", "type": "varchar(50)", "description": "เลขที่ใบกระจายสินค้า unique", "nullable": False},
            {"name": "branch_id", "type": "bigint", "description": "FK → branches", "nullable": False},
            {"name": "order_date", "type": "date", "description": "วันที่สั่ง", "nullable": False},
            {"name": "required_date", "type": "date", "description": "วันที่ต้องการ", "nullable": True},
            {"name": "ship_date", "type": "date", "description": "วันที่จัดส่ง", "nullable": True},
            {"name": "delivery_date", "type": "date", "description": "วันที่ส่งถึง", "nullable": True},
            {"name": "status", "type": "enum", "description": "draft|confirmed|picking|picked|packing|packed|shipped|delivered|cancelled", "nullable": False},
            {"name": "priority", "type": "enum", "description": "low | normal | high | urgent", "nullable": False},
            {"name": "subtotal", "type": "decimal(12,2)", "description": "ยอดรวมก่อนหัก", "nullable": False},
            {"name": "discount", "type": "decimal(12,2)", "description": "ส่วนลด", "nullable": False},
            {"name": "tax", "type": "decimal(12,2)", "description": "ภาษี", "nullable": False},
            {"name": "total_amount", "type": "decimal(12,2)", "description": "ยอดรวมทั้งสิ้น", "nullable": False},
            {"name": "created_at", "type": "timestamp", "description": "วันที่สร้าง", "nullable": True},
        ],
        "foreign_keys": {"branch_id": "branches"},
    },
    "distribution_order_items": {
        "description": "รายการสินค้าใน distribution order",
        "columns": [
            {"name": "id", "type": "bigint", "description": "Primary key", "nullable": False},
            {"name": "do_id", "type": "bigint", "description": "FK → distribution_orders", "nullable": False},
            {"name": "product_id", "type": "bigint", "description": "FK → products", "nullable": False},
            {"name": "batch_id", "type": "bigint", "description": "Batch reference", "nullable": True},
            {"name": "unit_id", "type": "bigint", "description": "FK → units", "nullable": False},
            {"name": "ordered_qty", "type": "decimal(10,3)", "description": "จำนวนที่สั่ง", "nullable": False},
            {"name": "picked_qty", "type": "decimal(10,3)", "description": "จำนวนที่หยิบแล้ว", "nullable": False},
            {"name": "shipped_qty", "type": "decimal(10,3)", "description": "จำนวนที่จัดส่งแล้ว", "nullable": False},
            {"name": "unit_price", "type": "decimal(10,2)", "description": "ราคาต่อหน่วย", "nullable": True},
            {"name": "discount_amount", "type": "decimal(10,2)", "description": "ส่วนลด (บาท)", "nullable": False},
            {"name": "total_price", "type": "decimal(12,2)", "description": "(ordered_qty * unit_price) - discount (computed)", "nullable": False},
        ],
        "foreign_keys": {
            "do_id": "distribution_orders",
            "product_id": "products",
            "unit_id": "units",
        },
    },
    "suppliers": {
        "description": "ผู้จำหน่ายสินค้า (vendors ของ depot) — PII fields excluded",
        "columns": [
            {"name": "id", "type": "bigint", "description": "Primary key", "nullable": False},
            {"name": "supplier_code", "type": "varchar(20)", "description": "รหัสซัพพลายเออร์ unique", "nullable": False},
            {"name": "supplier_name", "type": "varchar(200)", "description": "ชื่อซัพพลายเออร์", "nullable": False},
            {"name": "full_name", "type": "varchar(200)", "description": "ชื่อเต็ม", "nullable": True},
            {"name": "province", "type": "varchar(100)", "description": "จังหวัด", "nullable": True},
            {"name": "district", "type": "varchar(100)", "description": "อำเภอ", "nullable": True},
            {"name": "is_active", "type": "tinyint", "description": "สถานะใช้งาน (0/1)", "nullable": False},
        ],
        "foreign_keys": {},
    },
}


def get_accessible_tables() -> list[str]:
    return list(SCHEMA.keys())


def get_table_info(table: str) -> TableDef | None:
    return SCHEMA.get(table)


def get_allowed_columns(table: str) -> set[str]:
    """For SQL validator — which columns is agent allowed to SELECT?"""
    info = SCHEMA.get(table)
    if not info:
        return set()
    return {col["name"] for col in info["columns"]}


if __name__ == "__main__":
    # Quick verification
    print(f"Total tables: {len(SCHEMA)}")
    for name, info in SCHEMA.items():
        cols = len(info["columns"])
        fks = len(info["foreign_keys"])
        print(f"  {name:30s} {cols} cols, {fks} FKs")