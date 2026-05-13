"""FastAPI dependency injection: JWT authentication."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import User

_bearer = HTTPBearer(auto_error=False)


def _decode_token(token: str) -> str:
    """Decode JWT and return the subject (username). Raises 401 on failure."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str | None = payload.get("sub")
        if not username:
            raise ValueError("missing sub")
        return username
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無效的憑證",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Require a valid JWT. Returns the User object."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要登入",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username = _decode_token(credentials.credentials)
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用戶不存在")
    return user


async def optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Optionally resolve the JWT. Returns User or None (no error if unauthenticated)."""
    if not credentials:
        return None
    try:
        username = _decode_token(credentials.credentials)
    except HTTPException:
        return None
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()
