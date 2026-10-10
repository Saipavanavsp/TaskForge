import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models.enums import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    role: Optional[UserRole] = UserRole.member


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserOut(UserBase):
    id: uuid.UUID
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None
    user: UserOut


class TokenPayload(BaseModel):
    sub: str
    email: Optional[str] = None
    role: Optional[str] = None
    type: Optional[str] = None
    exp: Optional[int] = None
