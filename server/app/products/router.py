from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models
from app.auth import require_admin
from app.core.pagination import paginate
from app.core.schemas import Page
from app.core.utils import slugify
from app.core.database import get_db
from app.products.schemas import CategoryCreate, CategoryResponse, ProductCreate, ProductListResponse, ProductResponse, ProductUpdate

router = APIRouter(prefix="/api/v1", tags=["Catalog"])


@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).filter(models.Category.is_active.is_(True)).order_by(models.Category.name).all()


@router.post("/admin/categories", response_model=CategoryResponse, status_code=201)
def create_category(body: CategoryCreate, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    category = models.Category(name=body.name.strip(), slug=slugify(body.name), description=body.description)
    db.add(category)
    try:
        db.commit()
    except Exception as exc:
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


@router.get("/admin/products", response_model=list[ProductListResponse])
def admin_products(db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    products = db.query(models.Product).order_by(models.Product.created_at.desc()).all()
    return [_product_response(product) for product in products]


@router.post("/admin/products", response_model=ProductResponse, status_code=201)
def create_product(body: ProductCreate, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    product_data = body.model_dump()
    product_data["sku"] = body.sku.strip().upper()
    product = models.Product(**product_data)
    db.add(product)
    db.flush()
    product.inventory = models.Inventory(quantity=0)
    db.commit()
    db.refresh(product)
    return product


@router.patch("/admin/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, body: ProductUpdate, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    product = db.get(models.Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product