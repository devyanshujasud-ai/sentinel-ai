"""
Sentinel AI — Scan Routes

Endpoints for scanning prompts and viewing scan details.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.schemas.scan import ScanRequest
from app.services.scan_service import scan_prompt, get_scan_by_id

router = APIRouter(prefix="/scan", tags=["Prompt Scanning"])


@router.post("", status_code=status.HTTP_200_OK)
async def create_scan(
    payload: ScanRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Scan a prompt for threats.

    Runs the full detection pipeline: analysis → risk scoring → sanitization → storage.
    """
    result = await scan_prompt(
        prompt=payload.prompt,
        user_id=current_user["id"],
        target_llm=payload.target_llm,
    )

    return {
        "status": "success",
        "data": result,
    }


@router.get("/{scan_id}")
async def get_scan(
    scan_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a specific scan result by ID."""
    scan = await get_scan_by_id(scan_id, current_user["id"])
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found.",
        )

    return {
        "status": "success",
        "data": scan,
    }
