from fastapi import APIRouter, Depends, Header, Response, status
from sqlalchemy.orm import Session

from app import models
from app.auth import get_current_user
from app.core.database import get_db
from app.payments.schemas import PaymentOutcome, PaymentResponse
from app.payments.service import attempt_payment

router = APIRouter(prefix="/api/v1/payments", tags=["Payments"])


@router.post("/{order_id}/attempt", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment_attempt(
    order_id: int,
    body: PaymentOutcome,
    response: Response,
    idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=8, max_length=128),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Simulate a payment attempt for an order.

    Args:
        order_id: ID of the order to pay for.
        body: Simulated outcome (success, failure, or timeout).
        idempotency_key: Required ``Idempotency-Key`` header, 8-128 characters; reuse safely retries the same outcome.

    Returns:
        The payment attempt (201), or the existing attempt (200) for an identical idempotent retry.

    Raises:
        HTTPException: 401 if unauthenticated, 404 if the order does not exist or is not owned by the user, 409 if the key conflicts or the order is not awaiting payment, or 422 for invalid input.
    """
    payment, created = attempt_payment(db, order_id, current_user, body.outcome, idempotency_key)
    if not created:
        response.status_code = status.HTTP_200_OK
    return payment


@router.get("/{order_id}", response_model=list[PaymentResponse])
def list_payments(order_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """List payment attempts for an order visible to the authenticated user.

    Args:
        order_id: ID of the order whose payment attempts are requested.

    Returns:
        Payment attempts ordered from oldest to newest; an empty list if none are found.

    Raises:
        HTTPException: 401 if unauthenticated or 422 if the order ID is invalid.
    """
    query = db.query(models.Payment).join(models.Order).filter(models.Payment.order_id == order_id)
    if current_user.role != models.UserRole.admin:
        query = query.filter(models.Order.user_id == current_user.id)
    return query.order_by(models.Payment.created_at).all()
