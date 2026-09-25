import re
import time
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from app.auth.router import router as auth_router
from app.cart.router import router as cart_router
from app.inventory.router import router as inventory_router
from app.orders.router import router as orders_router
from app.payments.router import router as payments_router
from app.products.router import router as products_router
from app.users.router import router as users_router
from app.auth.permissions import router as permissions_router
from app.core.config import get_settings
from app.core.logger import get_logger

settings = get_settings()
logger = get_logger().get_std_logger()
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

app = FastAPI(
    title="E-commerce System Design Laboratory API",
    description="Phase 0 modular-monolith backend for catalog, inventory, cart, orders, and simulated payments",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    started_at = time.perf_counter()
    # https://chatgpt.com/share/6ab61e5e-6a40-83ee-8073-150e9241df82
    supplied_id = request.headers.get("X-Request-ID", "")
    request_id = supplied_id if REQUEST_ID_PATTERN.fullmatch(supplied_id) else uuid4().hex
    request.state.request_id = request_id
    logger.debug(
        "Request started method=%s path=%s request_id=%s",
        request.method,
        request.url.path,
        request_id,
    )
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    duration_ms = (time.perf_counter() - started_at) * 1000
    if response.status_code >= 500:
        log_method = logger.error
    elif response.status_code >= 400:
        log_method = logger.warning
    else:
        log_method = logger.info
    log_method(
        "Request completed method=%s path=%s status_code=%s duration_ms=%.2f request_id=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        request_id,
    )
    return response


def _problem(request: Request, status: int, title: str, detail: str, code: str, errors: list[dict] | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "type": f"https://example.local/problems/{code.lower().replace('_', '-')}",
            "title": title,
            "status": status,
            "detail": detail,
            "instance": request.url.path,
            "code": code,
            "request_id": getattr(request.state, "request_id", None),
            "errors": errors or [],
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        {"field": ".".join(str(part) for part in error["loc"] if part != "body"), "message": error["msg"]}
        for error in exc.errors()
    ]
    return _problem(request, 422, "Validation failed", "One or more fields are invalid.", "VALIDATION_ERROR", errors)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    titles = {401: "Authentication required", 403: "Forbidden", 404: "Not found", 409: "Conflict", 422: "Validation failed"}
    codes = {401: "UNAUTHENTICATED", 403: "FORBIDDEN", 404: "NOT_FOUND", 409: "CONFLICT", 422: "VALIDATION_ERROR"}
    detail = exc.detail if isinstance(exc.detail, str) else "The request could not be completed."
    response = _problem(request, exc.status_code, titles.get(exc.status_code, "Request failed"), detail, codes.get(exc.status_code, "REQUEST_ERROR"))
    if exc.headers:
        response.headers.update(exc.headers)
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "Unhandled API error method=%s path=%s request_id=%s",
        request.method,
        request.url.path,
        getattr(request.state, "request_id", None),
    )
    return _problem(request, 500, "Internal server error", "An unexpected error occurred.", "INTERNAL_ERROR")

# Phase 0 domain routers. All database schema changes are applied with Alembic.
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
    """Return the API root status and service name.

    Returns:
        A JSON object with ``status`` set to ``ok`` and the API message.

    Raises:
        None.
    """
    return {"status": "ok", "message": "E-commerce System Design Laboratory API"}


@app.get("/health", tags=["Health"])
def health():
    """Return the service health status.

    Returns:
        A JSON object with ``status`` set to ``healthy``.

    Raises:
        None.
    """
    return {"status": "healthy"}
