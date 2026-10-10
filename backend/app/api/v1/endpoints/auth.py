import uuid
from typing import Optional
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserOut

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    # Check if user already exists
    existing = await db.execute(select(User).where(User.email == user_in.email))
    if existing.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists"
        )

    # Hash password with Argon2id
    hashed_pwd = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        password_hash=hashed_pwd,
        full_name=user_in.full_name,
        role=user_in.role or UserRole.member,
        is_active=True
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Issue tokens
    access_token = create_access_token(
        subject=new_user.id,
        role=new_user.role.value,
        email=new_user.email
    )
    refresh_token = create_refresh_token(subject=new_user.id)

    # Set HttpOnly refresh cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,  # Set true in production behind HTTPS
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path="/"
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
        user=UserOut.model_validate(new_user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalars().first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    access_token = create_access_token(
        subject=user.id,
        role=user.role.value,
        email=user.email
    )
    refresh_token = create_refresh_token(subject=user.id)

    # Set HttpOnly, Secure, SameSite=Strict / Lax cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path="/"
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
        user=UserOut.model_validate(user)
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token_endpoint(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    refresh_token_body: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    token = refresh_token or refresh_token_body
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing"
        )

    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        user_id = uuid.UUID(payload.get("sub"))
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Rotate tokens: generate new pair
    new_access_token = create_access_token(
        subject=user.id,
        role=user.role.value,
        email=user.email
    )
    new_refresh_token = create_refresh_token(subject=user.id)

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path="/"
    )

    return TokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        refresh_token=new_refresh_token,
        user=UserOut.model_validate(user)
    )


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="refresh_token", path="/")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
