"""
Sentinel AI — Auth Schemas

Request and response schemas for authentication endpoints.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Schema for authentication response."""

    access_token: str
    token_type: str = "bearer"
    user: dict


class ProfileResponse(BaseModel):
    """Schema for user profile response."""

    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    total_scans: int
    threats_blocked: int
    created_at: str
