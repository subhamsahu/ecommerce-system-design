from datetime import datetime
from decimal import Decimal
import enum
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, Enum as SAEnum, JSON, Numeric, Text, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from app.core.utils import utc_now


class UserRole(str, enum.Enum):
    customer = "customer"
    admin = "admin"
    staff = "staff"
    employee = "employee"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(max_length=100, unique=True, index=True)
    email: str = Field(max_length=320, unique=True, index=True)
    full_name: str = Field(max_length=200)
    hashed_password: str = Field(max_length=255)
    role: UserRole = Field(default=UserRole.customer, sa_type=SAEnum(UserRole, name="userrole"))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))


# ── Role Permissions ──────────────────────────────────────────────────────────

# Default permission sets used when seeding the DB for the first time.
# Customize these based on your application's needs.
DEFAULT_ROLE_PERMISSIONS: dict = {
    "customer": {
        "canViewDashboard": False,
        "canViewUserManagement": False,
        "canManageUsers": False,
        "canViewSettings": False,
    },
    "staff": {
        "canViewDashboard": True,
        "canViewUserManagement": False,
        "canManageUsers": False,
        "canViewSettings": True,
    },
    "employee": {
        "canViewDashboard": True,
        "canViewUserManagement": False,
        "canManageUsers": False,
        "canViewSettings": True,
    },
}


class RolePermissions(SQLModel, table=True):
    __tablename__ = "role_permissions"

    id: int | None = Field(default=None, primary_key=True)
    role: UserRole = Field(sa_type=SAEnum(UserRole, name="userrole"), unique=True)
    permissions: dict = Field(sa_type=JSON)
    updated_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))
    updated_by: int | None = Field(default=None, foreign_key="users.id")

    editor: User | None = Relationship(sa_relationship_kwargs={"foreign_keys": "RolePermissions.updated_by"})


class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=120, unique=True)
    slug: str = Field(max_length=140, unique=True, index=True)
    description: str | None = Field(default=None, sa_type=Text)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))


class Product(SQLModel, table=True):
    __tablename__ = "products"
    __table_args__ = (CheckConstraint("price >= 0", name="ck_products_price_nonnegative"),)

    id: int | None = Field(default=None, primary_key=True)
    category_id: int | None = Field(default=None, foreign_key="categories.id", index=True)
    name: str = Field(max_length=200, index=True)
    sku: str = Field(max_length=80, unique=True, index=True)
    description: str | None = Field(default=None, sa_type=Text)
    price: Decimal = Field(default=Decimal("0.00"), sa_type=Numeric(12, 2))
    currency: str = Field(default="INR", max_length=3)
    is_published: bool = Field(default=False, index=True)
    is_archived: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))
    updated_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))

    category: Category | None = Relationship()
    inventory: Optional["Inventory"] = Relationship(back_populates="product", cascade_delete=True, sa_relationship_kwargs={"uselist": False})


class Inventory(SQLModel, table=True):
    __tablename__ = "inventory"
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="ck_inventory_quantity_nonnegative"),
        CheckConstraint("low_stock_threshold >= 0", name="ck_inventory_low_stock_threshold_nonnegative"),
    )

    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id", unique=True)
    quantity: int = Field(default=0)
    low_stock_threshold: int = Field(default=5)
    updated_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))

    product: Product = Relationship(back_populates="inventory")


class InventoryMovement(SQLModel, table=True):
    __tablename__ = "inventory_movements"

    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.id", index=True)
    quantity_delta: int
    reason: str = Field(max_length=255)
    reference_type: str | None = Field(default=None, max_length=50)
    reference_id: str | None = Field(default=None, max_length=100)
    created_by: int | None = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))


class Cart(SQLModel, table=True):
    __tablename__ = "carts"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True)
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))
    updated_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))
    items: list["CartItem"] = Relationship(back_populates="cart", cascade_delete=True)


