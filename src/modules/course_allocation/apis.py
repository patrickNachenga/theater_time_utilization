from typing import List, Optional

import strawberry

from src.core.security import CustomPermissionExtension, Info
from src.models import CourseAllocation
from src.modules.course_allocation.service import CourseAllocationService, CourseAllocationCrud
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import CourseAllocationInput, CourseAllocationNode, PaginationInput, CourseAllocationListNode, \
    ProgramCourseAssessmentNode, \
    ProgramCourseAssessmentUpdateExceedInput, \
    StaffAllocationInputNode, CourseAllocationStaffUpdateInput, StaffCourseAllocationBySemesterInputs, \
    StaffCourseAllocationBySemesterNode, InstructorSemesterCourseAllocationInputNode, ProgramCourseNode


@strawberry.type
class CourseAllocationQuery:

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_COURSE_ALLOCATIONS"])])
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

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_COURSE_ALLOCATIONS"])])
    def get_course_allocation(self, uid: str) -> Response[CourseAllocationNode]:
        try:
            return CourseAllocationService(CourseAllocation).get_course_by_uid(uid)
        except Exception as e:
            print(e)
            return Response(
                status=True,
                code=ResponseCode.FAILURE,
                message="Failed To Get Course Allocation",
                data=CourseAllocationNode(uid=None, program_course_uid=None, program_course=None, staff_uid=None))

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_COURSE_ALLOCATIONS_BY_STAFF"])])
    def get_instructor_semester_course_allocation(self, inputs: InstructorSemesterCourseAllocationInputNode,
                                                  info: Info) -> Response[List[ProgramCourseNode]]:
        try:
            if info.context.user is None:
                return Response(
                    status=False,
                    code=ResponseCode.UNAUTHORIZED,
                    message="Your session has expired please reset your session",
                    data=[])

            result = CourseAllocationService(CourseAllocation).get_instructor_semester_course_allocation(inputs, info)
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
                    data=[])

        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Course Allocation not found, An exception occurred",
                data=[])

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_STAFF_COURSE_ALLOCATION_BY_ACADEMIC_YEAR"])])
    def get_staff_course_allocation_by_Academic_year_semesters(self, inputs: StaffCourseAllocationBySemesterInputs) -> (
            Response)[List[StaffCourseAllocationBySemesterNode]]:
        result = None
        try:
            result = CourseAllocationService(CourseAllocation).get_staff_course_allocation_by_Academic_year_semesters(
                inputs)
        except Exception as e:
            print(e)

        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Successfully Retrieve Staff Course Allocation",
                data=result,
            )
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Course Allocation not found",
                data=List[CourseAllocationNode(uid="", program_course_uid='', program_course=None, staff_uid="")])

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_COURSE_ALLOCATION_BY_PROGRAM_COURSE"])])
    async def get_course_allocation_by_program_course_uid(self, program_course_uid: str) -> (
            Response)[CourseAllocationListNode]:
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
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_COURSE_ALLOCATIONS"])])
    def register_course_allocations(self, inputs: List[CourseAllocationInput]) -> (
            Response)[CourseAllocationListNode]:
        try:
            return CourseAllocationService(CourseAllocation).register_course_allocations(inputs)

        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to Register Course Allocation",
                            data=CourseAllocationListNode(items=[], total_count=0), )

    @strawberry.mutation(extensions=[CustomPermissionExtension(["VIEW_COURSE_ALLOCATIONS_BY_STAFF"])])
    def forward_instructor_course_result(self, program_course_uids: List[str], info: Info) -> Response[None]:
        try:
            if info.context.user is None:
                return Response(
                    status=False,
                    code=ResponseCode.UNAUTHORIZED,
                    message="Your session has expired please reset your session",
                    data=None)
            return CourseAllocationService(CourseAllocation).forward_instructor_course_result(program_course_uids, info)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Forward Course Results to HOD",
                data=None
            )

    @strawberry.mutation(extensions=[CustomPermissionExtension(["REMOVE_COURSE_ALLOCATION"])])
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

    @strawberry.field(extensions=[CustomPermissionExtension(["UPDATE_STAFF_COURSE_ALLOCATION"])])
    def update_course_allocation_staff(self, inputs: CourseAllocationStaffUpdateInput) -> (
            Response)[CourseAllocationNode]:
        try:
            course_allocations = CourseAllocationService(CourseAllocation).update_course_allocation_staff(inputs)
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=course_allocations,
                            message=f"Successfully updated Course Allocation Staff")

        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to update course allocation staff",
                            data=CourseAllocationNode(None)) @ strawberry.field

    @strawberry.field(extensions=[CustomPermissionExtension(["UPDATE_STAFF_COURSE_ALLOCATION"])])
    def staff_update_allocation_assessment_item(self, inputs: ProgramCourseAssessmentUpdateExceedInput) -> (
            Response)[ProgramCourseAssessmentNode]:
        try:
            program_course_assessment = CourseAllocationService(
                CourseAllocation).staff_update_allocation_assessment_item(
                inputs)
            if program_course_assessment:
                return Response(status=True, code=ResponseCode.SUCCESS,
                                data=program_course_assessment,
                                message=f"Successfully updated")
            else:
                return Response(status=False, code=ResponseCode.FAILURE,
                                data=[],
                                message=f"Failed to updated")

        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to update",
                            data=[])
