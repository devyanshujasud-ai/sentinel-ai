"""
Sentinel AI — Logging Middleware

Logs request method, path, status code, and response time for every API call.
"""

import time
import logging

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("sentinel.access")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Structured request/response logging middleware."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Log structured entry
        client_ip = request.client.host if request.client else "unknown"
        logger.info(
            "%s %s %s — %dms — %s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            client_ip,
        )

        # Add response headers
        response.headers["X-Response-Time"] = f"{duration_ms}ms"
        response.headers["X-Powered-By"] = "Sentinel AI"

        return response
