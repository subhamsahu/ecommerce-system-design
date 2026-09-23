from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class AddressInput(BaseModel):
    line1: str = Field(min_length=1, max_length=200)
    line2: str | None = None
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=1, max_length=100)
    postal_code: str = Field(min_length=1, max_length=20)
    country: str = Field(default="IN", min_length=2, max_length=2)


class CheckoutRequest(BaseModel):
    address: AddressInput


class OrderItemResponse(BaseModel):
    product_name: str
    sku: str
    quantity: int
    unit_price: Decimal


class OrderResponse(BaseModel):
    id: int
    status: str
    currency: str
    total: Decimal
    created_at: datetime
    items: list[OrderItemResponse]


class StatusUpdate(BaseModel):
    status: str