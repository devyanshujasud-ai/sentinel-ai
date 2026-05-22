"""
╔══════════════════════════════════════════════════════════════╗
║                     SENTINEL AI                              ║
║          AI Prompt Security Gateway — Backend API            ║
║                                                              ║
║  Scan, detect, and neutralize prompt threats before          ║
║  they reach your LLMs (ChatGPT, Claude, Gemini).            ║
╚══════════════════════════════════════════════════════════════╝

Entry point for the FastAPI application.
Run with: uvicorn main:app --reload --port 8000
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.database.connection import connect_db, close_db
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.middleware.logging_middleware import LoggingMiddleware
from app.api.routes_auth import router as auth_router
from app.api.routes_scan import router as scan_router
from app.api.routes_history import router as history_router
from app.api.routes_analytics import router as analytics_router
from app.api.routes_threats import router as threats_router
from app.services.threat_service import seed_threats

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-25s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("sentinel")

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
settings = get_settings()


# ---------------------------------------------------------------------------
# Application lifespan
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle events."""
    # Startup
    logger.info("Starting Sentinel AI v%s ...", settings.APP_VERSION)
    await connect_db()
    await seed_threats()
    logger.info("Sentinel AI is ready. Environment: %s", settings.APP_ENV)

    yield

    # Shutdown
    logger.info("Shutting down Sentinel AI ...")
    await close_db()
    logger.info("Sentinel AI stopped.")


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware stack (order matters — outermost first)
# ---------------------------------------------------------------------------
# CORS
origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.add_middleware(RateLimiterMiddleware)

# Request logging
app.add_middleware(LoggingMiddleware)

# ---------------------------------------------------------------------------
# Route registration
# ---------------------------------------------------------------------------
API_PREFIX = f"/api/{settings.API_VERSION}"

app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(scan_router, prefix=API_PREFIX)
app.include_router(history_router, prefix=API_PREFIX)
app.include_router(analytics_router, prefix=API_PREFIX)
app.include_router(threats_router, prefix=API_PREFIX)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint — returns service status."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
    }


@app.get("/", tags=["System"])
async def root():
    """Root endpoint — API information."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "docs": "/docs",
        "health": "/health",
        "api_prefix": API_PREFIX,
    }
