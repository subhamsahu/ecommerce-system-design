from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.auth.permissions import router as permissions_router
from app.auth.router import router as auth_router
from app.cart.router import router as cart_router
from app.core.config import get_settings
from app.core.errors import http_exception_handler, validation_exception_handler
from app.core.request_id import RequestIdMiddleware
from app.core.database import engine
from app.inventory.router import router as inventory_router
from app.orders.router import router as orders_router
from app.payments.router import router as payments_router
from app.products.router import router as products_router
from app.users.router import router as users_router

settings = get_settings()

app = FastAPI(
    title="E-commerce System Design Laboratory API",
    description="Phase 1 modular-monolith backend for catalog, inventory, cart, orders, and simulated payments.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(products_router)
app.include_router(inventory_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(payments_router)
app.include_router(permissions_router)


@app.get("/api/v1/health/live", tags=["health"])
def liveness(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "request_id": request.state.request_id})


@app.get("/api/v1/health/ready", tags=["health"])
def readiness(request: Request) -> JSONResponse:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "detail": "Database is unavailable.",
                "request_id": request.state.request_id,
            },
        )
    return JSONResponse({"status": "ok", "request_id": request.state.request_id})
