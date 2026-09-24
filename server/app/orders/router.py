from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status
from sqlalchemy.orm import Session, joinedload

from app import models
from app.auth import get_current_user, require_admin
from app.core.database import get_db
from app.core.schemas import Page
from app.orders.schemas import CheckoutRequest, OrderResponse, StatusUpdate
from app.orders.service import cancel_order, checkout, update_status

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])


def _response(order: models.Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        status=order.status.value,
        currency=order.currency,
        total=order.total,
        created_at=order.created_at,
        items=[
            {"product_name": item.product_name, "sku": item.sku, "quantity": item.quantity, "unit_price": item.unit_price}
            for item in order.items
        ],
    )


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    body: CheckoutRequest,
    response: Response,
    idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=8, max_length=128),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    order, created = checkout(db, current_user, body, idempotency_key)
    if not created:
        response.status_code = status.HTTP_200_OK
    return _response(order)


@router.get("", response_model=Page[OrderResponse])
def list_orders(
    status_filter: models.OrderStatus | None = Query(default=None, alias="status"),
    customer_id: int | None = Query(default=None, ge=1),
    created_after: datetime | None = None,
    created_before: datetime | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Order).options(joinedload(models.Order.items))
    if current_user.role != models.UserRole.admin:
        query = query.filter(models.Order.user_id == current_user.id)
    elif customer_id is not None:
        query = query.filter(models.Order.user_id == customer_id)
    if status_filter is not None:
        query = query.filter(models.Order.status == status_filter)
    if created_after is not None:
        query = query.filter(models.Order.created_at >= created_after)
    if created_before is not None:
        query = query.filter(models.Order.created_at <= created_before)
    total = query.order_by(None).count()
    rows = query.order_by(models.Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [_response(order) for order in rows],
        "pagination": {"page": page, "page_size": page_size, "total_items": total, "total_pages": (total + page_size - 1) // page_size if total else 0},
    }


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    query = db.query(models.Order).options(joinedload(models.Order.items)).filter(models.Order.id == order_id)
    if current_user.role != models.UserRole.admin:
        query = query.filter(models.Order.user_id == current_user.id)
    order = query.first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return _response(order)


@router.post("/{order_id}/cancellation", response_model=OrderResponse)
def cancellation(order_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Customer or administrator cancellation, including inventory and refund compensation."""
    return _response(cancel_order(db, order_id, current_user))


@router.patch("/{order_id}/status", response_model=OrderResponse)
def change_order_status(
    order_id: int,
    body: StatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    try:
        new_status = models.OrderStatus(body.status)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Unknown order status") from exc
    return _response(update_status(db, order_id, new_status, current_user))
