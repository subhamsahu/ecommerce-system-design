import re
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

_SAFE_REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{1,128}$")


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        received = request.headers.get("X-Request-ID", "")
        request_id = received if _SAFE_REQUEST_ID.fullmatch(received) else f"req_{uuid4().hex}"
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
