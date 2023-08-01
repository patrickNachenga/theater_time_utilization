from __future__ import annotations

import typing

import requests
from fastapi import APIRouter
from starlette.websockets import WebSocket
from strawberry import BasePermission
from strawberry.fastapi import BaseContext
from strawberry.http.typevars import Request
from strawberry.types import Info as _Info
from strawberry.types.info import RootValueType
from strawberry.utils.cached_property import cached_property
from strawberry.extensions import FieldExtension

from src.core.config import settings
from src.shared.models import Permission, UserAuthenticatedModel
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
        headers={"Authorization": f"Bearer {token}"},
    )
    if resp.status_code == 200 and resp.json():
        return UserAuthenticatedModel(**resp.json())
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
        is_authenticated = IsAuthenticated()
        # return next(root, info, **kwargs)
        if is_authenticated and not is_authenticated.has_permission(info=info, source=typing.Any):
            return Response(
                status=False,
                code=ResponseCode.RESTRICTED_ACCESS,
                message=is_authenticated.message,
                data=None)
        else:
            return next(root, info, **kwargs)
            from src.helpers.utils import auth_user_has_permission
            if auth_user_has_permission(info, self.required_permissions):
                return next(root, info, **kwargs)
        return Response(
            status=False,
            code=ResponseCode.RESTRICTED_ACCESS,
            message=is_authenticated.message,
            data=None)


class Context(BaseContext):
    @cached_property
    def user(self) -> UserAuthenticatedModel | None:
        """
            Get User From Token
        :return:
        """
        if not self.request:
            return None
        authorization = self.request.headers.get("Authorization", None)
        if authorization:
            return fetch_user(authorization.split(" ")[1])
        if self.request.get("access_token"):
            print(self.request.get("access_token"))
            return fetch_user(self.request.get("access_token"))
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
        service="registration",
    ),
    Permission(
        code="REGISTER_ACADEMIC_YEARS",
        name="Register Academic Years",
        description="Can Register Academic Years",
        service="registration",
    ),
    Permission(
        code="REMOVE_ACADEMIC_YEAR",
        name="Remove Academic Years",
        description="Can Remove Academic Years",
        service="registration",
    ),
    Permission(
        code="VIEW_ACADEMIC_YEAR_SEMESTER",
        name="View Academic Year Semeter",
        description="Can View Academic Year Semeter",
        service="registration",
    ),
    Permission(
        code="REGISTER_ACADEMIC_YEAR_SEMESTER",
        name="Register Academic Year Semeter",
        description="Can Register Academic Year Semeter",
        service="registration",
    ),
    Permission(
        code="REMOVE_ACADEMIC_YEAR_SEMESTER",
        name="Remove Academic Year Semeter",
        description="Can Remove Academic Year Semeter",
        service="registration",
    ),
    Permission(
        code="VIEW_EXAM_CATEGORY",
        name="View Exam Category",
        description="Can View Exam Category",
        service="registration",
    ),
    Permission(
        code="REGISTER_EXAM_CATEGORY",
        name="Register Exam Category",
        description="Can Register Exam Category",
        service="registration",
    ),
    Permission(
        code="REMOVE_EXAM_CATEGORY",
        name="Remove Exam Category",
        description="Can Remove Exam Category",
        service="registration",
    )

]