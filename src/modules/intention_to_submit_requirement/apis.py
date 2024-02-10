from typing import List, Optional

import strawberry

from src.core.security import CustomPermissionExtension
from src.models import IntentionToSubmitRequirement
from src.modules.intention_to_submit_requirement.service import IntentionToSubmitRequirementService, \
    IntentionToSubmitRequirementCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import PaginationInput, IntentionToSubmitRequirementInput, IntentionToSubmitRequirementNode, \
    IntentionToSubmitRequirementListNode


@strawberry.type
class IntentionToSubmitRequirementQuery:
    @strawberry.field()
    def get_intention_to_submit_requirements(self, pagination: PaginationInput) \
            -> Response[IntentionToSubmitRequirementListNode]:
        try:
            result = IntentionToSubmitRequirementCrud.get_multi_paginated(pagination,
                                                                          ["minimum_seminar", "minimum_manuscript"],
                                                                          IntentionToSubmitRequirementListNode)
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Intention To Submit Requirement Retrieved successfully",
            data=result)


    @strawberry.field()
    def get_intention_to_submit_requirement_by_category(self, category_uid: str) \
            -> Response[List[IntentionToSubmitRequirementNode]]:
        try:
            result = IntentionToSubmitRequirementService(IntentionToSubmitRequirement). \
                get_intention_to_submit_requirement_by_category(category_uid)
        except Exception as e:
            print(e)
            result = None
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Intention To Submit Requirement Retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Intention To Submit Requirement not found",
                data=None)

    @strawberry.field()
    def get_intention_to_submit_requirement_by_uid(self, uid: str) -> Response[IntentionToSubmitRequirementNode]:
        try:
            result = IntentionToSubmitRequirementService(IntentionToSubmitRequirement). \
                get_intention_to_submit_requirement_by_uid(uid)
        except Exception as e:
            print(e)
            result = None
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Intention To Submit Requirement Retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Intention To Submit Requirement not found",
                data=None)


@strawberry.type
class IntentionToSubmitRequirementMutation:
    @strawberry.field()
    def register_intention_to_submit_requirement(self, inputs: List[IntentionToSubmitRequirementInput]) \
            -> Response[IntentionToSubmitRequirementNode]:
        try:
            return IntentionToSubmitRequirementService(IntentionToSubmitRequirement). \
                register_get_intention_to_submit_requirement(inputs)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="No Intention To Submit Requirement found",
                data=None)

    @strawberry.mutation()
    async def remove_intention_to_submit_requirement(self, uid: str) -> Response[None]:
        """
        Remove Seminar Type by UID
        :param uid:
        :return:
        """
        try:
            IntentionToSubmitRequirementService.remove_intention_to_submit_requirement(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Intention to submit requirement Removed Successfully",
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Remove Intention to submit requirement",
                data=None
            )
