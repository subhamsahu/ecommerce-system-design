"""Payment-simulator use cases and their transactional state changes."""

import hashlib

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models


OUTCOMES = {
    "success": models.PaymentStatus.succeeded,
    "failure": models.PaymentStatus.failed,
    "timeout": models.PaymentStatus.timed_out,
}


def fingerprint(outcome: str) -> str:
    return hashlib.sha256(outcome.encode()).hexdigest()


def attempt_payment(
    db: Session,
    order_id: int,
    actor: models.User,
    outcome: str,
    idempotency_key: str,
) -> tuple[models.Payment, bool]:
    payment_fingerprint = fingerprint(outcome)
    order = db.query(models.Order).filter(models.Order.id == order_id).with_for_update().first()
    if not order or (actor.role != models.UserRole.admin and order.user_id != actor.id):
        raise HTTPException(status_code=404, detail="Order not found")

    existing = db.query(models.Payment).filter(
        models.Payment.order_id == order_id,
        models.Payment.idempotency_key == idempotency_key,
    ).first()
    if existing:
        if existing.request_fingerprint != payment_fingerprint:
            raise HTTPException(status_code=409, detail="Idempotency-Key was already used with a different request")
        return existing, False

    if order.status != models.OrderStatus.pending_payment:
        raise HTTPException(status_code=409, detail="Payment can only be attempted for an order awaiting payment")

    payment_status = OUTCOMES[outcome]
    try:
        payment = models.Payment(
            order_id=order.id,
            amount=order.total,
            status=payment_status,
            idempotency_key=idempotency_key,
            request_fingerprint=payment_fingerprint,
        )
        db.add(payment)
        db.flush()
        db.add(models.PaymentStatusHistory(payment_id=payment.id, to_status=payment_status.value, changed_by=actor.id))
        if payment_status == models.PaymentStatus.succeeded:
            old_status = order.status.value
            order.status = models.OrderStatus.paid
            db.add(models.OrderStatusHistory(
                order_id=order.id,
                from_status=old_status,
                to_status=order.status.value,
                changed_by=actor.id,
            ))
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        concurrent = db.query(models.Payment).filter(
            models.Payment.order_id == order_id,
            models.Payment.idempotency_key == idempotency_key,
        ).first()
        if concurrent:
            if concurrent.request_fingerprint != payment_fingerprint:
                raise HTTPException(status_code=409, detail="Idempotency-Key was already used with a different request") from exc
            return concurrent, False
        raise
    db.refresh(payment)
    return payment, True
