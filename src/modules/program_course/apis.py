from typing import List, Optional

import strawberry

from src.core.security import CustomPermissionExtension
from src.models import ProgramCourse
from src.modules.program_course.service import ProgramCourseService, ProgramCourseCrud
from src.modules.program_semester.service import ProgramSemesterService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import PaginationInput, ProgramCourseListNode, ProgramCourseInput, ProgramCourseNode, \
    RequestProgramSemester


@strawberry.type
class ProgramCourseQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_PROGRAM_COURSES"])])
    def get_program_courses(self, pagination: PaginationInput, program_semester: Optional[str] = None) -> Response[
        Optional[ProgramCourseListNode]]:
        try:
            unique_list = []
            # Verify and get supplied Program uid. and get existed program model
            if program_semester:
                try:
                    prog_sem = ProgramSemesterService.get_program_semester_by_uid(program_semester)
                    if prog_sem is None:
                        raise ValueError("no data found from supplied details")
                    else:
                        unique_list.append({"program_semester_id": prog_sem.id})

                except Exception as e:
                    print(e)
                    return Response(
                        status=False,
                        code=ResponseCode.FAILURE,
                        data=ProgramCourseListNode(items=[], total_count=0),
                        message="no data found from supplied details"
                    )
            result = ProgramCourseCrud.get_multi_paginated(pagination,
                                                           ['credit', 'independent_study_hours', 'pass_hours',
                                                            'lecture_hours', 'seminar_hours', 'practical_hours',
                                                            'assignment_hours', 'assignment_hours', 'assignment_hours'],
                                                           ProgramCourseListNode,
                                                           ["course", "course_category", "program_semester"],
                                                           unique_list)
        except Exception as e:
            print(e)
            result = ProgramCourseListNode(items=[], total_count=0)
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve Program Courses",
            data=result)

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_PROGRAM_COURSES"])])
    def get_program_course(self, uid: str) -> Response[ProgramCourseNode | None]:
        try:
            result = ProgramCourseService.get_program_course_by_uid(uid)
        except Exception as e:
            print(e)
            result = None
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Successfully Retrieve Program Course",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Program Course not found",
                data=None)

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_PROGRAM_COURSES"])])
    async def get_program_course_by_program_semester_uid(self, program_semester_uid: str) -> Response[
        Optional[ProgramCourseListNode]]:
        try:
            program_courses = ProgramCourseService.get_program_course_by_program_semester_uid(program_semester_uid)
            if program_courses:
                return program_courses
            raise ValueError("Unable to retrieve program courses")
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                data=ProgramCourseListNode(items=[], total_count=0),
                message="Unable to retrieve program courses"
            )

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_PROGRAM_COURSES"])])
    async def get_student_program_course(self, input: RequestProgramSemester) -> Response[List[ProgramCourseNode]]:

        try:
            result = ProgramCourseService.get_program_courses()
        except Exception as e:
            print(e)
            result = []
        return Response(
            status=True,
            code=ResponseCode.SUCCESS,
            message="Successfully Retrieve Program Courses",
            data=result)

        # for the rest of the process handling exceptions
        try:
            return ProgramCourseService.fetch_student_program_courses(input)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Unable to retrieve student program courses",
                data=[])


@strawberry.type
class ProgramCourseMutation:
    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_PROGRAM_COURSES"])])
    def register_program_course(self, inputs: List[ProgramCourseInput]) -> Response[Optional[ProgramCourseListNode]]:
        """
            register and update program courses
            :param inputs
            :return:Response[ProgramCourseListNode]
        """
        try:
            return ProgramCourseService(ProgramCourse).register_program_courses(inputs)
        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to Change Program Courses",
                            data=ProgramCourseListNode(items=[], total_count=0), )

    # Delete programs type function
    @strawberry.mutation(extensions=[CustomPermissionExtension(["REMOVE_PROGRAM_COURSE"])])
    async def remove_program_course(self, uid: str) -> Response[None]:
        """
        Remove program course By UID
        :param uid:
        :return:
        """
        try:
            ProgramCourseService(ProgramCourse).remove_program_course(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Program Course Removed Successfully",
                data=None
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Course Program Course",
                data=None
            )
