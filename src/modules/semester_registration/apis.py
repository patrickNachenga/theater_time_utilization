from typing import Optional

import strawberry

from src.core.security import CustomPermissionExtension
from src.modules.semester_registration.service import SemesterRegistrationService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import PaginationInput, SemesterRegistrationListNode


@strawberry.type
class SemesterRegistrationQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_COURSE_ALLOCATIONS"])])
    def get_semester_registrations(self, pagination: PaginationInput) -> Response[Optional[SemesterRegistrationListNode]]:
        try:
            result = SemesterRegistrationService().get_semester_registrations(pagination)
        except Exception as e:
            print(e)
            result = SemesterRegistrationListNode(items=[],total_count=0)
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve semester registration",
            data=result)

    @strawberry.field
    def get_student_semester_registrations(self,student_uid: str) -> Response[Optional[SemesterRegistrationListNode]]:
        try:
            result = SemesterRegistrationService().get_student_semester_registrations(student_uid)
        except Exception as e:
            print(e)
            result = SemesterRegistrationListNode(items=[],total_count=0)
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve semester registrations",
            data=result)



