from __future__ import annotations

import logging
from typing import Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.config import settings
from app.schemas.auth import TokenPayload, CurrentUser
from app.services.permission_service import permission_service

logger = logging.getLogger(__name__)

security_scheme = HTTPBearer(
    auto_error=False,
    description="JWT Bearer token issued by the Auth Service (RS256)",
)


def _decode_token(token: str) -> TokenPayload | None:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_PUBLIC_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
        )
        return TokenPayload(**payload)
    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected token decode error: {e}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> CurrentUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    token_payload = _decode_token(token)

    if token_payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    resolved_permissions = await permission_service.resolve_permissions(token_payload)

    if not resolved_permissions.permissions and not resolved_permissions.groups:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to resolve user permissions. Please try again later.",
        )

    return CurrentUser(
        uid=token_payload.guid,
        username=token_payload.username,
        email=token_payload.email,
        full_name=token_payload.full_name,
        groups=resolved_permissions.groups,
        perm_version=resolved_permissions.version,
        permissions=resolved_permissions.permissions,
        department=token_payload.department,
        directory=token_payload.directory,
        title=token_payload.title,
        pf_number=token_payload.hospital_number,
        token=token,
    )


def require_permissions(*permissions: str) -> Callable:
    async def _require_permissions(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if current_user.is_admin:
            return current_user
        for perm in permissions:
            if not current_user.has_permission(perm):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permission: {perm}",
                )
        return current_user

    return _require_permissions


def require_groups(*groups: str) -> Callable:
    async def _require_groups(
        current_user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        if current_user.is_admin:
            return current_user
        if not current_user.has_any_group(list(groups)):
            group_names = ", ".join(groups)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required groups: {group_names}",
            )
        return current_user

    return _require_groups


def require_admin(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return current_user
