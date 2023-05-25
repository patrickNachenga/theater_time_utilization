from typing import List

import strawberry

from src.modules.course_learn_outcome.service import CourseLearnOutcomeService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseLearnOutcomeNode, CourseLearnOutcomeInput


@strawberry.type
class CourseLearnOutcomeQuery:
    @strawberry.field
    def get_course_learn_outcome(self) -> Response[List[CourseLearnOutcomeNode]]:
        try:
            result = CourseLearnOutcomeService.get_course_learn_outcome()
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve Course Learn Outcome",
            data=result)


@strawberry.type
class CourseLearnOutcomeMutation:
    @strawberry.field
    def register_course_learn_outcome(self, inputs: List[CourseLearnOutcomeInput]) -> Response[List[CourseLearnOutcomeNode]]:
        try:
            return CourseLearnOutcomeService().register_course_learn_outcome(inputs)
        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed made Change on course learn outcome",
                            data=[])

    # Delete programs type function
    @strawberry.mutation
    async def remove_course_learn_outcome(self, uid: str) -> Response[None]:
        """
        Remove student By UID
        :param uid:
        :return:
        """
        try:
            CourseLearnOutcomeService().remove_course_learn_outcome(uid)
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
