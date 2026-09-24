from typing import Any

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def problem_response(
    request: Request,
    *,
    status_code: int,
    title: str,
    detail: str,
    code: str,
    errors: list[dict[str, Any]] | None = None,
) -> JSONResponse:
    payload: dict[str, Any] = {
        "type": f"https://ecommerce.local/problems/{code.lower().replace("_", "-")}",
        "title": title,
        "status": status_code,
        "detail": detail,
        "instance": request.url.path,
        "code": code,
        "request_id": getattr(request.state, "request_id", None),
    }
    if errors:
        payload["errors"] = errors
    return JSONResponse(
        status_code=status_code,
        content=payload,
        media_type="application/problem+json",
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail if isinstance(exc.detail, str) else "The request could not be completed."
    code = {
        401: "UNAUTHENTICATED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
    }.get(exc.status_code, "HTTP_ERROR")
    return problem_response(
        request,
        status_code=exc.status_code,
        title="Request failed",
        detail=detail,
        code=code,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = [
        {
            "field": ".".join(str(part) for part in error["loc"] if part != "body"),
            "message": error["msg"],
        }
        for error in exc.errors()
    ]
    return problem_response(
        request,
        status_code=422,
        title="Validation failed",
        detail="One or more fields are invalid.",
        code="VALIDATION_ERROR",
        errors=errors,
    )
