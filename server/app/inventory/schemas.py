from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class InventoryAdjustment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product_id: int
    quantity_delta: int
    reason: str = Field(min_length=1, max_length=255)

    @field_validator("quantity_delta")
    @classmethod
    def adjustment_must_change_quantity(cls, value: int) -> int:
        if value == 0:
            raise ValueError("quantity_delta must not be zero")
        return value


class InventoryResponse(BaseModel):
    product_id: int
    quantity: int
    low_stock_threshold: int


class InventoryMovementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity_delta: int
    reason: str
    reference_type: str | None
    reference_id: str | None
    created_by: int | None
    created_at: datetime
