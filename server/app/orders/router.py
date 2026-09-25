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
    """Create an order from the authenticated user's cart.

    Args:
        body: Checkout address details.
        idempotency_key: Required ``Idempotency-Key`` header, 8-128 characters; reuse safely retries the same checkout.

    Returns:
        The created order (201), or the existing order (200) for an identical idempotent retry.

    Raises:
        HTTPException: 401 if unauthenticated, 409 if the key is reused with different input or an item is no longer available, or 422 if the cart is empty or input is invalid.
    """
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
    """List orders visible to the authenticated user, newest first.

    Args:
        status_filter: Optional order status filter (query parameter ``status``).
        customer_id: Optional customer ID filter; applied for administrators only.
        created_after: Include orders created at or after this timestamp.
        created_before: Include orders created at or before this timestamp.
        page: One-based page number (default 1).
        page_size: Number of orders per page (default 20, maximum 100).

    Returns:
        A page of orders and pagination metadata. Non-administrators only see their own orders.

    Raises:
        HTTPException: 401 if unauthenticated or 422 if a query parameter is invalid.
    """
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
    """Get an order visible to the authenticated user.

    Args:
        order_id: ID of the order to retrieve.

    Returns:
        The order with its item snapshots.

    Raises:
        HTTPException: 401 if unauthenticated, 404 if the order does not exist or is not owned by the user, or 422 if the ID is invalid.
    """
    query = db.query(models.Order).options(joinedload(models.Order.items)).filter(models.Order.id == order_id)
    if current_user.role != models.UserRole.admin:
        query = query.filter(models.Order.user_id == current_user.id)
    order = query.first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return _response(order)


@router.post("/{order_id}/cancellation", response_model=OrderResponse)
def cancellation(order_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Cancel an order and restore inventory, issuing a refund when applicable.

    Args:
        order_id: ID of the order to cancel.

    Returns:
        The cancelled order.

    Raises:
        HTTPException: 401 if unauthenticated, 404 if the order does not exist or is not owned by the user, 409 if the order cannot be cancelled or inventory is missing, or 422 if the ID is invalid.
    """
    return _response(cancel_order(db, order_id, current_user))


@router.patch("/{order_id}/status", response_model=OrderResponse)
def change_order_status(
    order_id: int,
    body: StatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    """Advance an order through an allowed fulfillment status transition.

    Args:
        order_id: ID of the order to update.
        body: Target order status. Cancellation must use the cancellation endpoint.

    Returns:
        The order with its updated status.

    Raises:
        HTTPException: 401 if unauthenticated, 403 if not an administrator, 404 if the order does not exist, 409 if the transition is not allowed, or 422 for an unknown status or invalid input.
    """
    try:
        new_status = models.OrderStatus(body.status)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Unknown order status") from exc
    return _response(update_status(db, order_id, new_status, current_user))
