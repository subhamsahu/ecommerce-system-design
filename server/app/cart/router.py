from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app import models
from app.auth import get_current_user
from app.cart.schemas import CartItemInput, CartItemUpdate, CartResponse
from app.core.database import get_db

router = APIRouter(prefix="/api/v1/cart", tags=["Cart"])


def _get_cart(db: Session, user_id: int) -> models.Cart:
    cart = db.query(models.Cart).options(joinedload(models.Cart.items).joinedload(models.CartItem.product).joinedload(models.Product.inventory)).filter(models.Cart.user_id == user_id).first()
    if not cart:
        cart = models.Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def _response(cart: models.Cart) -> CartResponse:
    items = []
    total = Decimal("0.00")
    for item in cart.items:
        available = item.product.inventory.quantity if item.product.inventory else 0
        items.append({"id": item.id, "product_id": item.product_id, "name": item.product.name, "sku": item.product.sku, "quantity": item.quantity, "unit_price": item.product.price, "available_quantity": available})
        total += item.product.price * item.quantity
    return CartResponse(id=cart.id, items=items, total=total)


@router.get("", response_model=CartResponse)
def get_cart(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Get the authenticated user's cart, creating an empty cart if needed.

    Returns:
        The cart, its items, and the calculated total.

    Raises:
        HTTPException: 401 if the bearer token is missing or invalid.
    """
    return _response(_get_cart(db, current_user.id))


@router.post("/items", response_model=CartResponse)
def add_item(body: CartItemInput, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Add a product quantity to the authenticated user's cart.

    Args:
        body: Product ID and quantity to add.

    Returns:
        The updated cart and its calculated total.

    Raises:
        HTTPException: 401 if unauthenticated, 404 if the product is unavailable, 409 if stock is insufficient, or 422 if the input is invalid or the cart item limit would be exceeded.
    """
    product = db.query(models.Product).options(joinedload(models.Product.inventory)).filter(models.Product.id == body.product_id, models.Product.is_published.is_(True), models.Product.is_archived.is_(False)).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if not product.inventory:
        raise HTTPException(status_code=409, detail="Insufficient inventory")
    cart = _get_cart(db, current_user.id)
    item = next((row for row in cart.items if row.product_id == body.product_id), None)
    if item:
        requested_quantity = item.quantity + body.quantity
        if requested_quantity > 100:
            raise HTTPException(status_code=422, detail="Cart item limit is 100")
        if product.inventory.quantity < requested_quantity:
            raise HTTPException(status_code=409, detail="Insufficient inventory")
        item.quantity = requested_quantity
    else:
        if product.inventory.quantity < body.quantity:
            raise HTTPException(status_code=409, detail="Insufficient inventory")
        cart.items.append(models.CartItem(product_id=body.product_id, quantity=body.quantity))
    db.commit()
    return _response(_get_cart(db, current_user.id))


@router.patch("/items/{item_id}", response_model=CartResponse)
def update_item(item_id: int, body: CartItemUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Set the quantity of an item in the authenticated user's cart.

    Args:
        item_id: ID of the cart item to update.
        body: New item quantity.

    Returns:
        The updated cart and its calculated total.

    Raises:
        HTTPException: 401 if unauthenticated, 404 if the cart item is not owned by the user or does not exist, 409 if stock is insufficient, or 422 for invalid input.
    """
    item = db.query(models.CartItem).join(models.Cart).filter(models.CartItem.id == item_id, models.Cart.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    inventory = db.query(models.Inventory).filter(models.Inventory.product_id == item.product_id).first()
    if not inventory or inventory.quantity < body.quantity:
        raise HTTPException(status_code=409, detail="Insufficient inventory")
    item.quantity = body.quantity
    db.commit()
    return _response(_get_cart(db, current_user.id))


@router.delete("/items/{item_id}", response_model=CartResponse)
def remove_item(item_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Remove an item from the authenticated user's cart.

    Args:
        item_id: ID of the cart item to remove.

    Returns:
        The updated cart and its calculated total.

    Raises:
        HTTPException: 401 if unauthenticated or 404 if the cart item is not owned by the user or does not exist.
    """
    item = db.query(models.CartItem).join(models.Cart).filter(models.CartItem.id == item_id, models.Cart.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(item)
    db.commit()
    return _response(_get_cart(db, current_user.id))
