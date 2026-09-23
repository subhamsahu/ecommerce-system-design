from pydantic import BaseModel, Field


class InventoryAdjustment(BaseModel):
    product_id: int
    quantity_delta: int = Field(ne=0)
    reason: str = Field(min_length=1, max_length=255)


class InventoryResponse(BaseModel):
    product_id: int
    quantity: int
    low_stock_threshold: int