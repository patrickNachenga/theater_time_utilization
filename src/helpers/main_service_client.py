"""
Client for interacting with the external Auth Service to fetch user permissions.
"""

from __future__ import annotations

import logging
from typing import Optional

import httpx

from src.core.config import settings
from src.shared.models import PermissionResponse
from src.shared.response_code import ResponseCode as RC

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
        """
        Fetches user permissions from the Auth Service.
        """
        try:
            response = await self.client.get(f"/internal/user/{user_guid}/permissions")
            response.raise_for_status()

            resp = response.json()
            # print(resp.get("data"))

            # Check the status code from the response body
            resp_status = resp.get("status")
            if resp_status is None or resp_status != RC.SUCCESS:
                logger.warning(
                    f"Auth Service returned non-success status for user {user_guid}: "
                    f"status={resp_status}, message={resp.get('message', 'No message')}"
                )
                return None

            # Extract data payload
            data = resp.get("data")
            if not data:
                logger.warning(f"Auth Service returned empty data for user {user_guid}")
                return None

            return PermissionResponse(**data)

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Auth Service HTTP error for user {user_guid}: "
                f"Status {e.response.status_code} - {e.response.text[:500]}"
            )
            return None
        except httpx.RequestError as e:
            logger.error(f"Auth Service request error for user {user_guid}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching permissions for user {user_guid}: {e}")
            return None

    async def close(self):
        """Close the underlying HTTP client session."""
        await self.client.aclose()


# Initialize Auth Service client singleton
auth_service_client = MainServiceClient()