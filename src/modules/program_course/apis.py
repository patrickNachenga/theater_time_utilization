from typing import List, Optional

import strawberry

from src.core.security import CustomPermissionExtension, Info
from src.models import ProgramCourse
from src.modules.program_course.service import ProgramCourseService, ProgramCourseCrud
from src.modules.program_semester.service import ProgramSemesterService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import PaginationInput, ProgramCourseListNode, ProgramCourseInput, ProgramCourseNode, \
    RequestProgramSemester, CourseNode, ProgramCourseWithHeadshipListNode, InstructorSemesterCourseAllocationInputNode


@strawberry.type
class ProgramCourseQuery:
    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_PROGRAM_COURSES"])])
    def get_program_courses(self, pagination: PaginationInput, program_semester: Optional[str] = None) -> (
            Response)[ProgramCourseListNode]:
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

    @strawberry.field()  # extensions=[CustomPermissionExtension(["VIEW_PROGRAM_COURSES"])]
    def get_program_course(self, uid: str) -> Response[ProgramCourseNode]:
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

    @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_PROGRAM_COURSES_BY_SEMESTER"])])
    def get_program_course_by_program_semester_uid(self, program_semester_uid: str) -> Response[ProgramCourseListNode]:
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
    def get_hod_forward_exam_course_result_status_by_program_semester_uid(self, program_semester_uid: str,
                                                                          info: Info) -> Response[List[ProgramCourseNode]]:
        try:
            if info.context.user is None:
                return Response(
                    status=False,
                    code=ResponseCode.UNAUTHORIZED,
                    message="Your session has expired please reset your session",
                    data=[])

            result = ProgramCourseService.get_hod_forward_exam_course_result_status(program_semester_uid, info)
            if result:
                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Successfully Retrieve Courses",
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

    # @strawberry.field(extensions=[CustomPermissionExtension(["VIEW_PROGRAM_COURSES_BY_SEMESTER"])])
    @strawberry.field()
    async def get_program_course_by_program_semester_uid_with_headship(self, program_semester_uid: str, info: Info) -> \
            Response[List[ProgramCourseWithHeadshipListNode]]:
        try:
            program_courses = ProgramCourseService.get_program_course_by_program_semester_uid_with_headship(
                program_semester_uid, info)
            if program_courses:
                return program_courses
            raise ValueError("Unable to retrieve program courses")
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                data=[],
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
    @strawberry.mutation()
    def forward_course_result_by_hod(self, program_course_uids: List[str], info: Info) -> Response[None]:
        try:
            if info.context.user is None:
                return Response(
                    status=False,
                    code=ResponseCode.UNAUTHORIZED,
                    message="Your session has expired please reset your session",
                    data=None)
            return ProgramCourseService.hod_forward_exam_course_result(program_course_uids, info)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Forward Course Results to Principal",
                data=None
            )

    @strawberry.mutation(extensions=[CustomPermissionExtension(["PRINCIPAL_FORWARD_PROGRAM_SEMESTER_EXAM_RESULTS"])])
    def forward_course_result_by_principal(self, program_semester_uids: List[str], info: Info) -> Response[None]:
        try:
            if info.context.user is None:
                return Response(
                    status=False,
                    code=ResponseCode.UNAUTHORIZED,
                    message="Your session has expired please reset your session",
                    data=None)
            return ProgramCourseService.principal_forward_program_semester_exam_results(program_semester_uids, info)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Forward Course Results to Principal",
                data=None
            )

    @strawberry.mutation(extensions=[CustomPermissionExtension(["RETURN_EXAM_COURSE_RESULTS"])])
    def return_course_exam_result(self, program_course_uids: List[str], info: Info) -> Response[None]:
        try:
            if info.context.user is None:
                return Response(
                    status=False,
                    code=ResponseCode.UNAUTHORIZED,
                    message="Your session has expired please reset your session",
                    data=None)
            return ProgramCourseService.return_course_result(program_course_uids, info)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Return Exam Course Results",
                data=None
            )

    @strawberry.mutation(extensions=[CustomPermissionExtension(["RETURN_EXAM_COURSE_RESULTS"])])
    def return_course_exam_result_by_program_semester_uids(self, program_semester_uids: List[str], info: Info) -> Response[None]:
        try:
            if info.context.user is None:
                return Response(
                    status=False,
                    code=ResponseCode.UNAUTHORIZED,
                    message="Your session has expired please reset your session",
                    data=None)
            return ProgramCourseService.return_course_result(program_course_uids, info)
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Return Exam Course Results",
                data=None
            )

    @strawberry.field(extensions=[CustomPermissionExtension(["REGISTER_PROGRAM_COURSES"])])
    def register_program_course(self, inputs: List[ProgramCourseInput]) -> Response[ProgramCourseListNode]:
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
