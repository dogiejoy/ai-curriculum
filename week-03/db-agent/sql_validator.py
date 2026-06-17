"""
SQL Validator for DB Query Agent.
Enforces:
- SELECT only (no DML/DDL)
- Whitelisted tables only
- Single statement
- Reasonable length
"""
import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError

# Import schema definitions
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from schema_info import SCHEMA


class SQLValidationError(Exception):
    """Raised when SQL violates safety rules."""


ALLOWED_TABLES = set(SCHEMA.keys())


def validate_sql(sql: str, max_length: int = 5000) -> None:
    """
    Validate SQL safety. Raises SQLValidationError if unsafe.
    Pass → return None silently.
    """
    # === Layer 1: Basic checks ===
    sql = sql.strip().rstrip(";")  # Remove trailing semicolon

    if not sql:
        raise SQLValidationError("Empty query")

    if len(sql) > max_length:
        raise SQLValidationError(f"Query too long: {len(sql)} chars (max {max_length})")

    # === Layer 2: Single statement check ===
    if ";" in sql:
        # Could be a string literal with ; — but for our agent, just block
        raise SQLValidationError("Multi-statement queries not allowed (found ';' in body)")

    # === Layer 3: Parse with sqlglot ===
    try:
        parsed = sqlglot.parse_one(sql, read="mysql")
    except ParseError as e:
        raise SQLValidationError(f"Parse error: {e}")

    if parsed is None:
        raise SQLValidationError("Empty parse result")

    # === Layer 4: SELECT only ===
    if not isinstance(parsed, exp.Select):
        raise SQLValidationError(
            f"Only SELECT statements allowed (got {type(parsed).__name__})"
        )

    # === Layer 5: Block dangerous expression types in tree ===
    DANGEROUS_NODES = (
        exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Alter,
        exp.Create, exp.TruncateTable, exp.Grant,  # exp.Revoke,
        exp.Command,  # generic statement
    )
    for node in parsed.walk():
        if isinstance(node, DANGEROUS_NODES):
            raise SQLValidationError(
                f"Forbidden expression: {type(node).__name__}"
            )

    # === Layer 6: Whitelist tables ===
    tables_used = {t.name for t in parsed.find_all(exp.Table)}
    forbidden = tables_used - ALLOWED_TABLES
    if forbidden:
        raise SQLValidationError(
            f"Tables not allowed: {sorted(forbidden)}. "
            f"Allowed tables: {sorted(ALLOWED_TABLES)}"
        )

    # === Pass ===


def is_safe(sql: str) -> tuple[bool, str | None]:
    """Convenience wrapper that returns (ok, error_message)."""
    try:
        validate_sql(sql)
        return True, None
    except SQLValidationError as e:
        return False, str(e)