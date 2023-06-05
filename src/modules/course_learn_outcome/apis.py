from typing import List

import strawberry

from src.models import CourseLearnOutcome
from src.modules.course_learn_outcome.service import CourseLearnOutcomeService, CourseLearnOutcomeCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseLearnOutcomeNode, CourseLearnOutcomeInput, PaginationInput, CourseLearnOutcomeListNode


@strawberry.type
class CourseLearnOutcomeQuery:
    # @strawberry.field
    # def get_course_learn_outcomes(self, pagination: PaginationInput) -> Response[CourseLearnOutcomeListNode]:
    #     try:
    #         result = CourseLearnOutcomeCrud.get_multi_paginated(pagination, [],CourseLearnOutcomeListNode)
    #     except Exception as e:
    #         print(e)
    #         result = CourseLearnOutcomeListNode(items=[], total_count=0)
    #     return Response(
    #         status=True,
    #         code=ResponseCode.SUCCESS,
    #         message="Successfully Retrieve Course Learn Outcome",
    #         data=result)

    @strawberry.field
    def get_course_learn_outcomes_by_course(self, course_uid: str) -> Response[List[CourseLearnOutcomeNode]]:
        try:
            result = CourseLearnOutcomeService.get_course_learn_outcome_by_course(course_uid)
        except Exception as e:
            print(e)
            result = None
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Successfully Retrieve Course Learn Outcome",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Course Learn Outcome not found",
                data=[])

    @strawberry.field
    def get_course_learn_outcome(self, uid: str) -> Response[CourseLearnOutcomeNode]:
        try:
            result = CourseLearnOutcomeService(CourseLearnOutcome).get_course_learn_outcome_by_uid(uid)
        except Exception as e:
            print(e)
            result = None
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Course Learn Outcome Retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Course Learn Outcome not found",
                data=None)


@strawberry.type
class CourseLearnOutcomeMutation:
    @strawberry.field
    def register_course_learn_outcome(self, inputs: CourseLearnOutcomeInput) -> Response[CourseLearnOutcomeNode]:
        try:
            return CourseLearnOutcomeService(CourseLearnOutcome).register_course_learn_outcome(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to register course learn outcome",
                            data=None)

    # Delete programs type function
    @strawberry.mutation
    async def remove_course_learn_outcome(self, uid: str) -> Response[None]:
        """
        Remove student By UID
        :param uid:
        :return:
        """
        try:
            CourseLearnOutcomeService.remove_course_learn_outcome(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Course Learn Outcome Removed Successfully",
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Remove Course Learn Outcome",
                data=None
            )
