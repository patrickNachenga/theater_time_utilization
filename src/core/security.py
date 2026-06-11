from __future__ import annotations

import logging
import typing
from functools import cached_property

import requests
from fastapi import APIRouter
from strawberry import BasePermission
from strawberry.fastapi import BaseContext
from strawberry.types import Info as _Info
from strawberry.types.info import RootValueType
from strawberry.extensions import FieldExtension

from src.core.config import settings
from src.core.jwt_auth import decode_token_payload
from src.core.redis import redis_dependency
from src.helpers.main_service_client import auth_service_client
from src.shared.models import (
    Permission,
    TokenPayload,
    PermissionResponse,
    CurrentUser,
    UserAuthenticatedModel,
    UserHeadshipsModel,
)
from src.shared.response import Response
from src.shared.response_code import ResponseCode

logger = logging.getLogger(__name__)

route = APIRouter()


def fetch_user(token: str) -> UserAuthenticatedModel | None:
    """
        Fetch User By Token
    :param token:
    :return:
    """
    resp = requests.get(
        f"{settings.UAA_URi}/uaa/user",
        headers={"Authorization": f"Bearer {token}"}
    )

    if resp.status_code == 200 and resp.json():
        user_dict = {
            "authorities": resp.json()["authorities"],
            "profile": resp.json()["user"],
            "headships": UserHeadshipsModel(**resp.json()['headships'])
        }
        return UserAuthenticatedModel(**user_dict)
    return None


# ─── Permission Resolution Service (Async) ─────────────────────────────────


async def resolve_user_permissions(token_payload: TokenPayload) -> PermissionResponse | None:
    """
    Resolve user permissions with Redis caching + Auth Service fallback.

    Flow:
    1. Check Redis cache for user GUID
    2. If cached AND perm_version matches JWT → use cached data
    3. If cached BUT perm_version differs → delete stale cache, fetch from Auth Service
    4. If not cached → fetch from Auth Service
    5. If Auth Service fails → return None (caller handles 503)
    6. If Auth Service succeeds → save to cache, return PermissionResponse
    """
    user_guid = token_payload.guid
    jwt_perm_version = token_payload.perm_version

    if not user_guid:
        logger.warning("No user GUID found in token payload")
        return None

    # Step 1: Try Redis cache
    redis = redis_dependency.redis if redis_dependency.redis else None
    if redis:
        cached_permissions = await redis.get_cached_permissions(user_guid)

        if cached_permissions:
            # Step 2: Cache hit — check version
            if cached_permissions.version == jwt_perm_version:
                logger.debug(
                    f"Permissions for user {user_guid} found in cache "
                    f"(v{cached_permissions.version}), version matches JWT."
                )
                return cached_permissions
            else:
                # Step 3: Cache hit but version mismatch — stale data
                logger.info(
                    f"Permissions for user {user_guid} in cache are stale "
                    f"(cached v{cached_permissions.version} vs JWT v{jwt_perm_version}). "
                    f"Fetching fresh data from Auth Service."
                )
                await redis.delete_cached_permissions(user_guid)
    else:
        logger.warning(
            "Redis is not available. Skipping permission cache — will fetch from "
            "Auth Service directly. This may increase latency."
        )

    # Step 4 & 5: Fetch from Auth Service
    logger.info(f"INFO: Fetching permissions for user {user_guid} from Auth Service...")
    auth_permissions = await auth_service_client.fetch_user_permissions(user_guid)
    if not auth_permissions:
        logger.error(
            f"Failed to fetch permissions for user {user_guid} from Auth Service. "
            f"Unable to resolve user information."
        )
        return None

    # Step 6: Save to cache and return
    if redis:
        await redis.set_cached_permissions(user_guid, auth_permissions)

    logger.info(f"Successfully resolved permissions for user {user_guid} (v{auth_permissions.version})")
    return auth_permissions


# ─── Context ────────────────────────────────────────────────────────────────


