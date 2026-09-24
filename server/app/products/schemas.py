from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120)
    description: str | None = None


class CategoryResponse(CategoryCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    is_active: bool
    created_at: datetime


class CategoryUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    is_active: bool | None = None


class ProductCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=200)
    sku: str = Field(min_length=1, max_length=80)
    description: str | None = None
    price: Decimal = Field(ge=0, decimal_places=2)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    category_id: int | None = None


class ProductUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    price: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    category_id: int | None = None
    is_published: bool | None = None
    is_archived: bool | None = None


class ProductResponse(ProductCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_published: bool
    is_archived: bool
    created_at: datetime
    updated_at: datetime | None = None


class ProductListResponse(ProductResponse):
    available_quantity: int = 0
