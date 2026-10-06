from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CartItemInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product_id: int
    quantity: int = Field(ge=1, le=100)


class CartItemUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

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