class Context(BaseContext):
    """
    Request-scoped context for GraphQL resolvers.

    - JWT token decoding is done once (sync, cached).
    - Permission resolution is done once (async, cached in _resolved_user).
    """

    def __init__(self):
        super().__init__()
        self._raw_token: str | None = None
        self._resolved_user: CurrentUser | None = None
        self._resolved_permissions: PermissionResponse | None = None
        self._permissions_resolved: bool = False

    @cached_property
    def token_payload(self) -> TokenPayload | None:
        """
        Synchronously decode the JWT token from the Authorization header.
        No Redis/HTTP calls here — just token validation.
        Returns None if no valid token is present.
        Cached via @cached_property — computed only once per request.
        """
        if not self.request:
            return None

        authorization = self.request.headers.get("Authorization", None)
        if not authorization:
            logger.debug("No Authorization header found")
            return None

        try:
            token = authorization.split(" ")[1]
        except IndexError:
            logger.warning("Malformed Authorization header")
            return None

        self._raw_token = token
        payload = decode_token_payload(token)

        if not payload:
            logger.warning("JWT validation failed — invalid or expired token")
            return None

        return payload

    @cached_property
    def user_exists(self) -> bool:
        """Quick check if a valid token is present (sync, no permissions)."""
        return self.token_payload is not None

    async def _resolve_permissions_once(self) -> None:
        """
        Resolve permissions exactly once per request.
        Result is stored in private fields for subsequent calls.

        If the Auth Service is unavailable or user is not found,
        the user is treated as UNAUTHORIZED — no fallback CurrentUser is created.
        """
        if self._permissions_resolved:
            return

        self._permissions_resolved = True

        if not self.token_payload:
            return

        token_payload = self.token_payload
        token = self._raw_token or ""

        # Resolve permissions (async — may hit Redis + Auth Service)
        self._resolved_permissions = await resolve_user_permissions(token_payload)

        if not self._resolved_permissions:
            # Auth Service unavailable or user not found → UNAUTHORIZED
            logger.warning(
                f"Unable to resolve permissions for user {token_payload.guid}. "
                f"Auth Service unavailable or user not found. User is unauthorized."
            )
            self._resolved_user = None
            return

        # User found and permissions resolved → build CurrentUser
        # Map `id` from PermissionResponse (Auth Service user id — int)
        # Convert to string for consistent CurrentUser.id type
        perm_id = self._resolved_permissions.id
        user_id = str(perm_id) if perm_id is not None else (str(token_payload.guid) if token_payload.guid else None)
        self._resolved_user = CurrentUser(
            id=user_id,
            uid=user_id,
            guid=token_payload.guid,
            username=self._resolved_permissions.username or token_payload.username,
            email=self._resolved_permissions.email or token_payload.email,
            full_name=self._resolved_permissions.full_name or token_payload.full_name,
            groups=self._resolved_permissions.groups or token_payload.groups or [],
            perm_version=self._resolved_permissions.version,
            permissions=self._resolved_permissions.permissions or [],
            department=self._resolved_permissions.department or token_payload.department,
            department_uid=self._resolved_permissions.department_uid,
            directory=self._resolved_permissions.directory or token_payload.directory,
            directory_uid=self._resolved_permissions.directory_uid,
            pf_number=self._resolved_permissions.pf_number or token_payload.hospital_number or token_payload.pf_number,
            token=token,
        )

    async def get_permission_response(self) -> PermissionResponse | None:
        """
        Asynchronously resolve user permissions.
        Resolved once per request — subsequent calls return cached result.
        """
        await self._resolve_permissions_once()
        return self._resolved_permissions

    async def get_current_user(self) -> CurrentUser | None:
        """
        Asynchronously build the CurrentUser with resolved permissions.
        Resolved once per request — subsequent calls return cached result.
        Called by extensions that need full user context.
        """
        await self._resolve_permissions_once()
        return self._resolved_user

    @property
    def current_user(self) -> CurrentUser | None:
        """
        Synchronously access the resolved CurrentUser.
        Returns None if permissions have not been resolved yet.
        This is used by synchronous CRUD operations after the async
        CustomPermissionExtension has already resolved the user.
        """
        return self._resolved_user

    @cached_property
    def get_client_ip(self):
        return self.request.client.host


Info = _Info[Context, RootValueType]


async def get_context() -> Context:
    return Context()


# ─── Permission Extensions ──────────────────────────────────────────────────


class IsAuthenticated(BasePermission):
    message = "Unauthorized"

    def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:
        if info.context.user_exists:
            return True
        return False


class LoginRequiredExtension(FieldExtension):
    def resolve_async(self, next, root, info, **kwargs):
        is_authenticated = IsAuthenticated()
        if is_authenticated and not is_authenticated.has_permission(info=info, source=typing.Any):
            return Response(
                status=False,
                code=ResponseCode.RESTRICTED_ACCESS,
                message=is_authenticated.message,
                data=None)
        else:
            return next(root, info, **kwargs)


class CustomPermissionExtension(FieldExtension):
    def __init__(self, required_permissions: typing.List[str]):
        self.required_permissions = required_permissions

    async def resolve_async(self, next, root, info, **kwargs):
        # First check if user has a valid token
        if not info.context.user_exists:
            return Response(
                status=False,
                code=ResponseCode.RESTRICTED_ACCESS,
                message='Unauthorized',
                data=None)

        # Resolve permissions (async — may hit Redis/Auth Service)
        # This is cached per-request, so multiple extensions share the same result
        current_user = await info.context.get_current_user()

        if not current_user:
            return Response(
                status=False,
                code=ResponseCode.RESTRICTED_ACCESS,
                message='Unauthorized',
                data=None)

        # Admin users bypass permission checks
        if current_user.is_admin:
            return await next(root, info, **kwargs)

        has_permission = any(
            perm in current_user.permissions
            for perm in self.required_permissions
        ) if current_user.permissions else False

        if has_permission:
            return await next(root, info, **kwargs)
        else:
            return Response(
                status=False,
                code=ResponseCode.UNAUTHORIZED,
                message='Restricted Access',
                data=None)


