from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models
from app.auth import require_admin
from app.core.database import get_db
from app.core.schemas import Page
from app.inventory.schemas import InventoryAdjustment, InventoryMovementResponse, InventoryResponse

router = APIRouter(prefix="/api/v1/admin/inventory", tags=["Inventory"])


@router.post("/adjustments", response_model=InventoryResponse)
def adjust_inventory(body: InventoryAdjustment, db: Session = Depends(get_db), current_user: models.User = Depends(require_admin)):
    """Apply a stock adjustment and record its movement.

    Args:
        body: Product ID, non-zero quantity delta, and adjustment reason.

    Returns:
        The product's updated inventory quantity and low-stock threshold.

    Raises:
        HTTPException: 401 if unauthenticated, 403 if not an administrator, 404 if inventory is missing, 409 if the adjustment would make stock negative, or 422 for invalid input.
    """
    inventory = db.query(models.Inventory).filter(models.Inventory.product_id == body.product_id).with_for_update().first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    next_quantity = inventory.quantity + body.quantity_delta
    if next_quantity < 0:
        raise HTTPException(status_code=409, detail="Inventory cannot become negative")
    inventory.quantity = next_quantity
    db.add(models.InventoryMovement(product_id=body.product_id, quantity_delta=body.quantity_delta, reason=body.reason, created_by=current_user.id))
    db.commit()
    db.refresh(inventory)
    return {"product_id": inventory.product_id, "quantity": inventory.quantity, "low_stock_threshold": inventory.low_stock_threshold}


@router.get("/low-stock", response_model=list[InventoryResponse])
def low_stock(db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    """List inventory records at or below their low-stock thresholds.

    Returns:
        Matching product IDs, quantities, and thresholds; an empty list if none match.

    Raises:
        HTTPException: 401 if unauthenticated or 403 if not an administrator.
    """
    rows = db.query(models.Inventory).filter(models.Inventory.quantity <= models.Inventory.low_stock_threshold).all()
    return [{"product_id": row.product_id, "quantity": row.quantity, "low_stock_threshold": row.low_stock_threshold} for row in rows]


@router.get("/movements", response_model=Page[InventoryMovementResponse])
def list_movements(
    product_id: int | None = Query(default=None, ge=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    """List inventory movements, newest first.

    Args:
        product_id: Optional product ID to filter by.
        page: One-based page number (default 1).
        page_size: Number of records per page (default 20, maximum 100).

    Returns:
        A page of inventory movement records and pagination metadata.

    Raises:
        HTTPException: 401 if unauthenticated, 403 if not an administrator, or 422 if a query parameter is invalid.
    """
    query = db.query(models.InventoryMovement)
    if product_id is not None:
        query = query.filter(models.InventoryMovement.product_id == product_id)
    total = query.count()
    rows = query.order_by(models.InventoryMovement.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": rows,
        "pagination": {"page": page, "page_size": page_size, "total_items": total, "total_pages": (total + page_size - 1) // page_size if total else 0},
    }
