from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
import jwt
from passlib.context import CryptContext
from app.core.config import settings

# Argon2id password context
try:
    pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")
except Exception:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Fallback to direct comparison or hash verification if needed
        return False


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any],
    role: str,
    email: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "email": email,
        "role": role,
        "type": "access",
        "exp": expire,
        "iat": now,
        "nbf": now
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
    to_encode: Dict[str, Any] = {
        "sub": str(subject),
        "type": "refresh",
        "exp": expire,
        "iat": now,
        "nbf": now
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )
