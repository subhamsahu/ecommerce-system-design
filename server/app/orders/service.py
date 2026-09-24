"""Transactional order use cases owned by the order domain."""

import hashlib
import json
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app import models
from app.orders.schemas import CheckoutRequest


ALLOWED_TRANSITIONS = {
    models.OrderStatus.paid: {models.OrderStatus.processing},
    models.OrderStatus.processing: {models.OrderStatus.shipped},
    models.OrderStatus.shipped: {models.OrderStatus.delivered},
    models.OrderStatus.delivered: set(),
    models.OrderStatus.pending_payment: set(),
    models.OrderStatus.cancelled: set(),
    models.OrderStatus.refunded: set(),
}


def fingerprint(body: CheckoutRequest) -> str:
    payload = json.dumps(body.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def checkout(db: Session, user: models.User, body: CheckoutRequest, idempotency_key: str) -> tuple[models.Order, bool]:
    request_fingerprint = fingerprint(body)
    existing = (
        db.query(models.Order)
        .options(joinedload(models.Order.items))
        .filter(models.Order.user_id == user.id, models.Order.idempotency_key == idempotency_key)
        .first()
    )
    if existing:
        if existing.request_fingerprint != request_fingerprint:
            raise HTTPException(status_code=409, detail="Idempotency-Key was already used with a different request")
        return existing, False

    cart = (
        db.query(models.Cart)
        .options(joinedload(models.Cart.items))
        .filter(models.Cart.user_id == user.id)
        .first()
    )
    if not cart or not cart.items:
        raise HTTPException(status_code=422, detail="Cart is empty")

    try:
        address = models.Address(user_id=user.id, **body.address.model_dump())
        db.add(address)
        db.flush()
        order = models.Order(
            user_id=user.id,
            address_id=address.id,
            idempotency_key=idempotency_key,
            request_fingerprint=request_fingerprint,
            total=Decimal("0.00"),
            currency="INR",
        )
        db.add(order)
        db.flush()
        total = Decimal("0.00")
        # A stable lock order avoids avoidable deadlocks for carts sharing products.
        for cart_item in sorted(list(cart.items), key=lambda item: item.product_id):
            inventory = (
                db.query(models.Inventory)
                .filter(models.Inventory.product_id == cart_item.product_id)
                .with_for_update()
                .first()
            )
            product = db.get(models.Product, cart_item.product_id)
            if not product or product.is_archived or not product.is_published or not inventory or inventory.quantity < cart_item.quantity:
                raise HTTPException(status_code=409, detail="A cart item is no longer available in the requested quantity")
            total += product.price * cart_item.quantity
            inventory.quantity -= cart_item.quantity
            db.add(models.InventoryMovement(
                product_id=product.id,
                quantity_delta=-cart_item.quantity,
                reason="Order checkout",
                reference_type="order",
                reference_id=str(order.id),
                created_by=user.id,
            ))
            order.items.append(models.OrderItem(
                product_id=product.id,
                product_name=product.name,
                sku=product.sku,
                quantity=cart_item.quantity,
                unit_price=product.price,
            ))
            db.delete(cart_item)

        order.total = total
        order.history.append(models.OrderStatusHistory(to_status=order.status.value, changed_by=user.id))
        initial_payment = models.Payment(
            order_id=order.id,
            amount=total,
            status=models.PaymentStatus.pending,
            idempotency_key=f"checkout:{hashlib.sha256(idempotency_key.encode()).hexdigest()}",
            request_fingerprint=request_fingerprint,
        )
        db.add(initial_payment)
        db.flush()
        db.add(models.PaymentStatusHistory(payment_id=initial_payment.id, to_status=models.PaymentStatus.pending.value, changed_by=user.id))
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as exc:
        db.rollback()
        concurrent = (
            db.query(models.Order)
            .options(joinedload(models.Order.items))
            .filter(models.Order.user_id == user.id, models.Order.idempotency_key == idempotency_key)
            .first()
        )
        if concurrent:
            if concurrent.request_fingerprint != request_fingerprint:
                raise HTTPException(status_code=409, detail="Idempotency-Key was already used with a different request") from exc
            return concurrent, False
        raise
    db.refresh(order)
    return order, True


def cancel_order(db: Session, order_id: int, actor: models.User) -> models.Order:
    order = (
        db.query(models.Order)
        .filter(models.Order.id == order_id)
        .with_for_update()
        .first()
    )
    if not order or (actor.role != models.UserRole.admin and order.user_id != actor.id):
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status not in {models.OrderStatus.pending_payment, models.OrderStatus.paid, models.OrderStatus.processing}:
        raise HTTPException(status_code=409, detail="Order cannot be cancelled in its current state")

    old_status = order.status.value
    for item in order.items:
        inventory = (
            db.query(models.Inventory)
            .filter(models.Inventory.product_id == item.product_id)
            .with_for_update()
            .first()
        )
        if not inventory:
            raise HTTPException(status_code=409, detail="Order inventory record is missing")
        inventory.quantity += item.quantity
        db.add(models.InventoryMovement(
            product_id=item.product_id,
            quantity_delta=item.quantity,
            reason="Order cancellation",
            reference_type="order",
            reference_id=str(order.id),
            created_by=actor.id,
        ))

    succeeded_payment = (
        db.query(models.Payment)
        .filter(models.Payment.order_id == order.id, models.Payment.status == models.PaymentStatus.succeeded)
        .with_for_update()
        .first()
    )
    if succeeded_payment:
        succeeded_payment.status = models.PaymentStatus.refunded
        db.add(models.Refund(payment_id=succeeded_payment.id, amount=succeeded_payment.amount, reason="Order cancellation"))
        db.add(models.PaymentStatusHistory(
            payment_id=succeeded_payment.id,
            from_status=models.PaymentStatus.succeeded.value,
            to_status=models.PaymentStatus.refunded.value,
            changed_by=actor.id,
        ))
    order.status = models.OrderStatus.cancelled
    order.history.append(models.OrderStatusHistory(from_status=old_status, to_status=order.status.value, changed_by=actor.id))
    db.commit()
    db.refresh(order)
    return order


def update_status(db: Session, order_id: int, status: models.OrderStatus, actor: models.User) -> models.Order:
    # Lock only the order row. joinedload() adds an outer join to order_items,
    # which PostgreSQL rejects when FOR UPDATE is applied to the nullable side.
    order = db.query(models.Order).filter(models.Order.id == order_id).with_for_update().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if status == models.OrderStatus.cancelled:
        raise HTTPException(status_code=409, detail="Use the cancellation endpoint so inventory and refunds are handled atomically")
    if status not in ALLOWED_TRANSITIONS.get(order.status, set()):
        raise HTTPException(status_code=409, detail="Invalid order status transition")
    old_status = order.status.value
    order.status = status
    order.history.append(models.OrderStatusHistory(from_status=old_status, to_status=status.value, changed_by=actor.id))
    db.commit()
    db.refresh(order)
    return order
