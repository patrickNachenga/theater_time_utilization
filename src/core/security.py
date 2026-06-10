from __future__ import annotations

import typing

import requests
from fastapi import APIRouter
from strawberry import BasePermission
from strawberry.fastapi import BaseContext
from strawberry.types import Info as _Info
from strawberry.types.info import RootValueType
from strawberry.utils.cached_property import cached_property
from strawberry.extensions import FieldExtension

from src.core.config import settings
from src.core.jwt_auth import get_data
from src.shared.models import Permission, UserAuthenticatedModel, UserHeadshipsModel, UserAuthModel
from src.shared.response import Response
from src.shared.response_code import ResponseCode

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
    # resp = requests.get(
    #     "http://127.0.0.1:8000/uaa/user",
    #     headers={"Authorization": f"Bearer {token}"},
    # )

    if resp.status_code == 200 and resp.json():
        user_dict = {
            "authorities": resp.json()["authorities"],
            "profile": resp.json()["user"],
            "headships": UserHeadshipsModel(**resp.json()['headships'])
        }
        return UserAuthenticatedModel(**user_dict)
    return None


class IsAuthenticated(BasePermission):
    message = "Unauthorized"

    def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:
        if info.context.user:
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
    def __init__(self, required_permissions):
        self.required_permissions = required_permissions

    def resolve_async(self, next, root, info, **kwargs):
        # return next(root, info, **kwargs)
        if info.context.user:
            # return next(root, info, **kwargs)
            has_permission = any(perm in info.context.user.authorities for perm in self.required_permissions)
            if has_permission:
                return next(root, info, **kwargs)
            else:
                return Response(
                    status=False,
                    code=ResponseCode.UNAUTHORIZED,
                    message='Restricted Access',
                    data=None)
        return Response(
            status=False,
            code=ResponseCode.RESTRICTED_ACCESS,
            message='Unauthorized',
            data=None)


class Context(BaseContext):
    @cached_property
    def user(self) -> UserAuthModel | None | Response:
        if not self.request:
            return None
        authorization = self.request.headers.get("Authorization", None)
        if authorization:
            user_data = get_data(authorization.split(" ")[1])
            if user_data:
                return UserAuthModel(**user_data)
            return None
        return None

    @cached_property
    def get_client_ip(self):
        return self.request.client.host


Info = _Info[Context, RootValueType]


async def get_context() -> Context:
    return Context()


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
