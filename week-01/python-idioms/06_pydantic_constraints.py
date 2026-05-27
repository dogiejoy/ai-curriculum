from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal


class Product(BaseModel):
    # gt, ge, lt, le — number bounds
    # min_length, max_length — string/list length
    # Literal[...] — enum-like restriction
    # Required + constraint
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0, description="Price must be positive") 
    stock: int = Field(ge=0, le=10_000)
    
    # Optional (default None)
    description: Optional[str] = None
    
    # Default value
    currency: str = "THB"
    
    # Literal — restrict values
    status: Literal["active", "discontinued", "out_of_stock"] = "active"


# Valid
p1 = Product(name="Vet Wormer 50mg", price=120.50, stock=45)
print(p1)

# Constraint violation
try:
    p2 = Product(name="", price=-10, stock=-5)
except Exception as e:
    print(f"\nMultiple errors caught:\n{e}")

# Literal restriction
try:
    p3 = Product(name="Test", price=100, stock=10, status="invalid_status")
except Exception as e:
    print(f"\nLiteral error:\n{e}")


# === Real LLM use case ===
class TokenUsage(BaseModel):
    """Validation for usage object from Anthropic API response."""
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    
    # Computed field — Pydantic 2 syntax
    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


usage = TokenUsage(input_tokens=38, output_tokens=117)
print(f"\nUsage: in={usage.input_tokens}, out={usage.output_tokens}, total={usage.total_tokens}")