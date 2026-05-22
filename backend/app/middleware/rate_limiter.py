"""
Sentinel AI — Rate Limiter Middleware

In-memory sliding window rate limiter per client IP.
"""

import time
import logging
from collections import defaultdict
from typing import Dict, List

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import get_settings

logger = logging.getLogger("sentinel.rate_limiter")


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Sliding window rate limiter per client IP."""

    def __init__(self, app):
        super().__init__(app)
        self._requests: Dict[str, List[float]] = defaultdict(list)
        settings = get_settings()
        self.limit = settings.RATE_LIMIT_PER_MINUTE
        self.window = 60  # seconds

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for health check and docs
        if request.url.path in ("/health", "/docs", "/openapi.json", "/redoc"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Clean expired entries
        self._requests[client_ip] = [
            t for t in self._requests[client_ip] if now - t < self.window
        ]

        if len(self._requests[client_ip]) >= self.limit:
            retry_after = int(self.window - (now - self._requests[client_ip][0]))
            logger.warning("Rate limit exceeded for %s", client_ip)
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please slow down.",
                    "retry_after": max(1, retry_after),
                },
                headers={"Retry-After": str(max(1, retry_after))},
            )

        self._requests[client_ip].append(now)
        return await call_next(request)
