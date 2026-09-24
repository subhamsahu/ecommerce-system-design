from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.auth import get_current_user
from app.core.database import get_db
from app.payments.schemas import PaymentOutcome, PaymentResponse

router = APIRouter(prefix="/api/v1/payments", tags=["Payments"])

_OUTCOME_STATUS = {
    "success": models.PaymentStatus.succeeded,
    "failure": models.PaymentStatus.failed,
    "timeout": models.PaymentStatus.timed_out,
}


@router.post("/{order_id}/attempt", response_model=PaymentResponse)
def attempt_payment(
    order_id: int,
    body: PaymentOutcome,
    idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=8, max_length=128),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    payment_status = _OUTCOME_STATUS.get(body.outcome)
    if payment_status is None:
        raise HTTPException(status_code=422, detail="Outcome must be success, failure, or timeout.")

    try:
        order = (
            db.query(models.Order)
            .filter(models.Order.id == order_id, models.Order.user_id == current_user.id)
            .with_for_update()
            .first()
        )
        if not order:
            raise HTTPException(status_code=404, detail="Order not found.")

        existing = (
            db.query(models.Payment)
            .filter(
                models.Payment.order_id == order_id,
                models.Payment.idempotency_key == idempotency_key,
            )
            .first()
        )
        if existing:
            if existing.status != payment_status:
                raise HTTPException(
                    status_code=409,
                    detail="Idempotency-Key was already used with a different payment outcome.",
                )
            return existing

        if order.status != models.OrderStatus.pending_payment:
            raise HTTPException(
                status_code=409,
                detail="Payment can only be attempted while an order is pending payment.",
            )

        payment = models.Payment(
            order_id=order_id,
            amount=order.total,
            status=payment_status,
            idempotency_key=idempotency_key,
        )
        db.add(payment)
        if payment_status == models.PaymentStatus.succeeded:
            order.status = models.OrderStatus.paid
            order.history.append(
                models.OrderStatusHistory(
                    from_status=models.OrderStatus.pending_payment.value,
                    to_status=models.OrderStatus.paid.value,
                    changed_by=current_user.id,
                )
            )

        db.commit()
        db.refresh(payment)
        return payment
    except Exception:
        db.rollback()
        raise


@router.get("/{order_id}", response_model=list[PaymentResponse])
def list_payments(order_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    query = db.query(models.Payment).join(models.Order).filter(models.Payment.order_id == order_id)
    if current_user.role != models.UserRole.admin:
        query = query.filter(models.Order.user_id == current_user.id)
    return query.order_by(models.Payment.created_at).all()
