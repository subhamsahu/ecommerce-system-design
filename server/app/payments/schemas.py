from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    status: str
    amount: Decimal


class PaymentOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid")

    outcome: Literal["success", "failure", "timeout"] = "success"
