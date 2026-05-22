"""
Sentinel AI — Threats Routes

Endpoints for viewing threat definitions and categories.
"""

from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.services.threat_service import get_all_threats, get_threats_by_category

router = APIRouter(prefix="/threats", tags=["Threat Definitions"])


@router.get("")
async def list_threats(current_user: dict = Depends(get_current_user)):
    """List all active threat definitions."""
    threats = await get_all_threats()
    return {
        "status": "success",
        "data": {"threats": threats, "total": len(threats)},
    }


@router.get("/{category}")
async def threats_by_category(
    category: str,
    current_user: dict = Depends(get_current_user),
):
    """Get threat definitions by category."""
    threats = await get_threats_by_category(category)
    return {
        "status": "success",
        "data": {"threats": threats, "total": len(threats), "category": category.upper()},
    }