class CartItem(SQLModel, table=True):
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("cart_id", "product_id", name="uq_cart_product"),
        CheckConstraint("quantity > 0", name="ck_cart_items_quantity_positive"),
    )

    id: int | None = Field(default=None, primary_key=True)
    cart_id: int = Field(foreign_key="carts.id")
    product_id: int = Field(foreign_key="products.id")
    quantity: int
    cart: Cart = Relationship(back_populates="items")
    product: Product = Relationship()


class Address(SQLModel, table=True):
    __tablename__ = "addresses"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    line1: str = Field(max_length=200)
    line2: str | None = Field(default=None, max_length=200)
    city: str = Field(max_length=100)
    state: str = Field(max_length=100)
    postal_code: str = Field(max_length=20)
    country: str = Field(default="IN", max_length=2)
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))


class OrderStatus(str, enum.Enum):
    pending_payment = "pending_payment"
    paid = "paid"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"
    refunded = "refunded"


class Order(SQLModel, table=True):
    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint("user_id", "idempotency_key", name="uq_order_idempotency"),
        CheckConstraint("total >= 0", name="ck_orders_total_nonnegative"),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    address_id: int = Field(foreign_key="addresses.id")
    status: OrderStatus = Field(default=OrderStatus.pending_payment, sa_type=SAEnum(OrderStatus, name="orderstatus"), index=True)
    currency: str = Field(default="INR", max_length=3)
    total: Decimal = Field(sa_type=Numeric(12, 2))
    idempotency_key: str = Field(max_length=128)
    request_fingerprint: str = Field(max_length=64)
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True), index=True)
    updated_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))
    items: list["OrderItem"] = Relationship(back_populates="order", cascade_delete=True)
    history: list["OrderStatusHistory"] = Relationship(back_populates="order", cascade_delete=True)


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_items_quantity_positive"),
        CheckConstraint("unit_price >= 0", name="ck_order_items_unit_price_nonnegative"),
    )

    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    product_id: int | None = Field(default=None, foreign_key="products.id")
    product_name: str = Field(max_length=200)
    sku: str = Field(max_length=80)
    quantity: int
    unit_price: Decimal = Field(sa_type=Numeric(12, 2))
    order: "Order" = Relationship(back_populates="items")


class OrderStatusHistory(SQLModel, table=True):
    __tablename__ = "order_status_history"

    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    from_status: str | None = Field(default=None, max_length=40)
    to_status: str = Field(max_length=40)
    changed_by: int | None = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))
    order: Order = Relationship(back_populates="history")


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    succeeded = "succeeded"
    failed = "failed"
    timed_out = "timed_out"
    refunded = "refunded"


class Payment(SQLModel, table=True):
    __tablename__ = "payments"
    __table_args__ = (
        UniqueConstraint("order_id", "idempotency_key", name="uq_payment_idempotency"),
        CheckConstraint("amount >= 0", name="ck_payments_amount_nonnegative"),
    )

    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id", index=True)
    status: PaymentStatus = Field(default=PaymentStatus.pending, sa_type=SAEnum(PaymentStatus, name="paymentstatus"))
    amount: Decimal = Field(sa_type=Numeric(12, 2))
    idempotency_key: str = Field(max_length=128)
    request_fingerprint: str = Field(max_length=64)
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))


class PaymentStatusHistory(SQLModel, table=True):
    __tablename__ = "payment_status_history"

    id: int | None = Field(default=None, primary_key=True)
    payment_id: int = Field(foreign_key="payments.id", index=True)
    from_status: str | None = Field(default=None, max_length=40)
    to_status: str = Field(max_length=40)
    changed_by: int | None = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))


class Refund(SQLModel, table=True):
    __tablename__ = "refunds"
    __table_args__ = (CheckConstraint("amount >= 0", name="ck_refunds_amount_nonnegative"),)

    id: int | None = Field(default=None, primary_key=True)
    payment_id: int = Field(foreign_key="payments.id", unique=True)
    amount: Decimal = Field(sa_type=Numeric(12, 2))
    reason: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))


# ─── Add Your Custom Models Below ────────────────────────────────────────────
# Add your application-specific models here
# Example:
#
# class YourModel(Base):
#     __tablename__ = "your_table"
#     
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(200), nullable=False)
#     created_at: datetime = Field(default_factory=utc_now)
