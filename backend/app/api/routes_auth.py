"""
Sentinel AI — Auth Routes

Endpoints for user registration, login, and profile management.
"""

from fastapi import APIRouter, HTTPException, status, Depends

from app.core.security import hash_password, verify_password, create_access_token
from app.database.connection import get_database
from app.models.user import UserModel
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse
from app.auth.dependencies import get_current_user
from app.utils.helpers import generate_id, utc_now

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):
    """Register a new user account."""
    db = get_database()

    # Check if email already exists
    existing = await db.users.find_one({"email": payload.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    # Check if username taken
    existing_username = await db.users.find_one({"username": payload.username})
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This username is already taken.",
        )

    # Create user
    user = UserModel(
        _id=generate_id(),
        email=payload.email,
        username=payload.username,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        created_at=utc_now(),
        updated_at=utc_now(),
    )

    await db.users.insert_one(user.to_mongo())

    # Generate JWT
    token = create_access_token({"sub": user.id, "email": user.email})

    return AuthResponse(
        access_token=token,
        user=user.to_safe_dict(),
    )


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest):
    """Authenticate and receive an access token."""
    db = get_database()

    user_doc = await db.users.find_one({"email": payload.email})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not verify_password(payload.password, user_doc["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user_doc.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )

    token = create_access_token({"sub": user_doc["_id"], "email": user_doc["email"]})

    # Build safe user response
    safe_user = {k: v for k, v in user_doc.items() if k != "hashed_password"}
    safe_user["id"] = safe_user.pop("_id")

    return AuthResponse(access_token=token, user=safe_user)


@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return {
        "status": "success",
        "data": current_user,
    }
