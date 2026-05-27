name = "Dogie"
count = 117
cost = 0.009345

# Basic
print(f"Hello, {name}")

# Format spec
print(f"Tokens: {count:,}")              # 117 (comma format ใช้กับเลขใหญ่)
print(f"Cost: ${cost:.4f}")              # $0.0093 (4 decimal)
print(f"Percentage: {0.7891:.1%}")       # 78.9%

# Expression inside
print(f"Cost in baht: {cost * 36:.2f}")  # คำนวณตรงใน f-string

# Multi-line (triple-quoted)
report = f"""
Model: claude-opus-4-7
Input tokens: {count}
Estimated cost: ${cost:.6f}
"""
print(report)

# Debugging shortcut (Python 3.8+) — ใช้บ่อย!
x = 42
print(f"{x=}")        # x=42 (auto label!)
print(f"{count*2=}")  # count*2=234
