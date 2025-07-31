from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr, Field

from app.schemas.permission_schema import PermissionResponse
from app.schemas.role_schema import RoleResponse


class RegisterUser(BaseModel):
    """Schema for user registration."""

    firstname: str = Field(..., min_length=2)
    lastname: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=6)


class RegisterUserResponse(BaseModel):
    """Response model for user registration."""

    id: int
    firstname: str
    lastname: str
    email: EmailStr
    created_at: datetime | None = None

    class Config:
        orm_mode = True


class LoginUser(BaseModel):
    """Schema for user login."""

    email: EmailStr = Field(alias="username")
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str


class UserRetrieveResponse(RegisterUserResponse):
    """Response model for retrieving user details."""

    last_login: datetime | None = None
    updated_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user details."""

    firstname: str | None = Field(None, min_length=2)
    lastname: str | None = Field(None, min_length=2)

    class Config:
        from_attributes = True


class UserRolesPermissionsResponse(BaseModel):
    """Schema to get list of assigned role and permissions to user"""

    user_details: UserRetrieveResponse
    roles: List[RoleResponse]
    permissions: List[PermissionResponse]

    class Config:
        from_attributes = True
