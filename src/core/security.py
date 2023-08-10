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
from src.shared.models import Permission, UserAuthenticatedModel, UserHeadshipsModel
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
        code="VIEW_ACTIVE_ACADEMIC_YEARS",
        name="View View Academic Years",
        description="Can View Active Academic Years",
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
        code="VIEW_ACADEMIC_YEAR_SEMESTERS",
        name="View Academic Year Semesters",
        description="Can View Academic Year Semesters",
        service="registration",
    ),
    Permission(
        code="VIEW_ACADEMIC_YEAR_SEMESTER_BY_ACADEMIC_YEAR",
        name="View Academic Year Semeter By Academic YEar",
        description="Can View Academic Year Semeter By using Academic Year",
        service="registration",
    ),
    Permission(
        code="REGISTER_ACADEMIC_YEAR_SEMESTERS",
        name="Register Academic Year Semesters",
        description="Can Register Academic Year Semesters",
        service="registration",
    ),
    Permission(
        code="REMOVE_ACADEMIC_YEAR_SEMESTER",
        name="Remove Academic Year Semeter",
        description="Can Remove Academic Year Semeter",
        service="registration",
    ),
    Permission(
        code="VIEW_EXAM_CATEGORIES",
        name="View Exam Categories",
        description="Can View Exam Categories",
        service="registration",
    ),
    Permission(
        code="REGISTER_EXAM_CATEGORIES",
        name="Register Exam Categories",
        description="Can Register Exam Categories",
        service="registration",
    ),
    Permission(
        code="REMOVE_EXAM_CATEGORY",
        name="Remove Exam Category",
        description="Can Remove Exam Category",
        service="registration",
    ),
    Permission(
        code="VIEW_EXAM_CATEGORY_GROUPS",
        name="View Exam Category Groups",
        description="Can View Exam Category Groups",
        service="registration",
    ),
    Permission(
        code="REGISTER_EXAM_CATEGORY_GROUPS",
        name="Register Exam Category Groups",
        description="Can Register Exam Category Groups",
        service="registration",
    ),
    Permission(
        code="REMOVE_EXAM_CATEGORY_GROUP",
        name="Remove Exam Category Group",
        description="Can Remove Exam Category Group",
        service="registration",
    ),
    Permission(
        code="VIEW_EXAM_COURSEWORK",
        name="View Exam Coursework",
        description="Can View Exam Coursework",
        service="registration",
    ),
    Permission(
        code="REGISTER_EXAM_COURSEWORK",
        name="Register Exam Coursework",
        description="Can Register Exam Coursework",
        service="registration",
    ),
    Permission(
        code="REMOVE_EXAM_COURSEWORK",
        name="Remove Exam Coursework",
        description="Can Remove Exam Coursework",
        service="registration",
    ),
    Permission(
        code="VIEW_EXAM_RESULTS",
        name="View Exam Results",
        description="Can View Exam Results",
        service="registration",
    ),
    Permission(
        code="REGISTER_EXAM_RESULTS",
        name="Register Exam Results",
        description="Can Register Exam Results",
        service="registration",
    ),
    Permission(
        code="REMOVE_EXAM_RESULT",
        name="Remove Exam Result",
        description="Can Remove Exam Result",
        service="registration",
    ),
    Permission(
        code="VIEW_COURSES",
        name="View Course",
        description="Can View Course",
        service="registration",
    ),
    Permission(
        code="REGISTER_COURSES",
        name="Register Courses",
        description="Can Register Courses",
        service="registration",
    ),
    Permission(
        code="REMOVE_COURSE",
        name="Remove Exam Results",
        description="Can Delete Course",
        service="registration",
    ),
    Permission(
        code="VIEW_COURSE_ALLOCATIONS",
        name="View Course allocations",
        description="Can View Course allocations",
        service="registration",
    ),
    Permission(
        code="VIEW_STAFF_COURSE_ALLOCATION_BY_ACADEMIC_YEAR",
        name="View Staff Course allocation By Academic Year",
        description="Can View Staff Course allocation By Year",
        service="registration",
    ),
    Permission(
        code="VIEW_COURSE_ALLOCATION_BY_PROGRAM_COURSE",
        name="View Staff Course allocation By Program Course",
        description="Can View Staff Course Program Course",
        service="registration",
    ),
    Permission(
        code="VIEW_STAFF_COURSE_ALLOCATIONS",
        name="View Staff Course allocations",
        description="Can View Staff Course allocations",
        service="registration",
    ),
    Permission(
        code="REGISTER_COURSE_ALLOCATIONS",
        name="Register Courses",
        description="Can Register Course allocations",
        service="registration",
    ),
    Permission(
        code="REMOVE_COURSE_ALLOCATION",
        name="Remove Course Allocation",
        description="Can Delete Course allocation",
        service="registration",
    ),
    Permission(
        code="UPDATE_STAFF_COURSE_ALLOCATION",
        name="Update Staff Course Allocation",
        description="Can Update Staff Course allocation",
        service="registration",
    ),
    Permission(
        code="VIEW_COURSE_CATEGORIES",
        name="View Course Categories",
        description="Can View Course Categories",
        service="registration",
    ),
    Permission(
        code="REGISTER_COURSE_CATEGORY",
        name="Register Course",
        description="Can Register Course Category",
        service="registration",
    ),
    Permission(
        code="REMOVE_COURSE_CATEGORY",
        name="Remove Course Category",
        description="Can Delete Course category",
        service="registration",
    ),
    Permission(
        code="VIEW_PROGRAM_COURSE_ASSESSMENTS",
        name="VIEW Program Course Assessments",
        description="Can View Program Course Assessments",
        service="registration",
    ),
    Permission(
        code="REGISTER_PROGRAM_COURSE_ASSESSMENTS",
        name="Register Program Course Assessments",
        description="Can register Program Course Assessments",
        service="registration",
    ),
    Permission(
        code="REMOVE_PROGRAM_COURSE_ASSESSMENT",
        name="Remove Program Course Assessment",
        description="Can Delete Program Course Assessment",
        service="registration",
    ),
    Permission(
        code="VIEW_PROGRAMS",
        name="View Programs",
        description="Can View Programs",
        service="registration",
    ),
    Permission(
        code="REGISTER_PROGRAMS",
        name="Register Programs",
        description="Can Register Programs",
        service="registration",
    ),
    Permission(
        code="REMOVE_PROGRAM",
        name="Remove Program",
        description="Can Delete Program",
        service="registration",
    ),
    Permission(
        code="VIEW_PROGRAM_SEMESTERS",
        name="View Program Semesters",
        description="Can View Program Semesters",
        service="registration",
    ),
    Permission(
        code="REGISTER_PROGRAM_SEMESTERS",
        name="Register Program Semesters",
        description="Can Register Program Semesters",
        service="registration",
    ),
    Permission(
        code="REMOVE_PROGRAM_SEMESTER",
        name="Remove Program Semester",
        description="Can Delete Program Semester",
        service="registration",
    ),
    Permission(
        code="VIEW_PROGRAM_COURSES",
        name="View Program Courses",
        description="Can View Program Courses",
        service="registration",
    ),
    Permission(
        code="VIEW_PROGRAM_COURSES_BY_SEMESTER",
        name="View Program Courses By Semester",
        description="Can View Program Courses By Selected Semester",
        service="registration",
    ),
    Permission(
        code="REGISTER_PROGRAM_COURSES",
        name="Register Program Courses",
        description="Can Register Program Courses",
        service="registration",
    ),
    Permission(
        code="REMOVE_PROGRAM_COURSE",
        name="REMOVE Program Course",
        description="Can Delete Program Course",
        service="registration",
    ),
    Permission(
        code="VIEW_PROGRAM_CATEGORIES",
        name="View Program Categories",
        description="Can View Program Categories",
        service="registration",
    ),
    Permission(
        code="REGISTER_PROGRAM_CATEGORIES",
        name="Register Program Categories",
        description="Can Register Program Categories",
        service="registration",
    ),
    Permission(
        code="REMOVE_PROGRAM_CATEGORY",
        name="REMOVE Program Category",
        description="Can Delete Program Category",
        service="registration",
    ),
    Permission(
        code="VIEW_PROGRAM_CAPACITIES",
        name="View Program Capacities",
        description="Can View Program Capacities",
        service="registration",
    ),
    Permission(
        code="REGISTER_PROGRAM_CAPACITIES",
        name="Register Program Capacities",
        description="Can Register Program Capacities",
        service="registration",
    ),
    Permission(
        code="REMOVE_PROGRAM_CAPACITY",
        name="REMOVE Program Capacity",
        description="Can Delete Program Capacity",
        service="registration",
    ),
    Permission(
        code="VIEW_COURSE_LEARN_OUTCOMES",
        name="View Course Learning Outcomes",
        description="Can View Course  Learning Outcomes",
        service="registration",
    ),
    Permission(
        code="REGISTER_COURSE_LEARN_OUTCOMES",
        name="Register Course Learning Outcomes",
        description="Can Register Course Learning Outcomes",
        service="registration",
    ),
    Permission(
        code="REMOVE_COURSE_LEARN_OUTCOME",
        name="Remove Course Learning Outcome",
        description="Can Delete Course Learning Outcome",
        service="registration",
    ),
    Permission(
        code="VIEW_EXAM_RESULT_SUMMARIES",
        name="View Exam Result Summaries",
        description="Can View Exam Result Summaries",
        service="registration",
    ),
    Permission(
        code="REGISTER_EXAM_RESULT_SUMMARIES",
        name="Register Exam Result Summaries",
        description="Can Register Exam Result Summaries",
        service="registration",
    ),
    Permission(
        code="REMOVE_EXAM_RESULT_SUMMARY",
        name="Remove Exam Result Summary",
        description="Can Delete Exam Result Summary",
        service="registration",
    ),
    Permission(
        code="VIEW_STUDENT_SEMESTER_REGISTRATIONS",
        name="View Student Semester Registrations",
        description="Can View Student Semester Registrations",
        service="registration",
    ),
    Permission(
        code="VIEW_EXAM_RESULTS",
        name="View Exam Results",
        description="Can View Exam Results",
        service="registration",
    ),
    Permission(
        code="REGISTER_EXAM_RESULTS",
        name="Register Exam Results",
        description="Can Register Exam Results",
        service="registration",
    ),
    Permission(
        code="REMOVE_EXAM_RESULT",
        name="Remove Exam Result",
        description="Can Delete Exam Result",
        service="registration",
    ),
    Permission(
        code="VIEW_GROUPS",
        name="View Groups",
        description="Can View Groups",
        service="registration",
    ),
    Permission(
        code="REGISTER_GROUPS",
        name="Register Groups",
        description="Can Register Groups",
        service="registration",
    ),
    Permission(
        code="REMOVE_GROUP",
        name="Remove Group",
        description="Can Delete Group",
        service="registration",
    ),

    Permission(
        code="VIEW_STUDENT_COURSE_REGISTRATIONS",
        name="View Student Course Registrations",
        description="Can View Student Course Registrations",
        service="registration",
    ),
    Permission(
        code="VIEW_STUDENT_CURRENT_COURSE_REGISTRATIONS",
        name="View Student current Course Registrations",
        description="Can View current Student Course Registrations",
        service="registration",
    ),
    Permission(
        code="REGISTER_STUDENT_COURSES",
        name="Register Student Courses",
        description="Can Register Student Courses",
        service="registration",
    ),
]
