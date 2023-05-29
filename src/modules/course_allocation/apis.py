from typing import List

import strawberry

from src.models import CourseAllocation
from src.modules.course_allocation.service import CourseAllocationService, CourseAllocationCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseAllocationInput, CourseAllocationNode, PaginatedCourse, PaginationInput, \
    PaginatedCourseAllocation


@strawberry.type
class CourseAllocationQuery:

    @strawberry.field
    def get_course_allocations(self, pagination: PaginationInput) -> Response[PaginatedCourse]:
        try:
            result = CourseAllocationCrud.get_multi_paginated(pagination, ['program_course_id', 'staff_id',], PaginatedCourseAllocation)
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Course Category Retrieved successfully",
            data=result)


@strawberry.type
class CourseAllocationMutation:
    @strawberry.field
    def register_course_allocations(self, inputs: List[CourseAllocationInput]) -> Response[List[CourseAllocationNode]]:
        try:
            return CourseAllocationService(CourseAllocation).register_course_allocations(inputs)

        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to Register Course Allocation",
                            data=[])

    @strawberry.mutation
    async def remove_course_allocation(self, uid: str) -> Response[None]:
        """
        Remove course allocation by UID
        :param uid:
        :return:
        """
        try:
            result = CourseAllocationService(CourseAllocation).remove_course_allocation(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Course Allocation Removed Successfully",
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Remove Course Allocation",
                data=None
            )
