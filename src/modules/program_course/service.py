import json
import time
from datetime import datetime
from typing import List, Optional

import pendulum
import requests
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, desc

from src.core.config import settings
from src.core.moodle_api import MoodleApi
from src.core.redis import get_redis
from src.core.security import Info
from src.db.session import session_scope
from src.helpers.utils import get_user_departments_headship, get_user_unit_department_headship
from src.models import ProgramCourse, Program, AcademicYear, StudentCourseRegistration, Course, ProgramSemester, \
    ExamResultSummary, CourseAllocation
from src.models.exam_course_result_forward_logs import ExamCourseResultForwardLogs
from src.modules import CRUDBase
from src.modules.academic_year.service import AcademicYearService
from src.modules.course.service import CourseService
from src.modules.course_category.service import CourseCategoryService
from src.modules.program_semester.service import ProgramSemesterService
from src.modules.programs.service import ProgramService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramCourseInput, ProgramCourseListNode, ProgramSemesterListNode, ProgramSemesterInput, \
    ProgramCourseNode, InnerStudentProgramSemester, RequestProgramSemester, CourseNode, \
    ProgramCourseWithHeadshipListNode


class ProgramCourseService(CRUDBase[ProgramCourse, ProgramCourseInput, ProgramCourseInput]):
    @staticmethod
    def get_program_courses() -> List[ProgramCourse]:
        with session_scope() as session:
            result = session.query(ProgramCourse).filter(ProgramCourse.deleted_at.is_(None)).order_by(
                desc(ProgramCourse.updated_at)).all()
            return result

    @staticmethod
    def get_program_course_by_uid(uid: str) -> ProgramCourse:
        """
        Get Program Course by uid
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramCourse).where((ProgramCourse.uid == uid) & (ProgramCourse.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.first()

    @staticmethod
    def get_program_course_by_program_semester(program_semester_id: int) -> ProgramCourse:
        with (session_scope() as session):
            print('program_semester_id: ', program_semester_id)
            query = session.query(ProgramCourse).join(Course, ProgramCourse.course_id == Course.id).filter(
                ProgramCourse.program_semester_id == program_semester_id, ProgramCourse.deleted_at.is_(None))
            query = query.order_by(ProgramCourse.course_category_id.asc(), Course.code.asc())
            return query.all()

    @staticmethod
    def get_program_course_by_program_semester_uid(uid: str) -> Response[ProgramCourseListNode]:
        """
        Get Program Course by program semester uid
        :return:
        """
        with session_scope() as session:
            try:
                program_semester = ProgramSemesterService.get_program_semester_by_uid(uid)
                if program_semester is None:
                    raise ValueError("You have submitted incorrect programs semester details")
            except Exception as e:
                print(e)
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    data=ProgramCourseListNode(items=[], total_count=0),
                    message="You have submitted incorrect programs semester details"
                )

            stmt = select(ProgramCourse).where(
                (ProgramCourse.program_semester_id == program_semester.id) & (ProgramCourse.deleted_at.is_(None)))
            result_raw = session.scalars(stmt)
            result = result_raw.all()
            count = session.query(ProgramCourse.id).filter(ProgramCourse.deleted_at.is_(None)).count()
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                data=ProgramCourseListNode(items=result, total_count=count),
                message="Program Course Retrieved Successful"
            )

    @staticmethod
    def get_hod_forward_exam_course_result_status(program_semester_uid, info: Info) -> List[ProgramCourseNode]:
        """
        Get Program Course by program semester uid
        :return:
        """
        with (session_scope() as session):
            user_h_department_uids = get_user_departments_headship(info)
            program_semester = session.query(ProgramSemester).join(Program).filter(
                ProgramSemester.uid == program_semester_uid,
                ProgramSemester.deleted_at.is_(None),
                Program.department_uid.in_(user_h_department_uids),
                Program.deleted_at.is_(None)).one()
            if program_semester is None:
                return []
            courses = session.query(ProgramCourse).filter(
                ProgramCourse.program_semester_id == program_semester.id,
                ProgramCourse.deleted_at.is_(None)).all()

            return courses
            # print(result)

    @staticmethod
    def get_program_course_by_program_semester_uid_with_headship(uid, info: Info) -> Response[List[ProgramCourseWithHeadshipListNode]]:
        with (session_scope() as session):
            try:
                program_semester = ProgramSemesterService.get_program_semester_by_uid(uid)
                if program_semester is None:
                    raise ValueError("You have submitted incorrect programs semester details")
            except Exception as e:
                print(e)
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    data=[],
                    message="You have submitted incorrect programs semester details"
                )

            user_h_department_uids = get_user_departments_headship(info)
            result = (
                session.query(
                    ProgramCourse.uid,
                    Course.name,
                    Course.code
                )
                .join(Course, ProgramCourse.course_id == Course.id)
                .filter(ProgramCourse.program_semester_id == program_semester.id,
                        Course.department_uid.in_(user_h_department_uids), ProgramCourse.deleted_at.is_(None))
                .all()
            )
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                data=result,
                message="Program Course Retrieved Successful"
            )

    @staticmethod
    def get_program_courses_by_uids(uids: List[str]) -> List[ProgramCourse]:
        """
        Get programs course by uids
        :return:
        """
        with session_scope() as session:
            stmt = select(ProgramCourse).where(
                (ProgramCourse.uid.in_(uids)) & (ProgramCourse.deleted_at.is_(None)))
            result = session.scalars(stmt)
            return result.all()

    @staticmethod
    def check_uniqueness(course_id: int, program_semester_id: int) -> ProgramCourse:
        """
        Check if there already exists program course with same course_id, program_semester_id all together
        :return ProgramCourse:
        """
        with session_scope() as session:
            stmt = select(ProgramCourse).where(
                (ProgramCourse.course_id == course_id) &
                (ProgramCourse.program_semester_id == program_semester_id) &
                (ProgramCourse.deleted_at.is_(None))
            )
            result = session.scalars(stmt)
            return result.first()

    def register_program_courses(self, inputs: List[ProgramCourseInput]) -> Response[ProgramCourseListNode]:
        """
        Register programs Course
        :param inputs:
        :return Response[List[ProgramCourseNode]]:
        """
        program_course_list = []
        action_type = "Register"
        with session_scope() as session:
            # check for existing programs courses using uid
            existed_program_course = self.get_program_courses_by_uids([inputItem.uid for inputItem in inputs])
            for inputItem in inputs:
                # Verify and get supplied Program uid. and get existed program model
                program_semester = ProgramSemesterService.get_program_semester_by_uid(
                    inputItem.program_semester_uid)
                if program_semester is None:
                    return Response(
                        status=False,
                        code=ResponseCode.FAILURE,
                        data=ProgramSemesterListNode(items=[], total_count=0),
                        message="You have submitted incorrect programs semester details"
                    )

                # Verify and get supplied Course uid. and get existed Course id from returned Course model
                course = CourseService.get_course_by_uid(inputItem.course_uid)
                if course is None:
                    return Response(
                        status=False,
                        code=ResponseCode.FAILURE,
                        data=ProgramCourseListNode(items=[], total_count=0),
                        message="You have submitted incorrect courses details"
                    )

                # Verify and get supplied Course category uid. and get existed Course category id from returned Course model
                course_category = CourseCategoryService.get_course_category_by_uid(inputItem.course_category_uid)
                if course_category is None:
                    return Response(
                        status=False,
                        code=ResponseCode.FAILURE,
                        data=ProgramSemesterListNode(items=[], total_count=0),
                        message="You have submitted incorrect courses category details"
                    )

                if inputItem.uid is None:
                    # validate if this program semester is not deprecated
                    deprecated_program_course = self.check_uniqueness(course_id=course.id,
                                                                      program_semester_id=program_semester.id)
                    if deprecated_program_course:
                        return Response(
                            status=False,
                            code=ResponseCode.FAILURE,
                            data=ProgramCourseListNode(items=[], total_count=0),
                            message="Program Course Already Exist"
                        )

                    program_course = ProgramCourse(
                        program_semester=program_semester,
                        course=course,
                        credit=inputItem.credit,
                        course_category=course_category,
                        lecture_hours=inputItem.lecture_hours,
                        seminar_hours=inputItem.seminar_hours,
                        practical_hours=inputItem.practical_hours,
                        assignment_hours=inputItem.assignment_hours,
                        independent_study_hours=inputItem.independent_study_hours,
                        pass_hours=inputItem.pass_hours
                    )
                    local_object = session.merge(program_course)
                    session.add(local_object)
                    session.commit()
                    program_course_list.append(local_object)
                else:
                    action_type = "Update"
                    program_course = next(
                        filter(lambda program_course_data: str(program_course_data.uid) == str(inputItem.uid),
                               existed_program_course), None)
                    if program_course:
                        obj_data = jsonable_encoder(inputItem)
                        # # Replace referenced uids field with model required ids field
                        obj_data['program_semester'] = program_semester
                        obj_data['course'] = course
                        obj_data['course_category'] = course_category
                        for key, value in obj_data.items():
                            setattr(program_course, key, value)

                        local_object = session.merge(program_course)
                        session.add(local_object)
                        session.commit()
                        program_course_list.append(local_object)

            count = session.query(ProgramCourse).filter(ProgramCourse.deleted_at.is_(None)).count()
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=ProgramCourseListNode(items=program_course_list, total_count=count),
                            message=f"Successfully to {action_type} Program Course")

    @staticmethod
    async def fetch_student_program_courses(input: RequestProgramSemester) -> Response[List[ProgramCourseNode]]:
        """
        Register programs Course
        :param input:
        :return Response[List[ProgramCourseNode]]:
        """
        program_course_list = []
        with session_scope() as session:
            # Verify and get supplied Program uid and get existed program model
            try:
                program = ProgramService(Program).get(input.program_uid)
                if program is None:
                    raise ValueError("You have submitted incorrect program details")
            except Exception as e:
                print(e)
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    data=[],
                    message="You have submitted incorrect program details"
                )

            # Verify and get supplied Academic year uid and get existed Academic year model
            try:
                academic_year = AcademicYearService(AcademicYear).get(input.academic_year_uid)
                if academic_year is None:
                    raise ValueError("You submitted incorrect academic year details")
            except Exception as e:
                print(e)
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    data=[],
                    message="You submitted incorrect academic year details"
                )

            studentSemester: InnerStudentProgramSemester = InnerStudentProgramSemester()
            studentSemester.semester = input.semester
            studentSemester.program_id = program.id
            studentSemester.academic_year_id = academic_year.id
            studentSemester.study_year = input.study_year

            prog_sem = ProgramSemesterService.get_student_semester(studentSemester)
            if prog_sem is None:
                return Response(
                    status=False,
                    code=ResponseCode.FAILURE,
                    data=[],
                    message="No Program Semester Found For Your Details"
                )

            result = session.query(ProgramCourse, StudentCourseRegistration).outerjoin(StudentCourseRegistration,
                                                                                       ProgramCourse.id == StudentCourseRegistration.program_course).filter(
                ProgramCourse.program_semester_id == prog_sem.id).filter(
                StudentCourseRegistration.registration_number == input.registration_number).all()
            if result:
                return Response(
                    status=True, code=ResponseCode.SUCCESS,
                    data=result, message="student program course retrieve successful"
                )
            else:
                return Response(
                    status=False, code=ResponseCode.FAILURE,
                    data=result, message="No Program Course For this Student"
                )

    # Delete FUnction
    @staticmethod
    def remove_program_course(uid: str):
        """
        Remove Program course by UID
        :param uid:
        :return:
        """
        with session_scope() as session:
            session.query(ProgramCourse).filter_by(uid=uid).update({ProgramCourse.deleted_at: pendulum.now()})
            session.commit()

    @staticmethod
    def hod_forward_exam_course_result(program_course_uids, info) -> Response[None]:
        with session_scope() as session:
            user_h_department_uids = get_user_departments_headship(info)
            program_courses = session.query(ProgramCourse).join(ProgramSemester).join(Program).filter(
                ProgramCourse.uid.in_(program_course_uids),
                ProgramCourse.forward_status.in_([0, 1]),
                ProgramCourse.deleted_at.is_(None),
                ProgramSemester.deleted_at.is_(None),
                Program.department_uid.in_(user_h_department_uids),
                Program.deleted_at.is_(None)).all()
            if not program_courses:
                return Response(
                    status=True,
                    code=ResponseCode.NO_RECORD_FOUND,
                    message="Course Selected is not ready for forwarding",
                    data=None
                )
            forward_logs = []
            total = 0
            staff_uid = str(info.context.user.staff.uid)
            for pc in program_courses:
                status = pc.forward_status + 1
                total += 1
                staff_name = info.context.user.full_name
                if pc.forward_status == 0:
                    staff_name = f"{info.context.user.full_name} (Forced)"
                logs = ExamCourseResultForwardLogs(
                    program_course_id=pc.id,
                    staff_uid=staff_uid,
                    staff_name=staff_name,
                    forwarded_from=pc.forward_status,
                    forwarded_to=status
                )
                forced_forward_staff_uids = []
                if pc.forward_status == 0:
                    staff_allocations = session.query(CourseAllocation.staff_uid) \
                        .filter(CourseAllocation.program_course_id == pc.id,
                                CourseAllocation.deleted_at.is_(None)).all()
                    if staff_allocations:
                        forced_forward_staff_uids = [uid for uid, in staff_allocations]

                        # for allocation in staff_allocations:
                        #     forced_forward_staff_uids.append(str(allocation.staff_uid))

                if forced_forward_staff_uids:

                    # go to uaa to get student information
                    data_obj = {
                        "uids": forced_forward_staff_uids
                    }
                    # Set the Content-Type header to indicate that the request body is JSON
                    headers = {
                        "Content-Type": "application/json"
                    }
                    response = requests.post(settings.UAA_URi + '/get_staffs_by_staff_uids', json=data_obj,
                                             headers=headers, timeout=5)
                    #
                    response.raise_for_status()
                    if response.status_code == 200:
                        response_data = response.json()
                        if response_data:
                            recipient = []
                            for data in response_data:
                                recipient.append(
                                    {
                                        "email": data['email'],
                                        "name": data['full_name']
                                    }
                                )
                            #
                            # recipient = [
                            #     {
                            #         "email": "husseinmkwazu@sua.ac.tz",
                            #         "name": "Hussein Mkwazu"
                            #     },
                            #     {
                            #         "email": "josephat.bakobile@sua.ac.tz",
                            #         "name": "Josephat Bakobile"
                            #     }
                            # ]
                            #
                            # cc_email = {
                            #     "email": "kadefue@sua.ac.tz",
                            #     "name": "Kadeghe Fue"
                            # }
                            cc_email = {
                                "email": info.context.user.email,
                                "name": info.context.user.full_name
                            }

                            recipient.append(cc_email)

                            data_obj = json.dumps({
                                "title": "Force Forward Staff Course Exam Results",
                                "message": f"Dear Instructors, <br/><strong>{info.context.user.full_name}"
                                           f"</strong> has forced "
                                           f"<strong>{pc.course.name} ({pc.course.code})</strong> exam to the HOD, "
                                           f"You can no longer update or change the results. "
                                           f"In case you need to change anything related to this course, please reach out the HOD.",
                                "recipient_emails": recipient,
                                "cc_emails": [cc_email],
                            })


                            headers = {
                                "Content-Type": "application/json"
                            }
                            try:
                                requests.post(settings.UAA_URi + '/send_email', data=data_obj,
                                              headers=headers, timeout=5)
                            except Exception as e:
                                print(e)
                forward_logs.append(logs)
                session.query(ProgramCourse).filter_by(id=pc.id).update({"forward_status": status})
            session.add_all(forward_logs)
            session.commit()
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message=f"{total} Courses Successfully Forwarded",
                data=None
            )

    @staticmethod
    def principal_forward_program_semester_exam_results(program_semester_uids, info) -> Response[None]:
        with session_scope() as session:
            user_unit_department_uids = get_user_unit_department_headship(info)
            program_courses = session.query(ProgramCourse.id, ProgramCourse.forward_status).join(ProgramSemester).join(
                Program).filter(
                ProgramSemester.uid.in_(program_semester_uids),
                ProgramCourse.forward_status == 2,
                ProgramCourse.deleted_at.is_(None),
                ProgramSemester.deleted_at.is_(None),
                Program.department_uid.in_(user_unit_department_uids),
                Program.deleted_at.is_(None)).all()
            if not program_courses:
                return Response(
                    status=True,
                    code=ResponseCode.NO_RECORD_FOUND,
                    message="No Any Examination Is ready for Forwarding from selected Programs",
                    data=None
                )

            forward_logs = []
            total = 0

            staff_uid = str(info.context.user.staff.uid)
            for pc in program_courses:
                status = 3
                total += 1
                logs = ExamCourseResultForwardLogs(
                    program_course_id=pc.id,
                    staff_uid=staff_uid,
                    staff_name=info.context.user.full_name,
                    forwarded_from=pc.forward_status,
                    forwarded_to=status
                )
                forward_logs.append(logs)
                session.query(ProgramCourse).filter_by(id=pc.id).update({"forward_status": status})
                session.query(ExamResultSummary).filter_by(program_course_id=pc.id) \
                    .update({"publish_status": True, "publish_date": datetime.now().date(),
                             "publisher": info.context.user.full_name})
            session.add_all(forward_logs)
            session.commit()
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Program Examination Forwarded Successful",
                data=None
            )

    @staticmethod
    def return_course_result(program_course_uids, info) -> Response[None]:
        with session_scope() as session:
            # Get program Course information
            all_program_courses = 0
            for program_course_uid in program_course_uids:
                program_course = ProgramCourseService.get_program_course_by_uid(program_course_uid)
                if program_course is None:
                    return Response(
                        status=True,
                        code=ResponseCode.NO_RECORD_FOUND,
                        message="Invalid program course selection",
                        data=None
                    )
                if program_course.forward_status == 0:
                    return Response(
                        status=True,
                        code=ResponseCode.NO_RECORD_FOUND,
                        message="Selected Course Exam Result Is in initial Stage, Results Is not forwarded yet",
                        data=None
                    )

                if program_course.forward_status > 3:
                    return Response(
                        status=True,
                        code=ResponseCode.NO_RECORD_FOUND,
                        message="Program Course Result Can not be Edited any more, Results Already Published",
                        data=None
                    )
                # Result must be Return by principal only
                if program_course.forward_status == 2 or program_course.forward_status == 3:
                    user_unit_department_uids = get_user_unit_department_headship(info)
                    if len(user_unit_department_uids) == 0:
                        return Response(
                            status=True,
                            code=ResponseCode.NO_RECORD_FOUND,
                            message="You have no any Unit/Principal Leadership assigned this time",
                            data=None
                        )

                    selected_program_department_uid = program_course.program_semester.program.department_uid
                    if selected_program_department_uid not in user_unit_department_uids:
                        return Response(
                            status=True,
                            code=ResponseCode.NO_RECORD_FOUND,
                            message="You dont have any privilege for returning selected Examination Course Results to HOD",
                            data=None
                        )
                    status = program_course.forward_status - 1
                    logs = ExamCourseResultForwardLogs(
                        program_course_id=program_course.id,
                        staff_uid=info.context.user.staff.uid,
                        staff_name=info.context.user.full_name,
                        forwarded_from=program_course.forward_status,
                        forwarded_to=status
                    )
                    session.query(ProgramCourse).filter_by(id=program_course.id).update({"forward_status": status})
                    if program_course.forward_status == 3:
                        session.query(ExamResultSummary).filter_by(program_course_id=program_course.id) \
                            .update({"publish_status": False})
                    session.add(logs)
                    all_program_courses += 1
                # Result must be Return by HOD only
                elif program_course.forward_status == 1:
                    user_h_department_uids = get_user_departments_headship(info)
                    if len(user_h_department_uids) == 0:
                        return Response(
                            status=False,
                            code=ResponseCode.NO_RECORD_FOUND,
                            message="You have no any HOD Leadership assigned this time",
                            data=None
                        )

                    selected_program_department_uid = program_course.program_semester.program.department_uid
                    if selected_program_department_uid not in user_h_department_uids:
                        return Response(
                            status=True,
                            code=ResponseCode.NO_RECORD_FOUND,
                            message="You dont have any privilege for returning selected Examination Course Results to the Instructor",
                            data=None
                        )
                    status = program_course.forward_status - 1
                    logs = ExamCourseResultForwardLogs(
                        program_course_id=program_course.id,
                        staff_uid=info.context.user.staff.uid,
                        staff_name=info.context.user.full_name,
                        forwarded_from=program_course.forward_status,
                        forwarded_to=status
                    )
                    session.query(ProgramCourse).filter_by(id=program_course.id).update({"forward_status": status})
                    session.add(logs)
                    all_program_courses += 1
                session.commit()
                if all_program_courses > 0:
                    return Response(
                        status=True,
                        code=ResponseCode.SUCCESS,
                        message=f"{all_program_courses} Courses Returned",
                        data=None
                    )
                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Course Selected is not ready for forwarding",
                    data=None
                )

    @staticmethod
    def return_course_result_by_program_semester_uids(program_semester_uids, info) -> Response[None]:
        with session_scope() as session:
            # Get program Course information
            all_program = 0
            for program_semester_uid in program_semester_uids:
                program_semester = ProgramSemesterService.get_program_semester_by_uid(program_semester_uid)
                if program_semester is None:
                    return Response(
                        status=True,
                        code=ResponseCode.NO_RECORD_FOUND,
                        message="Invalid program semester  selection",
                        data=None
                    )

                program_courses = session.query(ProgramCourse).filter(
                    ProgramCourse.program_semester_id == program_semester.id,
                    ProgramCourse.deleted_at.is_(None)).all()

                all_program_courses = 0
                if program_courses is None:
                    return Response(
                        status=True,
                        code=ResponseCode.NO_RECORD_FOUND,
                        message="Invalid program course selection",
                        data=None
                    )
                for program_course in program_courses:
                    # Result must be Return by principal only
                    if program_course.forward_status == 2 or program_course.forward_status == 3:
                        user_unit_department_uids = get_user_unit_department_headship(info)
                        if len(user_unit_department_uids) == 0:
                            return Response(
                                status=True,
                                code=ResponseCode.NO_RECORD_FOUND,
                                message="You have no any Unit/Principal Leadership assigned this time",
                                data=None
                            )

                        selected_program_department_uid = program_course.program_semester.program.department_uid
                        if selected_program_department_uid not in user_unit_department_uids:
                            return Response(
                                status=True,
                                code=ResponseCode.NO_RECORD_FOUND,
                                message="You dont have any privilege for returning selected Examination Course Results to HOD",
                                data=None
                            )
                        status = program_course.forward_status - 1
                        logs = ExamCourseResultForwardLogs(
                            program_course_id=program_course.id,
                            staff_uid=info.context.user.staff.uid,
                            staff_name=info.context.user.full_name,
                            forwarded_from=program_course.forward_status,
                            forwarded_to=status
                        )
                        session.query(ProgramCourse).filter_by(id=program_course.id).update({"forward_status": status})
                        if program_course.forward_status == 3:
                            session.query(ExamResultSummary).filter_by(program_course_id=program_course.id) \
                                .update({"publish_status": False})
                        session.add(logs)
                        all_program_courses += 1
                    if all_program_courses > 0:
                        all_program += 1

                session.commit()
                if all_program > 0:
                    return Response(
                        status=True,
                        code=ResponseCode.SUCCESS,
                        message=f"{all_program} Program Examination Results Returned",
                        data=None
                    )
                return Response(
                    status=True,
                    code=ResponseCode.SUCCESS,
                    message="Program Selected is not ready for return forwarding Examination Results",
                    data=None
                )

    @staticmethod
    def get_unregister_moodle_program_course_by_course_id(course_id: int) -> ProgramCourseNode:
        """
        Get Program Course with null moodle id that belong to course with passed course id
        :return ProgramCourseNode:
        """
        with session_scope() as session:
            stmt = select(ProgramCourse).where(
                (ProgramCourse.course_id == course_id) &
                (ProgramCourse.moodle_id.is_(None)) &
                (ProgramCourse.deleted_at.is_(None))
            )
            result = session.scalars(stmt)
            return result.first()


ProgramCourseCrud = ProgramCourseService(ProgramCourse)
