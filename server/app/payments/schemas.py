from decimal import Decimal
from pydantic import BaseModel


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    status: str
    amount: Decimal


class PaymentOutcome(BaseModel):
    outcome: str = "success"