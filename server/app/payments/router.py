from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.auth import get_current_user, require_admin
from app.core.database import get_db
from app.payments.schemas import PaymentOutcome, PaymentResponse

router = APIRouter(prefix="/api/v1/payments", tags=["Payments"])


@router.post("/{order_id}/attempt", response_model=PaymentResponse)
def attempt_payment(
    order_id: int,
    body: PaymentOutcome,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    order = db.query(models.Order).filter(models.Order.id == order_id, models.Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    existing = db.query(models.Payment).filter(models.Payment.order_id == order_id, models.Payment.idempotency_key == idempotency_key).first()
    if existing:
        return existing
    status_map = {"success": models.PaymentStatus.succeeded, "failure": models.PaymentStatus.failed, "timeout": models.PaymentStatus.timed_out}
    payment_status = status_map.get(body.outcome)
    if not payment_status:
        raise HTTPException(status_code=422, detail="Outcome must be success, failure, or timeout")
    payment = models.Payment(order_id=order_id, amount=order.total, status=payment_status, idempotency_key=idempotency_key)
    db.add(payment)
    if payment_status == models.PaymentStatus.succeeded:
        order.status = models.OrderStatus.paid
    db.commit()
    db.refresh(payment)
    return payment


@router.get("/{order_id}", response_model=list[PaymentResponse])
def list_payments(order_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    query = db.query(models.Payment).join(models.Order).filter(models.Payment.order_id == order_id)
    if current_user.role != models.UserRole.admin:
        query = query.filter(models.Order.user_id == current_user.id)
    return query.order_by(models.Payment.created_at).all()