# ─── Permissions List ───────────────────────────────────────────────────────


permissions: typing.List[Permission] = [
    Permission(
        code="VIEW_ACADEMIC_YEARS",
        name="View Academic Years",
        description="Can View Academic Years",
        service="mnh_theatre_time",
    ),
    Permission(
        code="VIEW_ACTIVE_ACADEMIC_YEARS",
        name="View View Academic Years",
        description="Can View Active Academic Years",
        service="mnh_theatre_time",
    ),
    # Theatre time utilization permissions
    Permission(code="VIEW_PROCEDURE_DELAY_CATEGORIES", name="View Procedure Delay Categories", description="Can view procedure delay categories", service="mnh_theatre_time"),
    Permission(code="REGISTER_PROCEDURE_DELAY_CATEGORIES", name="Register Procedure Delay Categories", description="Can register procedure delay categories", service="mnh_theatre_time"),

    Permission(code="VIEW_PROCEDURE_DELAY_CAUSES", name="View Procedure Delay Causes", description="Can view procedure delay causes", service="mnh_theatre_time"),
    Permission(code="REGISTER_PROCEDURE_DELAY_CAUSES", name="Register Procedure Delay Causes", description="Can register procedure delay causes", service="mnh_theatre_time"),

    Permission(code="VIEW_PROCEDURES", name="View Procedures", description="Can view procedures", service="mnh_theatre_time"),
    Permission(code="REGISTER_PROCEDURES", name="Register Procedures", description="Can register procedures", service="mnh_theatre_time"),

    Permission(code="VIEW_THEATRE_ROLES", name="View Theatre Roles", description="Can view theatre roles", service="mnh_theatre_time"),
    Permission(code="REGISTER_THEATRE_ROLES", name="Register Theatre Roles", description="Can register theatre roles", service="mnh_theatre_time"),

    Permission(code="VIEW_THEATRE_MEMBERS", name="View Theatre Members", description="Can view theatre members", service="mnh_theatre_time"),
    Permission(code="REGISTER_THEATRE_MEMBERS", name="Register Theatre Members", description="Can register theatre members", service="mnh_theatre_time"),

    Permission(code="VIEW_THEATRE_MEMBER_ROLES", name="View Theatre Member Roles", description="Can view theatre member roles", service="mnh_theatre_time"),
    Permission(code="REGISTER_THEATRE_MEMBER_ROLES", name="Register Theatre Member Roles", description="Can register theatre member roles", service="mnh_theatre_time"),

    Permission(code="VIEW_REGIONS", name="View Regions", description="Can view regions", service="mnh_theatre_time"),
    Permission(code="REGISTER_REGIONS", name="Register Regions", description="Can register regions", service="mnh_theatre_time"),

    Permission(code="VIEW_INTERNAL_SOURCES", name="View Internal Sources", description="Can view internal sources", service="mnh_theatre_time"),
    Permission(code="REGISTER_INTERNAL_SOURCES", name="Register Internal Sources", description="Can register internal sources", service="mnh_theatre_time"),

    Permission(code="VIEW_EXTERNAL_SOURCES", name="View External Sources", description="Can view external sources", service="mnh_theatre_time"),
    Permission(code="REGISTER_EXTERNAL_SOURCES", name="Register External Sources", description="Can register external sources", service="mnh_theatre_time"),

    Permission(code="VIEW_THEATRE_UNITS", name="View Theatre Units", description="Can view theatre units", service="mnh_theatre_time"),
    Permission(code="REGISTER_THEATRE_UNITS", name="Register Theatre Units", description="Can register theatre units", service="mnh_theatre_time"),

    Permission(code="VIEW_DEATH_REASONS", name="View Death Reasons", description="Can view death reasons", service="mnh_theatre_time"),
    Permission(code="REGISTER_DEATH_REASONS", name="Register Death Reasons", description="Can register death reasons", service="mnh_theatre_time"),

    Permission(code="VIEW_THEATRE_TIME_RECORDS", name="View Theatre Time Records", description="Can view theatre time records", service="mnh_theatre_time"),
    Permission(code="REGISTER_THEATRE_TIME_RECORDS", name="Register Theatre Time Records", description="Can register theatre time records", service="mnh_theatre_time"),

    Permission(code="VIEW_THEATRE_RECORD_TEAM_MEMBERS", name="View Theatre Record Team Members", description="Can view theatre record team members", service="mnh_theatre_time"),
    Permission(code="REGISTER_THEATRE_RECORD_TEAM_MEMBERS", name="Register Theatre Record Team Members", description="Can register theatre record team members", service="mnh_theatre_time"),

    Permission(code="VIEW_THEATRE_RECORD_DELAYS", name="View Theatre Record Delays", description="Can view theatre record delays", service="mnh_theatre_time"),
    Permission(code="REGISTER_THEATRE_RECORD_DELAYS", name="Register Theatre Record Delays", description="Can register theatre record delays", service="mnh_theatre_time"),
]