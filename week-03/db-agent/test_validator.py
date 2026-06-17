"""
Adversarial test cases for SQL validator.
"""
from sql_validator import validate_sql, SQLValidationError


TEST_CASES = [
    # === Valid queries (should PASS) ===
    ("✅", "Simple SELECT",
     "SELECT * FROM products WHERE is_active = 1"),
    
    ("✅", "JOIN allowed tables",
     "SELECT p.name, c.name FROM products p JOIN categories c ON p.category_id = c.id"),
    
    ("✅", "Subquery same scope",
     "SELECT name FROM products WHERE id IN (SELECT product_id FROM inventory WHERE quantity > 0)"),
    
    ("✅", "Aggregation + GROUP BY",
     "SELECT branch_id, SUM(total_amount) FROM distribution_orders GROUP BY branch_id"),
    
    # === Should FAIL ===
    ("❌", "INSERT (DML)",
     "INSERT INTO products (name) VALUES ('hack')"),
    
    ("❌", "UPDATE (DML)",
     "UPDATE products SET selling_price = 0"),
    
    ("❌", "DELETE (DML)",
     "DELETE FROM products WHERE id = 1"),
    
    ("❌", "DROP TABLE (DDL)",
     "DROP TABLE products"),
    
    ("❌", "TRUNCATE",
     "TRUNCATE TABLE products"),
    
    ("❌", "Multi-statement injection",
     "SELECT * FROM products; DROP TABLE products"),
    
    ("❌", "Blocked table — users",
     "SELECT * FROM users"),
    
    ("❌", "JOIN with blocked table",
     "SELECT p.name FROM products p JOIN users u ON p.created_by = u.id"),
    
    ("❌", "Subquery from blocked table",
     "SELECT * FROM products WHERE created_by IN (SELECT id FROM users WHERE role='admin')"),
    
    ("❌", "UNION sneak with blocked table",
     "SELECT id, name FROM products UNION SELECT id, password FROM users"),
    
    ("❌", "ALTER",
     "ALTER TABLE products ADD COLUMN backdoor TEXT"),
    
    ("❌", "Long query (overflow)",
     "SELECT " + "x," * 3000 + " name FROM products"),
]


def main():
    pass_count = 0
    fail_count = 0
    correct = 0

    for expected, label, sql in TEST_CASES:
        sql_display = sql[:60] + "..." if len(sql) > 60 else sql
        
        try:
            validate_sql(sql)
            actual = "✅"
            error = None
        except SQLValidationError as e:
            actual = "❌"
            error = str(e)
        
        is_correct = expected == actual
        marker = "✓" if is_correct else "✗ FAIL"
        
        print(f"{marker:8s} {expected} expected, {actual} got | {label}")
        print(f"         SQL: {sql_display}")
        if error:
            print(f"         Reason: {error}")
        print()
        
        if is_correct:
            correct += 1
        if expected == "✅":
            pass_count += 1
        else:
            fail_count += 1

    total = len(TEST_CASES)
    print(f"{'='*70}")
    print(f"Score: {correct}/{total}")
    print(f"  Should pass: {pass_count} | Should fail: {fail_count}")


if __name__ == "__main__":
    main()