from decimal import Decimal

from pydantic import BaseModel, Field


class CartItemInput(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, le=100)


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    name: str
    sku: str
    quantity: int
    unit_price: Decimal
    available_quantity: int


class CartResponse(BaseModel):
    id: int
    items: list[CartItemResponse]
    total: Decimal