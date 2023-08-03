from typing import List, Optional

import strawberry

from src.models import CourseAllocation
from src.modules.course_allocation.service import CourseAllocationService, CourseAllocationCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseAllocationInput, CourseAllocationNode, PaginationInput, CourseAllocationListNode, \
    StaffAllocationInputNode, CourseAllocationStaffUpdateInput


@strawberry.type
class CourseAllocationQuery:

    @strawberry.field
    def get_course_allocations(self, pagination: PaginationInput) -> Response[CourseAllocationListNode]:
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
            print('test')
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Course Allocation not found",
                data=CourseAllocationNode(uid=None, program_course_uid=None, program_course=None, staff_uid=None))

    @strawberry.field
    def get_staff_course_allocation(self, inputs: StaffAllocationInputNode) -> Response[CourseAllocationListNode]:
        result = None
        try:
            result = CourseAllocationService(CourseAllocation).get_staff_course_allocation(inputs)
            if result:
                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Successfully Retrieve Course Allocation",
                    data=CourseAllocationListNode(items=result,total_count=len(result)))
            else:
                return Response(
                    status=False,
                    code=ResponseCode.NO_RECORD_FOUND,
                    message="Course Allocation not found",
                    data=CourseAllocationListNode(items=[],total_count=0))

        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Course Allocation not found, An exception occurred",
                data=CourseAllocationListNode(items=[],total_count=0))



    @strawberry.field
    def get_staff_course_allocation_by_Academic_year_semesters(self, inputs: StaffAllocationInputNode) -> Response[
        List[CourseAllocationNode]]:
        result = None
        try:
            result = CourseAllocationService(CourseAllocation).get_staff_course_allocation(inputs)

        except Exception as e:
            print(e)

        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Successfully Retrieve Course Allocation",
                data=result,
            )
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Course Allocation not found",
                data=List[CourseAllocationNode(uid="", program_course_uid='', program_course=None, staff_uid="")])

    @strawberry.field
    async def get_course_allocation_by_program_course_uid(self, program_course_uid: str) -> Response[CourseAllocationListNode]:
        try:
            course_allocation = CourseAllocationService.get_course_allocation_by_program_course_uid(
                program_course_uid)
            if course_allocation:
                return course_allocation
            raise ValueError("Unable to retrieve course allocation")
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                data=CourseAllocationListNode(items=[], total_count=0),
                message="Unable to retrieve course allocation"
            )


@strawberry.type
class CourseAllocationMutation:
    @strawberry.field
    def register_course_allocations(self, inputs: List[CourseAllocationInput]) -> Response[CourseAllocationListNode]:
        try:
            return CourseAllocationService(CourseAllocation).register_course_allocations(inputs)

        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to Register Course Allocation",
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
            print(result)
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

    @strawberry.field
    def update_course_allocation_staff(self, inputs: CourseAllocationStaffUpdateInput) -> Response[
        CourseAllocationNode]:
        try:
            course_allocations = CourseAllocationService(CourseAllocation).update_course_allocation_staff(inputs)
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=course_allocations,
                            message=f"Successfully updated Course Allocation Staff")

        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to update course allocation staff",
                            data=CourseAllocationNode(None))
