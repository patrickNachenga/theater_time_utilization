from typing import List

import strawberry

from src.models import CourseAllocation
from src.modules.course_allocation.service import CourseAllocationService, CourseAllocationCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseAllocationInput, CourseAllocationNode, PaginatedCourse, PaginationInput, \
    CourseAllocationListNode


@strawberry.type
class CourseAllocationQuery:

    @strawberry.field
    def get_course_allocations(self, pagination: PaginationInput) -> Response[PaginatedCourse]:
        try:
            result = CourseAllocationCrud.get_multi_paginated(pagination, [], CourseAllocationListNode)
        except Exception as e:
            print(e)
            result = CourseAllocationListNode(items=[], total_count=0)
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Course Allocation Retrieved successfully",
            data=result)

    @strawberry.field
    def get_course_allocation(self, uid: str) -> Response[CourseAllocationNode]:
        try:
            result = CourseAllocationService(CourseAllocation).get_course_by_uid(uid)
        except Exception as e:
            print(e)
            result = None
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Successfully Retrieve Course Allocation",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Course Allocation not found",
                data=result)


@strawberry.type
class CourseAllocationMutation:
    @strawberry.field
    def register_course_allocations(self, inputs: List[CourseAllocationInput]) -> Response[CourseAllocationListNode]:
        try:
            return CourseAllocationService(CourseAllocation).register_course_allocations(inputs)

        except Exception as e:
            print(e)
            return Response(status=True, code=ResponseCode.FAILURE, message="Failed to Register Course Allocation",
                            data=CourseAllocationListNode(items=[], total_count=0), )

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
