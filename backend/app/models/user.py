"""
Sentinel AI — User Model

MongoDB document structure for users.
"""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, EmailStr

from app.utils.helpers import generate_id, utc_now


class UserModel(BaseModel):
    """Represents a user document in the 'users' collection."""

    id: str = Field(default_factory=generate_id, alias="_id")
    email: EmailStr
    username: str
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = True
    role: str = "user"  # user | admin
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    total_scans: int = 0
    threats_blocked: int = 0

    model_config = {"populate_by_name": True}

    def to_mongo(self) -> dict:
        """Convert to MongoDB-insertable dict."""
        data = self.model_dump(by_alias=True)
        return data

    def to_safe_dict(self) -> dict:
        """Return user data without sensitive fields."""
        data = self.model_dump(by_alias=True)
        data.pop("hashed_password", None)
        data["id"] = data.pop("_id")
        return data
