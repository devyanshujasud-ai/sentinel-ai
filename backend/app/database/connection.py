"""
Sentinel AI — MongoDB Connection Manager

Async MongoDB connection lifecycle using Motor.
"""

import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings

logger = logging.getLogger("sentinel.database")

# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------
_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------
async def connect_db() -> None:
    """Initialize the Motor client and verify connectivity."""
    global _client, _database
    settings = get_settings()

    logger.info("Connecting to MongoDB at %s ...", settings.MONGODB_URI)
    _client = AsyncIOMotorClient(settings.MONGODB_URI)
    _database = _client[settings.DB_NAME]

    # Verify connection
    await _client.admin.command("ping")
    logger.info("MongoDB connected — database: %s", settings.DB_NAME)

    # Create indexes
    await _create_indexes()


async def close_db() -> None:
    """Gracefully close the Motor client."""
    global _client, _database
    if _client:
        _client.close()
        _client = None
        _database = None
        logger.info("MongoDB connection closed.")


# ---------------------------------------------------------------------------
# Accessors
# ---------------------------------------------------------------------------
def get_database() -> AsyncIOMotorDatabase:
    """Return the active database handle. Raises if not connected."""
    if _database is None:
        raise RuntimeError("Database not initialized. Call connect_db() first.")
    return _database


# ---------------------------------------------------------------------------
# Index creation
# ---------------------------------------------------------------------------
async def _create_indexes() -> None:
    """Create necessary indexes for performance and uniqueness."""
    db = get_database()

    # Users — unique email
    await db.users.create_index("email", unique=True)

    # Scans — user lookups and timestamp ordering
    await db.scans.create_index([("user_id", 1), ("created_at", -1)])
    await db.scans.create_index("created_at")

    # Analytics — user + date compound
    await db.analytics.create_index([("user_id", 1), ("date", -1)])

    # Threats — category lookup
    await db.threats.create_index("category")

    logger.info("Database indexes created.")
