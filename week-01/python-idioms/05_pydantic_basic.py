"""
Pydantic basics — runtime validation + serialization.
"""
from pydantic import BaseModel


class User(BaseModel):
    name: str
    age: int
    email: str


# 1. Valid data — works
u1 = User(name="Dogie", age=33, email="dogie@example.com")
print(u1)
# name='Dogie' age=33 email='dogie@example.com'

# 2. String → int auto-coerce (ใส่ "33" Pydantic แปลงให้)
u2 = User(name="Dogie", age="33", email="dogie@example.com")
print(u2.age, type(u2.age))  # 33 <class 'int'>

# 3. Invalid type → ValidationError
try:
    u3 = User(name="Dogie", age="not a number", email="dogie@example.com")
except Exception as e:
    print(f"\nCaught error:\n{e}\n")
    # pydantic.ValidationError: 1 validation error for User
    # age
    #   Input should be a valid integer...

# 4. Missing required field → ValidationError
try:
    u4 = User(name="Dogie")  # missing age + email
except Exception as e:
    print(f"Caught missing field error:\n{e}")

# 5. Serialization — model → dict, dict → json
u5 = User(name="Dogie", age=33, email="dogie@example.com")
print("\nAs dict:", u5.model_dump())
print("As JSON:", u5.model_dump_json())
print("As JSON (indented):", u5.model_dump_json(indent=2))