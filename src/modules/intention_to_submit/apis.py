from typing import List, Optional

import strawberry
from sqlalchemy import String

from src.core.security import CustomPermissionExtension
from src.core.security import Info
from src.models import IntentionToSubmit
from src.modules.intention_to_submit.service import IntentionToSubmitService, IntentionToSubmitCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import StudentSeminarInput, StudentSeminarNode, IntentionToSubmitNode, IntentionToSubmitInput, \
    StudentSeminarsInputNode, IntentionToSubmitListNode, IntentionToSubmitListNode, PaginationSeminarInput, \
    PaginationInput, IntentionToSubmitStudentListNode


@strawberry.type
class IntentionToSubmitQuery:

    @strawberry.field()
    def get_all_thesis(self, pagination: PaginationInput) -> Response[IntentionToSubmitListNode]:
        try:
            result = IntentionToSubmitCrud.get_multi_paginated(pagination, ["description", "name"],
                                                               IntentionToSubmitListNode)
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Intention to Sub Retrieved successfully",
            data=result)

    @strawberry.field()
    def get_intention_to_submit_thesis(self, pagination: PaginationInput, info: Info) \
            -> Response[IntentionToSubmitStudentListNode]:
        try:
            result = IntentionToSubmitCrud.get_all_intention_to_submit_paginated(info, pagination,
                                                                                 ['title', 'plagiarism_status'])
        except Exception as e:
            print(e)
            result = IntentionToSubmitStudentListNode(items=[], total_count=0)
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Intention to Submit THESIS Retrieved Successfully",
            data=result)

    @strawberry.field()
    def get_thesis(self, pagination: PaginationInput, info: Info) \
            -> Response[IntentionToSubmitStudentListNode]:
        try:
            result = IntentionToSubmitCrud.get_thesis(info, pagination, ['title', 'plagiarism_status'])
        except Exception as e:
            print(e)
            result = IntentionToSubmitStudentListNode(items=[], total_count=0)
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Intention to Submit THESIS Retrieved Successfully",
            data=result)
    @strawberry.field()
    def get_all_intention_to_submit(self) -> Response[List[IntentionToSubmitNode]]:
        try:
            return IntentionToSubmitService.get_all_intention_to_submit()
        except Exception as e:
            print(e)
        return Response(
            status=False,
            code=ResponseCode.NO_RECORD_FOUND,
            message="No Intention to Submit found",
            data=[])

    @strawberry.field()
    def get_intention_to_submit(self, uid: str) -> Response[IntentionToSubmitNode]:
        try:
            result = IntentionToSubmitService(IntentionToSubmit).get_intention_to_submit_by_uid(uid)
        except Exception as e:
            print(e)
            result = None
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Intention to submit Retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Intention to Submit not found",
                data=None)

    @strawberry.field()
    def get_intention_to_submit_by_student_uid(self, student_uid: str) -> Response[
        List[IntentionToSubmitNode]]:
        # try:
        result = IntentionToSubmitService.get_intention_to_submit_by_student_uid(student_uid)

        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Intention to submit Retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Intention to submit not found",
                data=None)


@strawberry.type
class IntentionToSubmitMutation:
    @strawberry.field()
    def register_intention_to_submit(self, inputs: List[IntentionToSubmitInput]) -> Response[IntentionToSubmitNode]:
        try:
            return IntentionToSubmitService(IntentionToSubmit).register_intention_to_submit(inputs)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Intention to submit not found",
                data=None)

    @strawberry.mutation()
    async def remove_intention_to_submit(self, uid: str) -> Response[None]:
        """
        Remove Intention to Submit by UID
        :param uid:
        :return:
        """
        try:
            IntentionToSubmitService.remove_intention_to_submit(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Intention to Submit Removed Successfully",
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Remove Intention to Submit ",
                data=None
            )
