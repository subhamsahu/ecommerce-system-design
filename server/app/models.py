from decimal import Decimal
import enum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class UserRole(str, enum.Enum):
    customer = "customer"
    admin = "admin"
    staff = "staff"
    employee = "employee"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(320), unique=True, index=True, nullable=True)
    full_name = Column(String(200), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.customer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


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


class RolePermissions(Base):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(SAEnum(UserRole), unique=True, nullable=False)
    permissions = Column(JSON, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    editor = relationship("User", foreign_keys=[updated_by])


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, nullable=False)
    slug = Column(String(140), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (CheckConstraint("price >= 0", name="ck_products_price_nonnegative"),)

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    sku = Column(String(80), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    currency = Column(String(3), nullable=False, default="INR")
    is_published = Column(Boolean, default=False, nullable=False, index=True)
    is_archived = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    category = relationship("Category")
    inventory = relationship("Inventory", back_populates="product", uselist=False, cascade="all, delete-orphan")


class Inventory(Base):
    __tablename__ = "inventory"
    __table_args__ = (CheckConstraint("quantity >= 0", name="ck_inventory_quantity_nonnegative"),)

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    low_stock_threshold = Column(Integer, nullable=False, default=5)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    product = relationship("Product", back_populates="inventory")


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity_delta = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=False)
    reference_type = Column(String(50), nullable=True)
    reference_id = Column(String(100), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    items = relationship("CartItem", cascade="all, delete-orphan", back_populates="cart")


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (UniqueConstraint("cart_id", "product_id", name="uq_cart_product"),)

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    line1 = Column(String(200), nullable=False)
    line2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(2), nullable=False, default="IN")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class OrderStatus(str, enum.Enum):
    pending_payment = "pending_payment"
    paid = "paid"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"
    refunded = "refunded"


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (UniqueConstraint("user_id", "idempotency_key", name="uq_order_idempotency"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    status = Column(SAEnum(OrderStatus), default=OrderStatus.pending_payment, nullable=False, index=True)
    currency = Column(String(3), nullable=False, default="INR")
    total = Column(Numeric(12, 2), nullable=False)
    idempotency_key = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    items = relationship("OrderItem", cascade="all, delete-orphan", back_populates="order")
    history = relationship("OrderStatusHistory", cascade="all, delete-orphan", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    product_name = Column(String(200), nullable=False)
    sku = Column(String(80), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    order = relationship("Order", back_populates="items")


class OrderStatusHistory(Base):
    __tablename__ = "order_status_history"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    from_status = Column(String(40), nullable=True)
    to_status = Column(String(40), nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    order = relationship("Order", back_populates="history")


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    succeeded = "succeeded"
    failed = "failed"
    timed_out = "timed_out"
    refunded = "refunded"


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (UniqueConstraint("order_id", "idempotency_key", name="uq_payment_idempotency"),)

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    status = Column(SAEnum(PaymentStatus), default=PaymentStatus.pending, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    idempotency_key = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Refund(Base):
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False, unique=True)
    amount = Column(Numeric(12, 2), nullable=False)
    reason = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ─── Add Your Custom Models Below ────────────────────────────────────────────
# Add your application-specific models here
# Example:
#
# class YourModel(Base):
#     __tablename__ = "your_table"
#     
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(200), nullable=False)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())

