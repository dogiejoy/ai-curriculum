# Sample data — simulate API response
api_results = [
    {"model": "claude-opus-4-7",           "tokens": 117, "cost": 0.009},
    {"model": "claude-sonnet-4-6",         "tokens": 95,  "cost": 0.0014},
    {"model": "claude-haiku-4-5-20251001", "tokens": 88,  "cost": 0.0004},
]

# 1. List comprehension — map
costs = [r["cost"] for r in api_results]
print(costs)

# 2. With filter (if clause)
expensive = [r for r in api_results if r["cost"] > 0.001]
print(expensive)

# 3. With transformation
labels = [f"{r['model'].split('-')[1].title()}: ${r['cost']:.4f}" 
          for r in api_results]
print(labels)
# ['Opus: $0.0090', 'Sonnet: $0.0014', 'Haiku: $0.0004']

# 4. Dict comprehension — สำคัญสำหรับ config + lookup
cost_by_model = {r["model"]: r["cost"] for r in api_results}
print(cost_by_model["claude-opus-4-7"])  # 0.009

# 5. Set comprehension (uncommon แต่มี)
unique_models = {r["model"] for r in api_results}
print(unique_models)

# 6. Generator expression — lazy, memory-efficient
# ใช้กับ data ใหญ่ที่ไม่อยากเก็บใน memory ทั้งหมด
total_cost = sum(r["cost"] for r in api_results)
print(f"Total: ${total_cost:.4f}")

# 7. Nested comprehension — careful, อ่านยาก
matrix = [[r["model"], r["tokens"]] for r in api_results]
print(matrix)
