"""
Sentinel AI — History Routes

Endpoints for viewing scan history with pagination.
"""

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import get_current_user
from app.services.scan_service import get_scan_history

router = APIRouter(prefix="/history", tags=["Scan History"])


@router.get("")
async def list_scan_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user),
):
    """Get paginated scan history for the current user."""
    result = await get_scan_history(
        user_id=current_user["id"],
        page=page,
        page_size=page_size,
    )

    return {
        "status": "success",
        "data": result,
    }
