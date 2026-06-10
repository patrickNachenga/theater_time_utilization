from __future__ import annotations

import logging

from app.schemas.auth import PermissionResponse, TokenPayload
from app.services.redis_service import redis_service
from app.services.main_service_client import auth_service_client

logger = logging.getLogger(__name__)


class PermissionService:
    async def resolve_permissions(self, token_payload: TokenPayload) -> PermissionResponse:
        user_guid = token_payload.guid
        jwt_perm_version = token_payload.perm_version

        cached_permissions = await redis_service.get_user_permissions(user_guid)

        if cached_permissions:
            if cached_permissions.version == jwt_perm_version:
                logger.debug(f"Permissions for user {user_guid} found in cache and versions match.")
                return cached_permissions
            else:
                logger.info(
                    f"Permissions for user {user_guid} in cache are stale (cached v{cached_permissions.version}, "
                    f"JWT v{jwt_perm_version}). Fetching from Auth Service."
                )
        else:
            logger.info(f"Permissions for user {user_guid} not found in cache. Fetching from Auth Service.")

        auth_service_permissions = await auth_service_client.fetch_user_permissions(user_guid)

        if not auth_service_permissions:
            logger.error(f"Failed to fetch permissions for user {user_guid} from Auth Service.")
            return PermissionResponse(user_guid=user_guid, version=jwt_perm_version, groups=[], permissions=[])

        await redis_service.set_user_permissions(user_guid, auth_service_permissions)
        return auth_service_permissions


permission_service = PermissionService()
