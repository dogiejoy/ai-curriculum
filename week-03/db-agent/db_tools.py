"""
DB tools for Friday's DB Query Agent.
Provides:
- describe_schema(table): structured schema info from schema_info.py
- query_database(sql): validated read-only SQL execution
"""
import json
import os
import sys
from decimal import Decimal
from datetime import date, datetime, time
from pathlib import Path

import pymysql
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
from schema_info import SCHEMA, get_accessible_tables
from sql_validator import validate_sql, SQLValidationError

#load_dotenv()
load_dotenv(Path(__file__).parent.parent.parent / "week-02" / ".env")

# ===== DB Connection =====

def get_connection():
    """Create new connection per call. Production: use connection pool."""
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", 3306)),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_DATABASE"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        read_timeout=10,    # 10s query timeout
        connect_timeout=5,
    )


# ===== Tool 1: describe_schema =====

def describe_schema(table: str) -> dict:
    """Return column metadata + foreign keys for a table.
    
    Returns dict with: table, description, columns, foreign_keys
    Or error dict if table not allowed.
    """
    if table not in SCHEMA:
        return {
            "error": f"Table '{table}' not accessible to agent",
            "allowed_tables": get_accessible_tables(),
        }
    
    info = SCHEMA[table]
    return {
        "table": table,
        "description": info["description"],
        "columns": info["columns"],
        "foreign_keys": info["foreign_keys"],
    }


# ===== Tool 2: query_database =====

MAX_ROWS_RETURNED = 100   # Hard limit


def _json_safe(value):
    """Convert MySQL types to JSON-serializable values."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def query_database(sql: str) -> dict:
    """Validate + execute read-only SELECT.
    
    Returns dict with: rows, row_count, columns
    Or error dict if validation/execution fails.
    """
    # Layer 1: Validate
    try:
        validate_sql(sql)
    except SQLValidationError as e:
        return {"error": f"SQL validation failed: {e}"}
    
    # Layer 2: Execute
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                rows = cursor.fetchmany(MAX_ROWS_RETURNED)
                
                # Convert to JSON-safe
                safe_rows = [
                    {k: _json_safe(v) for k, v in row.items()}
                    for row in rows
                ]
                
                columns = list(safe_rows[0].keys()) if safe_rows else []
                
                return {
                    "rows": safe_rows,
                    "row_count": len(safe_rows),
                    "columns": columns,
                    "truncated": len(safe_rows) == MAX_ROWS_RETURNED,
                }
        finally:
            conn.close()
    
    except pymysql.MySQLError as e:
        return {"error": f"Database error: {e.args[1] if len(e.args) > 1 else e}"}
    except Exception as e:
        return {"error": f"Unexpected error: {type(e).__name__}: {e}"}


# ===== Anthropic tool definitions (for Friday agent) =====

TOOL_DEFINITIONS = [
    {
        "name": "describe_schema",
        "strict": True,
        "description": (
            "Get the schema (columns, types, descriptions, foreign keys) for a table. "
            "Call this BEFORE generating SQL to understand structure. "
            f"Allowed tables: {', '.join(get_accessible_tables())}."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "table": {
                    "type": "string",
                    "description": "Table name to describe (e.g. 'products', 'branches')",
                },
            },
            "required": ["table"],
            "additionalProperties": False,
        },
    },
    {
        "name": "query_database",
        "strict": True,
        "description": (
            "Execute a read-only SELECT SQL query against the database. "
            "Returns matching rows (up to 100). "
            "Only SELECT statements allowed. "
            "Always call describe_schema() FIRST to learn the schema before generating SQL."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": (
                        "SELECT SQL query. Use MySQL syntax. "
                        "JOIN allowed between accessible tables. "
                        "Always include LIMIT for safety."
                    ),
                },
            },
            "required": ["sql"],
            "additionalProperties": False,
        },
    },
]


# ===== Standalone test =====

def test():
    print("=" * 70)
    print("TEST 1: describe_schema")
    print("=" * 70)
    result = describe_schema("products")
    print(f"Description: {result.get('description', 'N/A')}")
    print(f"Columns: {len(result['columns'])}")
    print(f"FKs: {result['foreign_keys']}")
    
    print()
    print("=" * 70)
    print("TEST 2: query_database — simple SELECT")
    print("=" * 70)
    result = query_database("SELECT id, sku, name FROM products LIMIT 5")
    if "error" in result:
        print(f"❌ {result['error']}")
    else:
        print(f"Rows: {result['row_count']}")
        print(json.dumps(result['rows'], ensure_ascii=False, indent=2))
    
    print()
    print("=" * 70)
    print("TEST 3: query_database — JOIN + aggregation")
    print("=" * 70)
    result = query_database("""
        SELECT c.name as category, COUNT(p.id) as product_count
        FROM categories c
        LEFT JOIN products p ON p.category_id = c.id
        GROUP BY c.id, c.name
        ORDER BY product_count DESC
        LIMIT 10
    """)
    if "error" in result:
        print(f"❌ {result['error']}")
    else:
        print(f"Rows: {result['row_count']}")
        print(json.dumps(result['rows'], ensure_ascii=False, indent=2))
    
    print()
    print("=" * 70)
    print("TEST 4: query_database — should FAIL (blocked table)")
    print("=" * 70)
    result = query_database("SELECT * FROM users")
    print(f"Result: {result.get('error', 'PASSED (unexpected!)')}")
    
    print()
    print("=" * 70)
    print("TEST 5: query_database — should FAIL (UPDATE)")
    print("=" * 70)
    result = query_database("UPDATE products SET selling_price = 0")
    print(f"Result: {result.get('error', 'PASSED (unexpected!)')}")


if __name__ == "__main__":
    test()