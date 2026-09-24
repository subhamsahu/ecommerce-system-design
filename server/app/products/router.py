from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.auth import require_admin
from app.core.schemas import Page
from app.core.utils import slugify
from app.core.database import get_db
from app.products.schemas import CategoryCreate, CategoryResponse, CategoryUpdate, ProductCreate, ProductListResponse, ProductResponse, ProductUpdate

router = APIRouter(prefix="/api/v1", tags=["Catalog"])


@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).filter(models.Category.is_active.is_(True)).order_by(models.Category.name).all()


@router.get("/admin/dashboard")
def admin_dashboard(db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    """Small Phase 0 operational summary for the admin panel."""
    low_stock = db.query(func.count(models.Inventory.id)).filter(
        models.Inventory.quantity <= models.Inventory.low_stock_threshold
    ).scalar()
    return {
        "total_products": db.query(func.count(models.Product.id)).scalar(),
        "low_stock_products": low_stock,
        "total_orders": db.query(func.count(models.Order.id)).scalar(),
        "total_customers": db.query(func.count(models.User.id)).filter(
            models.User.role == models.UserRole.customer
        ).scalar(),
    }


@router.post("/admin/categories", response_model=CategoryResponse, status_code=201)
def create_category(body: CategoryCreate, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    category = models.Category(name=body.name.strip(), slug=slugify(body.name), description=body.description)
    db.add(category)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Category name or slug already exists") from exc
    db.refresh(category)
    return category


@router.get("/admin/categories", response_model=list[CategoryResponse])
def admin_categories(db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    return db.query(models.Category).order_by(models.Category.name).all()


@router.patch("/admin/categories/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, body: CategoryUpdate, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    category = db.get(models.Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    if body.name is not None:
        category.name = body.name.strip()
        category.slug = slugify(body.name)
    if body.description is not None:
        category.description = body.description
    if body.is_active is not None:
        category.is_active = body.is_active
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Category name or slug already exists") from exc
    db.refresh(category)
    return category


def _product_response(product: models.Product) -> ProductListResponse:
    return ProductListResponse.model_validate(product).model_copy(
        update={"available_quantity": product.inventory.quantity if product.inventory else 0}
    )


@router.get("/products", response_model=Page[ProductListResponse])
def list_products(
    search: str | None = None,
    category_id: int | None = None,
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(models.Product).filter(models.Product.is_published.is_(True), models.Product.is_archived.is_(False))
    if search:
        term = f"%{search.strip()}%"
        query = query.filter((models.Product.name.ilike(term)) | (models.Product.sku.ilike(term)))
    if category_id is not None:
        query = query.filter(models.Product.category_id == category_id)
    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)
    total = query.count()
    rows = query.order_by(models.Product.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [_product_response(row) for row in rows],
        "pagination": {"page": page, "page_size": page_size, "total_items": total, "total_pages": (total + page_size - 1) // page_size if total else 0},
    }


@router.get("/products/{product_id}", response_model=ProductListResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id, models.Product.is_published.is_(True), models.Product.is_archived.is_(False)).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return _product_response(product)


@router.get("/admin/products", response_model=Page[ProductListResponse])
def admin_products(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    query = db.query(models.Product)
    total = query.count()
    products = query.order_by(models.Product.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "items": [_product_response(product) for product in products],
        "pagination": {"page": page, "page_size": page_size, "total_items": total, "total_pages": (total + page_size - 1) // page_size if total else 0},
    }


@router.post("/admin/products", response_model=ProductResponse, status_code=201)
def create_product(body: ProductCreate, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    product_data = body.model_dump()
    product_data["sku"] = body.sku.strip().upper()
    if body.category_id is not None and not db.get(models.Category, body.category_id):
        raise HTTPException(status_code=422, detail="Category not found")
    product = models.Product(**product_data)
    db.add(product)
    try:
        db.flush()
        product.inventory = models.Inventory(quantity=0)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Product SKU already exists") from exc
    db.refresh(product)
    return product


@router.patch("/admin/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, body: ProductUpdate, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    product = db.get(models.Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if body.category_id is not None and not db.get(models.Category, body.category_id):
        raise HTTPException(status_code=422, detail="Category not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Product update conflicts with an existing record") from exc
    db.refresh(product)
    return product
