import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine  # noqa: F401 - kept for Alembic metadata access
from app import models  # noqa: F401 - registers all ORM models with Base.metadata
from app.auth.router import router as auth_router
from app.cart.router import router as cart_router
from app.inventory.router import router as inventory_router
from app.orders.router import router as orders_router
from app.payments.router import router as payments_router
from app.products.router import router as products_router
from app.users.router import router as users_router
from app.auth.permissions import router as permissions_router

# Auto-create tables for SQLite (local dev) only.
# On PostgreSQL (production/Render), Alembic migrations manage the schema.
from app.core.config import get_settings as _get_settings
if _get_settings().database_url.startswith("sqlite"):
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-commerce System Design Laboratory API",
    description="Phase 0 modular-monolith backend for catalog, inventory, cart, orders, and simulated payments",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Phase 0 domain routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(products_router)
app.include_router(inventory_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(payments_router)
app.include_router(permissions_router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "E-commerce System Design Laboratory API"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
