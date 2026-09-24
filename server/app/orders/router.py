import hashlib
import json
from decimal import Decimal

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app import models
from app.auth import get_current_user, require_admin
from app.core.database import get_db
from app.orders.schemas import CheckoutRequest, OrderResponse, StatusUpdate

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])
ALLOWED_TRANSITIONS = {
    models.OrderStatus.paid: {models.OrderStatus.processing, models.OrderStatus.cancelled},
    models.OrderStatus.processing: {models.OrderStatus.shipped, models.OrderStatus.cancelled},
    models.OrderStatus.shipped: {models.OrderStatus.delivered},
    models.OrderStatus.delivered: set(),
    models.OrderStatus.pending_payment: {models.OrderStatus.cancelled},
    models.OrderStatus.cancelled: set(),
    models.OrderStatus.refunded: set(),
}


def _response(order: models.Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        status=order.status.value,
        currency=order.currency,
        total=order.total,
        created_at=order.created_at,
        items=[
            {
                "product_name": item.product_name,
                "sku": item.sku,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
            }
            for item in order.items
        ],
    )


def _request_hash(body: CheckoutRequest) -> str:
    serialized = json.dumps(body.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _existing_idempotent_order(
    db: Session,
    *,
    user_id: int,
    idempotency_key: str,
    request_hash: str,
) -> models.Order | None:
    existing = (
        db.query(models.Order)
        .options(joinedload(models.Order.items))
        .filter(
            models.Order.user_id == user_id,
            models.Order.idempotency_key == idempotency_key,
        )
        .first()
    )
    if existing and existing.idempotency_request_hash != request_hash:
        raise HTTPException(
            status_code=409,
            detail="Idempotency-Key was already used with a different checkout request.",
        )
    return existing


@router.post("", response_model=OrderResponse, status_code=201)
def checkout(
    body: CheckoutRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=8, max_length=128),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    request_hash = _request_hash(body)

    try:
        existing = _existing_idempotent_order(
            db,
            user_id=current_user.id,
            idempotency_key=idempotency_key,
            request_hash=request_hash,
        )
        if existing:
            return _response(existing)

        cart = (
            db.query(models.Cart)
            .options(
                joinedload(models.Cart.items)
                .joinedload(models.CartItem.product)
                .joinedload(models.Product.inventory)
            )
            .filter(models.Cart.user_id == current_user.id)
            .first()
        )
        if cart is None or not cart.items:
            raise HTTPException(status_code=422, detail="Cart is empty.")

        address = models.Address(user_id=current_user.id, **body.address.model_dump())
        db.add(address)
        db.flush()

        order = models.Order(
            user_id=current_user.id,
            address_id=address.id,
            idempotency_key=idempotency_key,
            idempotency_request_hash=request_hash,
            total=Decimal("0.00"),
            currency="INR",
        )
        db.add(order)
        db.flush()

        total = Decimal("0.00")
        for cart_item in list(cart.items):
            inventory = (
                db.query(models.Inventory)
                .filter(models.Inventory.product_id == cart_item.product_id)
                .with_for_update()
                .first()
            )
            product = db.get(models.Product, cart_item.product_id)
            if (
                product is None
                or not product.is_published
                or product.is_archived
                or inventory is None
                or inventory.quantity < cart_item.quantity
            ):
                raise HTTPException(
                    status_code=409,
                    detail=f"Insufficient inventory for {product.name if product else 'product'}.",
                )

            total += product.price * cart_item.quantity
            inventory.quantity -= cart_item.quantity
            db.add(
                models.InventoryMovement(
                    product_id=product.id,
                    quantity_delta=-cart_item.quantity,
                    reason="Order checkout",
                    reference_type="order",
                    reference_id=str(order.id),
                    created_by=current_user.id,
                )
            )
            order.items.append(
                models.OrderItem(
                    product_id=product.id,
                    product_name=product.name,
                    sku=product.sku,
                    quantity=cart_item.quantity,
                    unit_price=product.price,
                )
            )
            db.delete(cart_item)

        order.total = total
        order.history.append(
            models.OrderStatusHistory(
                to_status=models.OrderStatus.pending_payment.value,
                changed_by=current_user.id,
            )
        )
        result = _response(order)
        db.commit()
        return result
    except IntegrityError:
        db.rollback()
        existing = _existing_idempotent_order(
            db,
            user_id=current_user.id,
            idempotency_key=idempotency_key,
            request_hash=request_hash,
        )
        if existing:
            return _response(existing)
        raise
    except Exception:
        db.rollback()
        raise


@router.get("", response_model=list[OrderResponse])
def list_orders(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    query = db.query(models.Order).options(joinedload(models.Order.items))
    if current_user.role != models.UserRole.admin:
        query = query.filter(models.Order.user_id == current_user.id)
    return [_response(order) for order in query.order_by(models.Order.created_at.desc()).all()]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    query = db.query(models.Order).options(joinedload(models.Order.items)).filter(models.Order.id == order_id)
    if current_user.role != models.UserRole.admin:
        query = query.filter(models.Order.user_id == current_user.id)
    order = query.first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    return _response(order)


@router.post("/{order_id}/cancellation", response_model=OrderResponse)
def cancel_order(order_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    try:
        order = (
            db.query(models.Order)
            .filter(models.Order.id == order_id, models.Order.user_id == current_user.id)
            .with_for_update()
            .first()
        )
        if not order:
            raise HTTPException(status_code=404, detail="Order not found.")
        if models.OrderStatus.cancelled not in ALLOWED_TRANSITIONS.get(order.status, set()):
            raise HTTPException(status_code=409, detail="Order cannot be cancelled in its current state.")

        order.status = models.OrderStatus.cancelled
        for item in order.items:
            inventory = (
                db.query(models.Inventory)
                .filter(models.Inventory.product_id == item.product_id)
                .with_for_update()
                .first()
            )
            if inventory:
                inventory.quantity += item.quantity
                db.add(
                    models.InventoryMovement(
                        product_id=item.product_id,
                        quantity_delta=item.quantity,
                        reason="Order cancellation",
                        reference_type="order",
                        reference_id=str(order.id),
                        created_by=current_user.id,
                    )
                )

        payment = (
            db.query(models.Payment)
            .filter(
                models.Payment.order_id == order.id,
                models.Payment.status == models.PaymentStatus.succeeded,
            )
            .with_for_update()
            .first()
        )
        if payment:
            payment.status = models.PaymentStatus.refunded
            db.add(models.Refund(payment_id=payment.id, amount=payment.amount, reason="Order cancellation"))
            order.status = models.OrderStatus.refunded

        order.history.append(
            models.OrderStatusHistory(
                to_status=order.status.value,
                changed_by=current_user.id,
            )
        )
        result = _response(order)
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    body: StatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    try:
        order = db.query(models.Order).filter(models.Order.id == order_id).with_for_update().first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found.")
        try:
            new_status = models.OrderStatus(body.status)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="Unknown order status.") from exc
        if new_status not in ALLOWED_TRANSITIONS.get(order.status, set()):
            raise HTTPException(status_code=409, detail="Invalid order status transition.")

        old_status = order.status.value
        order.status = new_status
        order.history.append(
            models.OrderStatusHistory(
                from_status=old_status,
                to_status=new_status.value,
                changed_by=current_user.id,
            )
        )
        result = _response(order)
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise
