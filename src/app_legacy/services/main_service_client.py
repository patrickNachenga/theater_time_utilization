from __future__ import annotations

import logging

import httpx

from app.config import settings
from app.schemas.auth import PermissionResponse

logger = logging.getLogger(__name__)


class MainServiceClient:
    def __init__(self):
        headers = {}
        if settings.MAIN_SERVICE_API_KEY:
            headers["X-API-Key"] = settings.MAIN_SERVICE_API_KEY

        self.client = httpx.AsyncClient(
            base_url=settings.MAIN_SERVICE_BASE_URL,
            timeout=settings.MAIN_SERVICE_TIMEOUT,
            headers=headers,
        )

    async def fetch_user_permissions(self, user_guid: str) -> PermissionResponse | None:
        try:
            response = await self.client.get(f"/internal/user/{user_guid}/permissions")
            response.raise_for_status()
            resp = response.json()
            data = resp.get("data")

            if not data:
                logger.info(f"Auth Service returned no data for user {user_guid}")
                return None

            if str(resp.get("status")) != '8000':
                logger.info(f"Unable to pull user {user_guid} in Auth service: {resp.get('status')}")
                return None

            return PermissionResponse(**data)
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Auth Service client HTTP error for user {user_guid}: "
                f"Status {e.response.status_code} - {e.response.text}"
            )
            return None
        except httpx.RequestError as e:
            logger.error(f"Auth Service client request error for user {user_guid}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching permissions for user {user_guid}: {e}")
            return None


auth_service_client = MainServiceClient()
